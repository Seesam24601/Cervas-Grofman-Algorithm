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

# check_contigutity
# Prints a warning if the given graph is discontiguous with respect to the given
# data layer and list the discontiguous ids.
def check_contiguity(graph, data_layer, data_col, name_col):

    # Get list of every possible item and its name in the data_layer
    data_list = list(data_layer[data_col])
    name_list = list(data_layer[name_col])

    # Find the subgraphs of the each item in the graph and check whether or not 
    # they are connected
    connected_components = []
    for item in data_list:
        subgraph = graph.subgraph(get_subgraph(graph, data_col, item))
        connected_components.append(number_connected_components(subgraph))

    # Print warning if necessary
    if max(connected_components) != 1:
        print("WARNING: A graph is discontiguous for a data layer")

        # Print a list of the discontiguous items
        print("The following IDs are discontiguous: ")
        for i in range(len(connected_components)):
            if connected_components[i] != 1:
                print(name_list[i])
        print()

# muni_over_county
# 
def muni_over_county(graph, muni_col, name_col):
    muni_used = dict()
    muni_dupl = set()

    # Loop through all of the municipalities and if the same municipality is
    # found a second time make note.
    for i in range(len(graph.nodes())):
        muni_id = graph.nodes()[i][muni_col]
        if muni_id in muni_used:
            muni_dupl.add(muni_id)
        else:
            muni_used[muni_id] = i

    # Print warning if necesary
    if len(muni_dupl) != 0:
        print("WARNING: A municipality has separate nodes in two counties with the same id")

        # Print the offending municipalities
        for node in muni_dupl:
            print(graph.nodes()[muni_used[node]][name_col])
        print()