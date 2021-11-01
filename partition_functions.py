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

# add_districts
# Add the assignment column to the data with the appropriate number of districts
def add_districts(data_county, assignment_col, county_col, district_num):
    data_county[assignment_col] = 1
    district = 2
    flipped_counties = set()

    # Search through the nodes and flip until one node has been flipped for
    # every district
    for i in range(len(data_county[assignment_col])):
        flipped_counties.add(data_county[county_col][i])
        data_county[assignment_col][i] = district
        district += 1
        if district > district_num:
            break

    return data_county, flipped_counties

# Get County nodes
# Returns all of the nodes in a particular county
def get_county_nodes(subgraph, district):
    nodes = dict()

    for x in subgraph:
        nodes[x] = district

    return nodes

# check_population
# Return true if the population is within epsilon of the ideal population
def check_population(population, ideal_population, epsilon):
    return ((population <= (ideal_population * (1 + epsilon))) 
        and (population >= (ideal_population * (1 - epsilon))))

# add_to_assignment
# Safely adds a value to a dictionary regardless of whether or not the key is
# already present
def add_to_assignment(county_assignments, county, district, population):
    if county not in county_assignments:
        county_assignments[county] = [(district, population)]
    else:
        county_assignments[county].append((district, population))

# check_contiguous
# Return true if no districts are split between multiple discontiguous parts
def check_contiguous(partition, pieces):

    # Count the number of connected components
    current_pieces = 0
    for part, subgraph in partition.subgraphs.items():
        current_pieces += number_connected_components(subgraph)

    # Make sure the number of connected components is equal to the number of
    # districts
    return current_pieces == pieces