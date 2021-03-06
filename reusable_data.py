#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
resuable_data.py

Created by Charlie Murphy
17 October 2021

This file caclulates specific metrics that are used by the algorithm and are the
same between runs so that by calculating them once the algorithm can run more 
efficiently
'''

# border_county_edges
# takes a graph (via a partition) and returns a dictionary with that maps pairs 
# of counties to the edges (as tuples of node ids in the graph), that are 
# between said counties
def border_county_edges(graph, county_col):
    dictionary = dict()

    # Loop through the edges of the graph
    for edge in graph.edges():
        edge_counties = (graph.nodes()[edge[0]][county_col],
            graph.nodes()[edge[1]][county_col])

        # Only add edges that reach across a county border.
        if edge_counties[0] != edge_counties[1]:
            safe_add(dictionary, edge_counties[0], edge_counties[1], edge)

    return dictionary

# safe_add
# Given two counties adds them to dictionary based on whether the county pair
# is already in the dictionary or not
def safe_add(dictionary, county1, county2, edge):
    if (county1, county2) in dictionary:
        dictionary[(county1, county2)].add(edge)
    elif (county2, county1) in dictionary:
        dictionary[(county2, county1)].add(edge)
    else:
        S = set()
        S.add(edge)
        dictionary[(county1, county2)] = S

# bordering_counties
# Returns a list of tuples of counties that border one another
def bordering_counties(graph, county_col, id_to_county):
    bordering_counties = []
    for edge in graph.edges():
        bordering_counties.append((id_to_county[edge[0]],id_to_county[edge[1]]))
    return bordering_counties

# county_population
# Return the population of the given county as given by the node
def get_county_population(graph, county_id, pop_col):
    return graph.nodes[county_id][pop_col]

# county_populations
# Create a dictionary mapping counties to their population
def get_county_populations(graph, id_to_county, pop_col):
    populations = dict()

    # Loop through every county
    for node in graph:
        populations[id_to_county[node]] = get_county_population(graph, node, 
        pop_col)

    return populations

# get_county_to_id
# Create a dictionary that maps county names to ids
def get_county_to_id(graph, county_col):
    county_to_id = dict()
    for i in range(len(graph.nodes())):
        county_to_id[graph.nodes()[i][county_col]] = i
    return county_to_id

# get_id_to_county
# Flips the county_to_id dictionary
def get_id_to_county(county_to_id):
    return dict((values, keys) for keys, values in county_to_id.items())

# Get intersections
# Returns a dictionary of nodes that splits the state by both county and 
# district boundaries
def get_intersections(partition, county_col):

    locality_intersections = {}

    for n in partition.graph.nodes():
        locality = partition.graph.nodes[n][county_col]
        if locality not in locality_intersections:
            locality_intersections[locality] = set(
                [partition.assignment[n]])

        locality_intersections[locality].update([partition.assignment[n]])

    return locality_intersections

# get_subgraph
# Return the collection of nodes within a county.
def get_subgraph(graph, county_col, county):

    nodes = set()
    for node in graph.nodes:
        if graph.nodes[node][county_col] == county:
            nodes.add(node)
    
    return nodes

# get_county_subgraphs
# Returns a dictionary mapping counties to their sugbraphs of nodes in the given
# partition
def get_county_subgraphs(partition, counties, county_col):
    subgraphs = dict()

    # Loop through every county
    for county in counties:
        subgraphs[county] = get_subgraph(partition, county_col, county)

    return subgraphs

# get_border_nodes
# Create a dictionary mapping counties to municipalities on the border of said 
# counties
def get_border_nodes(graph, county_col):
    dictionary = dict()

    # Loop through the edges of the graph
    for edge in graph.edges():
        edge_counties = (graph.nodes()[edge[0]][county_col],
            graph.nodes()[edge[1]][county_col])

        # Only add edges that reach across a county border.
        if edge_counties[0] != edge_counties[1]:
            for i in range(0,2):
                if edge_counties[i] in dictionary:
                    dictionary[edge_counties[i]].add(edge[i])
                else:
                    S = set()
                    S.add(edge[i])
                    dictionary[edge_counties[i]] = S

    # Convert to list to improve effiiency when making random calls
    for county in dictionary:
        dictionary[county] = list(dictionary[county])

    return dictionary

# resuable_data
# Collects and returns all of the reusable data structures from this file
def reusable_data(county_graph, muni_graph, vtd_graph, county_col, muni_col,
    pop_col):
    
    county_to_id = get_county_to_id(county_graph, county_col)
    id_to_county = get_id_to_county(county_to_id)

    muni_to_id = get_county_to_id(muni_graph, muni_col)
    id_to_muni = get_id_to_county(muni_to_id)

    border_muni = bordering_counties(muni_graph, muni_col, id_to_muni)

    border_county = bordering_counties(county_graph, county_col, id_to_county)

    border_edges = border_county_edges(vtd_graph, muni_col)

    border_edges_county = border_county_edges(muni_graph, county_col)

    border_nodes = get_border_nodes(muni_graph, county_col)

    county_populations = get_county_populations(county_graph, id_to_county, 
        pop_col)
    counties = list(county_populations.keys())

    muni_populations = get_county_populations(muni_graph, id_to_muni, 
        pop_col)
    munis = list(muni_populations.keys())

    county_subgraphs = get_county_subgraphs(muni_graph, counties, county_col)

    muni_subgraphs = get_county_subgraphs(vtd_graph, munis, muni_col)

    return (county_to_id, id_to_county, muni_to_id, id_to_muni, border_muni, 
        border_county, border_edges, border_nodes, county_populations, counties, 
        muni_populations, munis, county_subgraphs, muni_subgraphs, 
        border_edges_county)