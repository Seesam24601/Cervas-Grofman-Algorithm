#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
county_borders.py

Created by Charlie Murphy
25 August 2021

This file contains snippets of code that could be used to get a set of tuples 
representing all of the counties that border one another.
'''

from gerrychain import GeographicPartition

# Get County Graph
# Returns a partition of a graph by county.
def get_county_graph(graph, county_col, updaters):
    return GeographicPartition(graph, assignment = county_col,
        updaters = my_updaters)

# County Borders
# Returns a set of tuples off all of the pairs of counties that border one 
# another
def county_borders(graph, county_col, updaters):

    # Get partition of the graph by county
    county_graph = get_county_graph(graph, county_col, updaters)

    # Make a set of the borders using cut edges
    county_pairs = set()
    for edge in tuple(partition["cut_edges"]):
        edge_counties = (county_graph.assignment[edge[0]], 
            county_graph.assignment[edge[1]])
        county_pairs.add(edge_counties)