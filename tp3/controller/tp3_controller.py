from pox.core import core
import pox.openflow.discovery

from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt

import networkx as nx

import pox.openflow.libopenflow_01 as of


class Tp3Controller:
	def __init__(self):
		self.connections = set()
		self.switches = []
		self.graph = nx.Graph()
		self.hosts = set()
		self.output_ports = {}
		core.call_when_ready(self.start, ('openflow', 'openflow_discovery'))

	def start(self):
		core.openflow.addListeners(self)
		core.openflow_discovery.addListeners(self)
		print('\n\nStarted!')

	def _handle_ConnectionUp(self, event):
		if (event.connection not in self.connections):
			self.connections.add(event.connection)
			print('---New switch up:', dpid_to_str(event.dpid))
			#print('---Metadata: ', str(event.connection.ports), str(event.connection.features))

	def _handle_ConnectionDown(self, event):
		print('---Switch down!')

	def _handle_LinkEvent(self, event):
		print('---Link found!')
		self.graph.add_edge(event.link.dpid1, event.link.dpid2)
		
		self.output_ports[(event.link.dpid1, event.link.dpid2)] = event.link.port1
		print(self.output_ports)


	def _handle_PacketIn(self, event):
		print('--Packet came in:', event.port) #, event.parsed.ipv4.srcip)

		#print([p for p in nx.all_shortest_paths(self.graph, source=1, target=4)])
		ipv4 = event.parsed.find('ipv4')
		
		if ipv4 is None:
			return

		srcip = str(ipv4.srcip)
		dstip = str(ipv4.dstip)

		if srcip not in self.hosts:
			self.hosts.add(srcip)
			self.graph.add_edge(srcip, event.connection.dpid)
			self.output_ports[(event.connection.dpid, srcip)] = event.port

		if dstip not in self.graph:
			return

		current_path = nx.all_shortest_paths(self.graph, source=event.connection.dpid, target=dstip).next()
		print("PATH:", current_path)
		print("hosts:", self.hosts)
		next_hop = current_path[1]

		msg = of.ofp_flow_mod()
		msg.match.nw_dst = ipv4.dstip
		msg.match.dl_type=0x800
		#msg.match.tp_dst = 
		msg.actions.append(of.ofp_action_output(port = self.output_ports[(event.connection.dpid, next_hop)]))
		event.connection.send(msg)

		#return generate_ft(self.paths, dpid) 


def launch():
	pox.openflow.discovery.launch()
	core.registerNew(Tp3Controller)