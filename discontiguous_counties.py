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

def check_contiguity(graph, ):
    pass