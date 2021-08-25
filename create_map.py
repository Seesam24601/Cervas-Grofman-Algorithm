#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_map.py

Created by Charlie Murphy
19 August 2021

This file creates a single redistricting plan with n-1 county splits.
'''

from gerrychain.constraints import deviation_from_ideal
import random

# Population Deviation
def pop_deviation(partition, district):
    return abs(deviation_from_ideal(partition)[district])

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

# Get County
# Returns all of the nodes in a particular county that are not currently in a
# district
def get_county(partition, county_col, pop_col, county, district):
    
    locality_intersections = get_intersections(partition, county_col)

    nodes = dict()
    population = 0

    for locality in locality_intersections:
        if locality == county:
            for d in locality_intersections[locality]:
                for x in partition.parts[d]:
                    if partition.graph.nodes[x][county_col] == locality:
                        nodes[x] = district
                        population += partition.graph.nodes[x][pop_col]

    return nodes, population

# New County
# Returns a bordering county that is not yet part of any district by randomly
# looking through cut edges
def new_county(partition, county_col, county, district):
    while True:

        # Get a random cut edge
        edge = random.choice(tuple(partition["cut_edges"]))

        # Find the districts and counties of this edge
        edge_districts = (partition.assignment[edge[0]], 
            partition.assignment[edge[1]])
        edge_counties = (partition.graph.nodes[edge[0]][county_col], 
            partition.graph.nodes[edge[1]][county_col])

        # Keep if the edge has one node in the current district and one node
        # that has yet to been assigned
        if edge_districts in [(1, district), (district, 1)]:

            # If the edge has one node in the current county and one node in
            # another county, return the other county.
            if county == edge_counties[0]:
                return edge_counties[1]
            elif county == edge_counties[1]:
                return edge_counties[0]

# Create Map
# Create a single redistricting plan using the Cervas-Grofman algorithm
def create_map(partition, county_col, pop_col, starting_county, 
    pop_deviation_max, district_num, ideal_population):

    # Get first county
    county = starting_county

    # Loop through every district except for the last one which will be created 
    # by the remaining vtds
    for district in range(2, district_num + 1):

        # While the next county chosen is a full county
        population = 0
        while True:

            # Get nodes and population of current county
            nodes, county_population = get_county(partition, county_col, pop_col, 
                county, district)

            # If the population of this county would make the population of the 
            # district greater than the ideal population, leave the loop
            if county_population > ideal_population - population:
                break

            # Otherwise add the county to the district
            partition = partition.flip(nodes)
            population += county_population

            # Find the next county.
            county = new_county(partition, county_col, county, district)

        return partition


        

            

            
