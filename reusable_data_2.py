#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
resuable_data_2.py

Created by Charlie Murphy
17 October 2021

This file caclulates specific metrics that are used by the algorithm and are the
same between runs so that by calculating them once the algorithm can run more 
efficiently
'''

# ideal_population
# Calculate the total population of the partition and divide it by the number 
# of districts
def get_ideal_population(partition, district_num):
    return int(sum(list(partition["population"].values())) / district_num)

# starting_node
# Convert the starting county FIPS number to the node in the partition
def get_starting_node(graph, col, start):
    for i in range(len(graph.nodes())):
        if graph.nodes()[i][col] == start:
            return i

# get_subgraph
# Return the collection of nodes within an outer_node.
def get_subgraph(graph, col, benchmark):

    nodes = set()
    for node in graph.nodes:
        if graph.nodes[node][col] == benchmark:
            nodes.add(node)
    
    return nodes

# get_county_subgraphs
# Returns a dictionary mapping counties to their sugbraphs of nodes in the given
# partition
def get_county_subgraphs(outer_graph, inner_graph, col):
    subgraphs = dict()

    # Loop through every county
    for node in outer_graph.nodes:
        benchmark = outer_graph.nodes()[node][col]
        subgraphs[node] = get_subgraph(inner_graph, col, benchmark)

    return subgraphs