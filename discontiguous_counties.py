#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
discontiguous_counties.py

Created by Charlie Murphy
24 September 2021

This file adds a single edge so that all counties in PA are contiguous. The same
approach can be used to correct counties in other states if necessary
'''

from networkx import number_connected_components
from reusable_data import get_subgraph

# find_node_by_geoid
# Return the node in the graph with the given GEOID
def find_node_by_geoid(graph, geoid_col, geoid):
    for node in graph:
        if graph.nodes[node][geoid_col] == geoid:
            return node

# correct PA
# Add a single edge to the VTD graph for PA to connect the discontiguous 
# precinct in Chester county.
def correct_PA(graph, geoid_col, assignment_col):
    node1 = find_node_by_geoid(graph, geoid_col, '42029000036')
    node2 = find_node_by_geoid(graph, geoid_col, '42029000905')
    graph.add_edge(node1, node2)
    
    return graph

def check_contiguity(graph, data_layer, data_col):

    # Get list of every possible item in the data_layer
    data_list = list(data_layer[data_col])

    # Find the subgraphs of the each item in the graph and check whether or not 
    # they are connected
    connected_components = []
    for item in data_list:
        subgraph = get_subgraph(graph, data_col, item)
        connected_components.append(number_connected_components(subgraph))

    print(connected_components)

