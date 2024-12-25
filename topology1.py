#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from graphviz import Digraph

def visualize_network(net):
    dot = Digraph(comment='Network Topology with Isolated Slices')
    dot.attr(rankdir='LR')
    
    # Define styles for each group
    dot.attr('node', shape='rectangle', style='filled')
    
    # Create subgraphs for each site and slice
    with dot.subgraph(name='cluster_0') as site_a:
        site_a.attr(label='Site A', color='lightgrey', style='filled')
        site_a.node('h1', 'H1\n10.0.0.1', fillcolor='white')
        site_a.node('h2', 'H2\n10.0.0.2', fillcolor='white')
        site_a.node('s1', 'S1', fillcolor='lightblue')

    with dot.subgraph(name='cluster_1') as site_b:
        site_b.attr(label='Site B', color='lightgrey', style='filled')
        site_b.node('h3', 'H3\n10.0.0.3', fillcolor='white')
        site_b.node('h4', 'H4\n10.0.0.4', fillcolor='white')
        site_b.node('s4', 'S4', fillcolor='lightblue')
    
    # Add central switches
    dot.node('s2', 'S2', fillcolor='lightgrey')
    dot.node('s3', 'S3', fillcolor='mediumorchild')
    
    # Add links with bandwidth
    dot.edge('h1', 's1')
    dot.edge('h2', 's1')
    dot.edge('s1', 's2', label='1 Mb/s')
    dot.edge('s2', 's4', label='1 Mb/s')
    dot.edge('s4', 'h3')
    dot.edge('s4', 'h4')
    dot.edge('s1', 's3', label='10 Mb/s')
    dot.edge('s3', 's4', label='10 Mb/s')
    
    # Save the graph
    dot.render('network_topology', format='png', cleanup=True)
    info('*** Topology visualization saved as network_topology.png\n')

def createNetwork():
    "Create the network with isolated slices"
    
    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/8',
                  link=TCLink,  # Enable TCLink for QoS
                  controller=Controller)  # Use the default local controller

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/8')
    h2 = net.addHost('h2', ip='10.0.0.2/8')
    h3 = net.addHost('h3', ip='10.0.0.3/8')
    h4 = net.addHost('h4', ip='10.0.0.4/8')

    info('*** Adding links\n')
    # Upper slice (1 Mb/s)
    net.addLink(h1, s1, port1=1, port2=3, bw=1)
    net.addLink(s1, s2, port1=1, port2=1, bw=1)
    net.addLink(s2, s4, port1=2, port2=1, bw=1)
    net.addLink(h3, s4, port1=1, port2=3, bw=1)

    # Lower slice (10 Mb/s)
    net.addLink(h2, s1, port1=1, port2=4, bw=10)
    net.addLink(s1, s3, port1=2, port2=1, bw=10)
    net.addLink(s3, s4, port1=2, port2=2, bw=10)
    net.addLink(h4, s4, port1=1, port2=4, bw=10)

    # Generate visualization
    visualize_network(net)

    info('*** Starting network\n')
    net.build()
    net.start()

    # Configure the switches for basic forwarding
    info('*** Setting up forwarding rules\n')
    
    # Upper slice (h1 <-> h3)
    s1.cmd('ovs-ofctl add-flow s1 "in_port=3,actions=output:1"')  # h1 -> s1
    s1.cmd('ovs-ofctl add-flow s1 "in_port=1,actions=output:3"')  # s1 -> h1

    s2.cmd('ovs-ofctl add-flow s2 "in_port=1,actions=output:2"')  # s1 -> s4
    s2.cmd('ovs-ofctl add-flow s2 "in_port=2,actions=output:1"')  # s4 -> s1

    s4.cmd('ovs-ofctl add-flow s4 "in_port=1,actions=output:3"')  # s2 -> h3
    s4.cmd('ovs-ofctl add-flow s4 "in_port=3,actions=output:1"')  # h3 -> s2

    # Lower slice (h2 <-> h4)
    s1.cmd('ovs-ofctl add-flow s1 "in_port=4,actions=output:2"')  # h2 -> s1
    s1.cmd('ovs-ofctl add-flow s1 "in_port=2,actions=output:4"')  # s1 -> h2

    s3.cmd('ovs-ofctl add-flow s3 "in_port=1,actions=output:2"')  # s1 -> s4
    s3.cmd('ovs-ofctl add-flow s3 "in_port=2,actions=output:1"')  # s4 -> s1

    s4.cmd('ovs-ofctl add-flow s4 "in_port=2,actions=output:4"')  # s3 -> h4
    s4.cmd('ovs-ofctl add-flow s4 "in_port=4,actions=output:2"')  # h4 -> s3

    info('*** Network started\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createNetwork()

