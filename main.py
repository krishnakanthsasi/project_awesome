# -*- coding: utf-8 -*-
""" ===========================================================================

This script is where we adjust parameters and run the model

=========================================================================== """

import generate_network as gn
import dynamics_network as dn
import networkx as nx
import matplotlib.pyplot as plt

def print_stuff():
    print('\n\n\n')
    for node in network.nodes_iter(data=True):
        print(node)
    print()
    for edge in network.edges_iter(data=True):
        print(edge)

# Build a network corresponding to regular grid with d dimensions of size L, 
# with liquidity threshold -4 and solvency threshold -6
network = gn.regular_network(L = 100, d = 2, Tl = -2, Ts = -4)

# Run the simulation for 1 iteration
avalanche_sizes = dn.run_simulation(network, 100)

print(avalanche_sizes)

# Draw the graph. NOTE: networkx has some basic drawing functionality but it
# takes too long for me to draw 100x100
#nx.draw(G)
#plt.show()


