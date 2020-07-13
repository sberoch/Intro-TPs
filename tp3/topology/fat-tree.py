"""
Este archivo ejemplifica la creacion de una topologia de mininet
En este caso estamos creando una topologia muy simple con la siguiente forma

   host --- switch --- switch --- host
"""

from mininet.topo import Topo

class FatTree( Topo ):
  def __init__( self, half_ports = 2, **opts ):
    Topo.__init__(self, **opts)
    
    sw00 = self.create_root()

    switches = self.create_switches([[sw00]], opts['levels'])
    
    self.add_last_level_hosts(switches)


  def create_root(self):
    sw00 = self.addSwitch('sw00')

    h1 = self.addHost('h1')
    h2 = self.addHost('h2')
    h3 = self.addHost('h3')

    self.addLink(sw00, h1)
    self.addLink(sw00, h2)
    self.addLink(sw00, h3)

    return sw00


  def create_switches(self, switches, levels):
    for i in range(1, levels):
      switches_nivel = []
      for j in range(2**i):
        switches_nivel.append(self.addSwitch('sw'+str(i)+str(j)))
      switches.append(switches_nivel)

    for i in range(len(switches)-1):
      for j in range(len(switches[i])):
        nivel_siguiente = switches[i+1]
        for sw in nivel_siguiente:
          self.addLink(switches[i][j], sw)
    return switches


  def add_last_level_hosts(self, switches):
    host_number = 4
    for sw in switches[-1]:
      self.addHost('h'+str(host_number))
      self.addLink(sw,'h'+str(host_number))
      host_number+=1


topos = { 'fat-tree': FatTree }
