from pox.core import core
import pox.openflow.discovery

from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt

import networkx as nx

import pox.openflow.libopenflow_01 as of


class Tp3Controller:
	def __init__(self):
		self.graph = nx.Graph()
		self.output_ports = {}
		self.flows_to_paths = {}
		self.round_robin_counter = 0
		self.hosts_links = {}
		core.call_when_ready(self.start, ('openflow', 'openflow_discovery'))

	def start(self):
		core.openflow.addListeners(self)
		core.openflow_discovery.addListeners(self)
		print('Started!')

	def _handle_ConnectionUp(self, event):
		for link, port in self.hosts_links.items():
			if event.connection.dpid in link:
				self.graph.add_edge(link[0], link[1])
				self.output_ports[link] = port

	def _handle_ConnectionDown(self, event):
		self.save_links_with_hosts(event.connection.dpid)
		self.graph.remove_node(event.connection.dpid)
		self.delete_links_to_deleted_switch(event.connection.dpid)
		self.delete_paths_with_deleted_switch(event.connection.dpid)

	def save_links_with_hosts(self, deleted_id):
		for link in self.graph.edges(deleted_id):
			if not isinstance(link[0], int) or not isinstance(link[1], int):
				self.hosts_links[link] = self.output_ports[link]

	def delete_links_to_deleted_switch(self, deleted_id):
		msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
		for connection in core.openflow.connections: 
			if (connection.dpid,deleted_id) in self.output_ports:
				print("Borrando links del switch con ID: {}".format(connection.dpid))
				connection.send(msg)

		self.output_ports = {l: p for l, p in self.output_ports.items() if deleted_id not in l}

	def delete_paths_with_deleted_switch(self, deleted_id):
		self.flows_to_paths = {f: p for f, p in self.flows_to_paths.items() if deleted_id not in p}

	def _handle_LinkEvent(self, event):
		self.graph.add_edge(event.link.dpid1, event.link.dpid2)
		self.output_ports[(event.link.dpid1, event.link.dpid2)] = event.link.port1


	def _handle_PacketIn(self, event):
		source = str(event.parsed.src)
		dest = str(event.parsed.dst)

		if source not in self.graph:
			self.graph.add_edge(source, event.connection.dpid)
			self.output_ports[(event.connection.dpid, source)] = event.port

		if dest not in self.graph:
			#Es un ping de discovery probablemente, drop
			return

		print(nx.to_dict_of_lists(self.graph))

		ipv4 = event.parsed.find('ipv4')
		#TODO: que el flow tenga mas cosas
		flow = (ipv4.srcip, ipv4.dstip)

		if flow in self.flows_to_paths:
			path = self.flows_to_paths[flow]
			print("Match in flow table! ", path)
			sw_index = path.index(event.connection.dpid)
			print("I'm in Switch ", path[sw_index])
			next_hop = path[sw_index+1]

		else:
			paths = [p for p in nx.all_shortest_paths(self.graph, source=event.connection.dpid, target=dest)]
			print("Paths: ", paths)

			index = self.round_robin_counter % len(paths)
			path = paths[index]
			self.round_robin_counter += 1

			print("Calculated shortest path:", path)
			next_hop = path[1]
			self.flows_to_paths[flow] = path

		msg = of.ofp_flow_mod()
		msg.data = event.ofp
		msg.match.nw_dst = ipv4.dstip
		msg.match.dl_type = 0x800
		#msg.match.tp_dst = 
		msg.actions.append(of.ofp_action_output(port = self.output_ports[(event.connection.dpid, next_hop)]))
		event.connection.send(msg)


def launch():
	pox.openflow.discovery.launch()
	core.registerNew(Tp3Controller)