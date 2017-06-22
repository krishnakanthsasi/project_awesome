# -*- coding: utf-8 -*-
""" ===========================================================================

This script is where we adjust parameters and run the model

=========================================================================== """

import generate_network as gn
import dynamics_network as dn
import analyze_network as an
import networkx as nx
import time

#NOTE: The print_stuff funtion got moved to the analyze_network file.

# Build a network corresponding to regular grid with d dimensions of size L, 
# with liquidity threshold -4 and solvency threshold -6
network = gn.regular_network(L = 3,  d = 2, Tl = -4, Ts = -6)

node1 = network.nodes()[0]
node2 = network.nodes()[1]
node3 = network.nodes()[2]

node1.setCapital(3)
node1.setLiquidity(4)

node2.setLiquidity(-3)
node3.setLiquidity(-2)

for node in network.nodes()[:3]:
    print(node)

dn._invest_surplus_liquidity(network)

print("\n")
for node in network.nodes()[:3]:
    print(node)


# Plot the distribution of avalanches
#print(avalanche_sizes)
#an.histogram_avalanches(avalanche_sizes, num_bins = 20, y_scale='symlog', x_scale='symlog')

# Plot the graph in a circle. NOTE: This only works on small graphs.
# an.plot_network(network)



