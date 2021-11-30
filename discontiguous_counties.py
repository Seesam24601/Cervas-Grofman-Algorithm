#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
discontiguous_counties.py

Created by Charlie Murphy
24 September 2021

This file adds a single edge so that all counties in PA are contiguous. The same
approach can be used to correct counties in other states if necessary
'''

from gerrychain import GeographicPartition
from networkx import number_connected_components, connected_components
from partition_functions import get_pieces
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
# Prints a warning and the offending municipalities' names if there is any
# municipality nodes that share the same ID. Typically this means that the 
# municipality is split between two counties.
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

# check_donuts
# Returns a dictionary mapping every donut node to the set of donut_hole nodes
# that are inside of it. A donut_hole is defined as any municipality in a county
# that is separated from the majority of the other municipalities in the county
# by a single municipality. A donut hole is any such municipality
def check_donuts(graph, counties, county_subgraphs, assignment_col):

    # Create empty dictionary
    donuts = dict()

    # Loop through every county
    for county in counties:

        # Create a subgraph of each county that has the capacity to handle 2 
        # districts
        current_graph = graph.subgraph(county_subgraphs[county])
        if len(current_graph.nodes()) > 1:
            for node in current_graph.nodes():
                current_graph.nodes()[node][assignment_col] = 2
                break

            # Create a partition of the subgraph
            current_partition = GeographicPartition(current_graph, 
                assignment = assignment_col)

            # Create a set of all donut holes within the county
            county_donuts = set()

            # Flip every node to district 1 to start
            for node in current_partition.graph.nodes():
                current_partition = current_partition.flip({node : 1})
            
            # Loop through every node
            for node in current_partition.graph.nodes():

                # If the node is not a donut hole, move it to district 2
                if node not in county_donuts:
                    current_partition = current_partition.flip({node : 2})

                    # If this results in district 1 becoming discontiguous,
                    # then the current note is a donut
                    for part, subgraph in current_partition.subgraphs.items():
                        if (part == 1 and 
                            number_connected_components(subgraph) != 1):

                            # We then search through all of the connected 
                            # components of district 1 and for all but the 
                            # largest component any nodes in the components
                            # are considered donut holes of the current district
                            # and added to dictionary accordingly
                            maxlength = 0
                            componentlist = []
                            donut_holes = set()
                            donuts[node] = donut_holes
                            for component in connected_components(subgraph):
                                componentlist.append(component)
                                if len(component)>maxlength:
                                    maxlength = len(component)
                            for component in componentlist:
                                if len(component) < maxlength:
                                    for add_node in component:
                                        donut_holes.add(add_node)
                                        county_donuts.add(add_node)

                    # Flip the node back to district 1 before the next cycle of
                    # the loop
                    current_partition = current_partition.flip({node : 1})
        
    return donuts
        