#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
partition_functions.py

Created by Charlie Murphy
25 October 2021

This file is used to hold functions shared between partition_counties.py and
partition_municipalities.py to increase the modularity of both programs.
'''

from networkx import number_connected_components

# check_contiguous
# Return whether or not the unallocated nodes are contiguous within the given 
# partition
def check_contiguous(partition):
    return check_contiguous_district(partition, 1)

# check_contiguous_district
# Return whether or not the nodes allocated to the given district are contiguous 
# within the given partition
def check_contiguous_district(partition, district):
    for part, subgraph in partition.subgraphs.items():
        if (part == district and 
            number_connected_components(subgraph) != 1): 
            return False
    return True

# check_subgrapj
# If not at the county level, return whether or not the unallocated nodes are 
# contiguous within the given partition
def check_subgraph(subgraph_partition, level):
    if level != 0:
        return check_contiguous(subgraph_partition)
    return True

# get_pieces
# Find the current number of pieces actually in the graph
def get_pieces(partition):
    current_pieces = 0
    for part, subgraph in partition.subgraphs.items():
        current_pieces += number_connected_components(subgraph)
    return current_pieces

# check_population
# Return true if the population is within epsilon of the ideal population
def check_population(population, ideal_population, population_deviation):
    return abs(population - ideal_population) <= population_deviation

# safe_add
# Add (key, entry) pair to dictionary where the entry is added to the existing 
# entry if the key already exists
def safe_add(dictionary, key, entry):
    if key in dictionary:
        dictionary[key] += entry
    else:
        dictionary[key] = entry

# Check whether the node allocated is adjacent to a node that was split and thus
# would require additional contiguity checks
def check_split_nodes(partitions, level, split_nodes, node, district):
    if level!=2 and node in split_nodes[level]:
        print("HYPE for TYPEs")
        return check_contiguous_district(partitions[2], district)
    return True

# After splitting a node, get a list of all of the adjacent nodes
def get_split_nodes(partitions, level, split_nodes, node):
    for edge in partitions[level]["cut_edges"]:
        for i in range(0,2):
            if edge[i] == node:
                split_nodes[level].add(edge[i-1])
    return split_nodes