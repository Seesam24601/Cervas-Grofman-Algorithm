#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
make_partition.py

Created by Charlie Murphy
17 December 2021

This file creates a partition with the appropriate number of districts, given a
graph
'''

from gerrychain import GeographicPartition, updaters

# make_partition
# Create a partition with the appropriate number of districts, given a graph
def make_partition(graph, district_num, assignment_col, my_updaters):

    # Add a node to every district
    i = 1
    flipped_nodes = []
    for node in graph.nodes():
        graph.nodes()[node][assignment_col] = i 
        flipped_nodes.append(node)
        i += 1   
        if i > district_num:
            break

    # Create the partition
    partition = GeographicPartition(graph, assignment = assignment_col,
        updaters = my_updaters)

    # Return the district of every node to 1 (unassigned)
    for node in flipped_nodes:
        partition = partition.flip({node : 1})

    return partition

# get_updaters
# Create dictionary of updaters used for making partition
def get_updaters(pop_col):

    # Population Updater
    my_updaters = {"population": updaters.Tally(pop_col, alias = "population")}

    # Cut Edges Updater
    my_updaters.update({"cut_edges": updaters.cut_edges})

    return my_updaters