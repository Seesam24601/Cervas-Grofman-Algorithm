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

def new_county(partition, county, district):
    while True:

        edge = random.choice(tuple(partition["cut_edges"]))

        edge_districts = (partition.assignment[edge[0]], 
            partition.assignment[edge[1]])
        edge_counties = (partition.graph.nodes[edge[0]][county_field], 
            partition.graph.nodes[edge[1]][county_field])

        if edge_districts in [(1, district), (district, 1)]:

            if county == edge_counties[0]:
                return edge_counties[1]
            elif county == edge_counties[1]:
                return edge_counties[0]

def create_map(partition, county_col, pop_col, starting_county, 
    pop_deviation_max, district_num, ideal_population):

    county = starting_county

    for district in range(2, district_num + 1):

        population = 0

        while True:

            nodes, county_population = get_county(partition, county_col, pop_col, 
                county, district)

            if county_population > ideal_population - population:
                break

            partition.assignment.update(nodes)
            population += county_population

            county = new_county(partition, county, district)
            print(county)            

        return partition

        

            

            
