#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from graphviz import Digraph
import os

def visualize_network(net):
    try:
        dot = Digraph(comment='Network Topology')
        dot.attr(rankdir='TB')
        
        # Define styles for each group
        dot.attr('node', shape='rectangle', style='filled')
        
        # Create subgraphs for each slice
        with dot.subgraph(name='cluster_0') as slice1:
            slice1.attr(label='Slice 1', color='green', style='filled')
            slice1.node('h1', 'H1', shape='box', fillcolor='white')
            slice1.node('h2', 'H2', shape='box', fillcolor='white')
            slice1.node('h5', 'H5', shape='box', fillcolor='white')
            slice1.node('h6', 'H6', shape='box', fillcolor='white')
            slice1.node('s1', 'S1', fillcolor='blue')
        
        with dot.subgraph(name='cluster_1') as slice2:
            slice2.attr(label='Slice 2', color='pink', style='filled')
            slice2.node('h3', 'H3', shape='box', fillcolor='white')
            slice2.node('h4', 'H4', shape='box', fillcolor='white')
            slice2.node('h7', 'H7', shape='box', fillcolor='white')
            slice2.node('h8', 'H8', shape='box', fillcolor='white')
            slice2.node('s2', 'S2', fillcolor='blue')
        
        with dot.subgraph(name='cluster_2') as connecting:
            connecting.attr(label='Connecting Slice', color='lightyellow', style='filled')
            connecting.node('s9', 'S9', fillcolor='blue')
            connecting.node('srv1', 'SRV1', shape='box', fillcolor='white')
            connecting.node('srv2', 'SRV2', shape='box', fillcolor='white')
        
        # Add links
        dot.edge('h1', 's1')
        dot.edge('h2', 's1')
        dot.edge('h5', 's1')
        dot.edge('h6', 's1')
        dot.edge('h3', 's2')
        dot.edge('h4', 's2')
        dot.edge('h7', 's2')
        dot.edge('h8', 's2')
        dot.edge('s1', 's9')
        dot.edge('s2', 's9')
        dot.edge('s9', 'srv1')
        dot.edge('s9', 'srv2')
        
        # Save the graph
        dot.render('network_topology', format='png', cleanup=True)
        info('* Topology visualization saved as network_topology.png\n')
    except Exception as e:
        info('Error visualizing network: {}\n'.format(e))

def createNetwork():
    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/8')

    # Add the controllers
    info('* Adding controllers\n')
    c0 = net.addController(name='c0',
                          controller=Controller,
                          ip='127.0.0.1',
                          protocol='tcp',
                          port=6633)
    c1 = net.addController(name='c1',
                          controller=Controller,
                          ip='127.0.0.1',
                          protocol='tcp',
                          port=6634)
    c2 = net.addController(name='c2',
                          controller=Controller,
                          ip='127.0.0.1',
                          protocol='tcp',
                          port=6635)

    # Create switches
    info('* Adding switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s9 = net.addSwitch('s9', cls=OVSKernelSwitch)

    # Create hosts
    info('* Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    h6 = net.addHost('h6', ip='10.0.0.6')
    h7 = net.addHost('h7', ip='10.0.0.7')
    h8 = net.addHost('h8', ip='10.0.0.8')
    srv1 = net.addHost('srv1', ip='10.0.0.9')
    srv2 = net.addHost('srv2', ip='10.0.0.10')

    # Add links
    info('* Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h5, s1)
    net.addLink(h6, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(h7, s2)
    net.addLink(h8, s2)
    net.addLink(s1, s9)
    net.addLink(s2, s9)
    net.addLink(s9, srv1)
    net.addLink(s9, srv2)

    # Visualize the topology
    visualize_network(net)

    # Start the network
    info('* Starting network\n')
    net.build()
    c0.start()
    c1.start()
    c2.start()
    
    for switch in [s1, s2, s9]:
        switch.start([c0, c1, c2])

    info('* Network started\n')
    
    # Configure the switches for forwarding
    info('* Setting up forwarding rules\n')
    
    # Slice 1 forwarding
    s1.cmd('ovs-ofctl add-flow s1 "in_port=1,actions=output:2,3,4"')  # H1 -> H2, H5, H6
    s1.cmd('ovs-ofctl add-flow s1 "in_port=2,actions=output:1,3,4"')  # H2 -> H1, H5, H6
    s1.cmd('ovs-ofctl add-flow s1 "in_port=3,actions=output:1,2,4"')  # H5 -> H1, H2, H6
    s1.cmd('ovs-ofctl add-flow s1 "in_port=4,actions=output:1,2,3"')  # H6 -> H1, H2, H5
    
    # Slice 2 forwarding
    s2.cmd('ovs-ofctl add-flow s2 "in_port=3,actions=output:4,7,8"')  
    s2.cmd('ovs-ofctl add-flow s2 "in_port=4,actions=output:3,7,8"')  # H4 -> H3, H7, H8
    s2.cmd('ovs-ofctl add-flow s2 "in_port=7,actions=output:3,4,8"')  # H7 -> H3, H4, H8
    s2.cmd('ovs-ofctl add-flow s2 "in_port=8,actions=output:3,4,7"')  # H8 -> H3, H4, H7
    # Connecting Slice forwarding and filtering
    s9.cmd('ovs-ofctl add-flow s9 "in_port=1,priority=10,actions=output:5,6"')  # S1 -> SRV1, SRV2 (non-UDP)
    s9.cmd('ovs-ofctl add-flow s9 "in_port=1,priority=5,ip,udp,actions=output:5"')  # S1 -> SRV1 (UDP)
    s9.cmd('ovs-ofctl add-flow s9 "in_port=2,priority=10,actions=output:5,6"')  # S2 -> SRV1, SRV2 (non-UDP)
    s9.cmd('ovs-ofctl add-flow s9 "in_port=2,priority=5,ip,udp,actions=output:6"')  # S2 -> SRV2 (UDP)
    s9.cmd('ovs-ofctl add-flow s9 "in_port=5,actions=NORMAL"')  # SRV1 -> Allow returning traffic
    s9.cmd('ovs-ofctl add-flow s9 "in_port=6,actions=NORMAL"')  # SRV2 -> Allow returning traffic

    # Start CLI
    CLI(net)
    
    # Stop the network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createNetwork()
