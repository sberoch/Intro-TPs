from pox.core import core
import pox.openflow.discovery

from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt

import networkx as nx

class Tp3Controller:
	def __init__(self):
		self.connections = set()
		self.switches = []
		self.graph = nx.Graph()
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
		print(nx.to_dict_of_lists(self.graph))


	def _handle_PacketIn(self, event):
		print('--Packet came in:', event.port) #, event.parsed.ipv4.srcip)

		print([p for p in nx.all_shortest_paths(self.graph, source=1, target=4)])


def launch():
	pox.openflow.discovery.launch()
	core.registerNew(Tp3Controller)