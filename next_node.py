#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
next_node.py

Created by Charlie Murphy
17 December 2021

This file returns a dictionary mapping possible next nodes to how many nodes
they are away from the first node allocated for this district.
'''

"""
UPDATES:

use set instead of partition assignment
use edges as limiter instead of nodes
would allow for disuse of updaters?
"""

# next_node
# Give a partiton and node create a dictionary mapping the distance away from 
# the first node in the district to the unallocated nodes that currently border
# the district
def next_node(partition, nodes, district, dof_dictionary, allowed_nodes):

    # Create empty dictionaries for nodes that border the district
    bordering_nodes = dict()
   
    # Loop through the cut edges
    for edge in partition["cut_edges"]:

        # Map each bordering county to the number of nodes it is away 
        # from the first node placed for said district
        for i in range(2):
            if (edge[i] in nodes and edge[i - 1] in allowed_nodes 
                and partition.assignment[edge[i - 1]] == 1):

                index = dof_dictionary[edge[i]] + 1
                if index not in bordering_nodes:
                    bordering_nodes[index] = set()
                bordering_nodes[index].add(edge[i - 1])
                break
                    
    return bordering_nodes