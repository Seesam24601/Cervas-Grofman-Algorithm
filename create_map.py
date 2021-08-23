#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_map.py

Created by Charlie Murphy
19 August 2021

This file creates a single redistricting plan with n-1 county splits.
'''

from gerrychain.constraints import deviation_from_ideal

# Population Deviation
def pop_deviation(partition, district):
    return deviation_from_ideal(partition)[district]

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
def get_county(partition, county_col, county):
    
    locality_intersections = get_intersections(partition, county_col)

    nodes = set()
    for locality in locality_intersections:
        if locality == county:
            for d in locality_intersections[locality]:
                for x in partition.parts[d]:
                    if partition.graph.nodes[x][county_col] == locality:
                        nodes.add(x)

    return frozenset(nodes)

def create_map(partition, county_col, starting_county, pop_deviation_max, 
    district_num):

    for district in range(2, district_num + 1):
     
        county = None
        # while pop_deviation(partition, district) < pop_deviation_max:

        if district == 2 and county is None:
            county = starting_county

        nodes = get_county(partition, county_col, county)
        partition.assignment.update_parts({district: nodes})

        return partition

        

            

            
    