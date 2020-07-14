from pox.core import core
import pox.openflow.discovery


class Tp3Controller:
	def __init__(self):
		self.connections = set()
		self.switches = []
		core.call_when_ready(self.start, ('openflow', 'openflow_discovery'))

	def start(self):
		core.openflow.addListeners(self)
		core.openflow_discovery.addListeners(self)
		print('\n\nStarted!')

	def _handle_ConnectionUp(self, event):
		if (event.connection not in self.connections):
			self.connections.add(event.connection)
			print('---New switch up!')

	def _handle_ConnectionDown(self, event):
		print('---Switch down!')

	def _handle_LinkEvent(self, event):
		print('---Link found!')

	def _handle_PacketIn(self, event):
		print('--Packet came in!')


def launch():
	pox.openflow.discovery.launch()
	core.registerNew(Tp3Controller)