#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
partition_counties.py

Created by Charlie Murphy
11 September 2021

This file takes a graph of counties in the state and following the Cervas-
Groffman algorithm returns a dictionary mapping each county ID to a list of 
tuples. These tuples are in the format (district, population) which corresponds
to the population to be added to that district from the county. Only districts
that are in a given county are included in the list. Moreover, the sum of the
populations from the list of tuples for a given county will be equal to the 
total population of that county.

Note that in this file county name refers to the FIPS id (or similar) assigned
to the counties in the field county_col while county id refers to the index of
the node object associated with that county in the graph.
'''

from copy import deepcopy
from partition_functions import (check_population, add_to_assignment,
    check_contiguous)
import random
from write_partition import write_to_shapefile

# partition_counties
# Continue to try to create valid county assignment dictionaries and return 
# one once created
def partition_counties(partition, county_col, pop_col, starting_county, 
    flipped_counties, epsilon, district_num, ideal_population, county_to_id, 
    id_to_county, county_populations, county_list):

    # Flip all of the counties to district 1
    for county in flipped_counties:
        partition = partition.flip({county_to_id[county] : 1})

    # Continue to try to create a valid county assignment dictionary
    while True:
        validity, county_assignments = attempt_county_partition(partition, 
            county_col, pop_col, starting_county, epsilon, district_num, 
            ideal_population, county_to_id, id_to_county, county_populations)

        # If the dictionary is valid, return the dictionary
        if validity:
            clean_assignment(county_assignments, partition, county_col, pop_col, 
               county_to_id, county_populations, county_list)
            return county_assignments

# attempt_county_partition
# Attempt to create a valid county assignment dictionary using the
# Cervas-Groffman algorithm
def attempt_county_partition(partition, county_col, pop_col, starting_county, 
    epsilon, district_num, ideal_population, county_to_id, id_to_county, 
    county_populations):

    # Set the default values
    district = 2
    pieces = 2
    population = 0
    
    # Create empty dictionaries and lists as needed
    county_assignments = dict()
    counties = []

    # Add all single_county_districts
    partition, district, pieces = single_county_districts(partition, 
        county_assignments, county_col, pop_col, id_to_county, district, 
        ideal_population, epsilon, county_populations, pieces)

    # Add starting county
    partition, counties, county_assignments, district, population, pieces, \
        dof_dictionary = add_county(
        partition, starting_county, county_to_id, counties, county_assignments, 
        district, pop_col, population, ideal_population, epsilon, pieces,
        district_num, county_populations, {}, 0)

    # Continue adding counties until either you create a full plan you the 
    # program gets stuck
    while True:

        # Find the unallocated counties that border the current district
        solution = False
        bordering_counties = get_next_county(partition, counties, 
            county_to_id, id_to_county, district, dof_dictionary)

        # Start at the minimum number of nodes away from the starting node and
        # move upward
        for dof in range(50):
            if dof not in bordering_counties:
                if dof == 49:
                    return False, county_assignments 
                continue

            # Shuffle the bordering counties
            max_length_keys = list(bordering_counties[dof])
            random.shuffle(max_length_keys)

            # For each bordering county, try to add it to the plan
            for key in max_length_keys:
                county = id_to_county[key]

                # Attempt to add the county
                proposed_partition, proposed_counties, \
                    proposed_county_assignments, proposed_district, \
                    proposed_population, proposed_pieces, \
                    proposed_dof_dictionary = add_county(partition,
                    county, county_to_id, counties.copy(), 
                    deepcopy(county_assignments), district, pop_col, population, 
                    ideal_population, epsilon, pieces, district_num,
                    county_populations, dof_dictionary.copy(), dof)

                # Check whether this addition preserves the contiguity of the
                # plan
                if check_contiguous(proposed_partition, proposed_pieces):
                    partition = proposed_partition
                    counties = proposed_counties
                    county_assignments = proposed_county_assignments
                    district = proposed_district
                    population = proposed_population
                    pieces = proposed_pieces
                    dof_dictionary = proposed_dof_dictionary

                    solution = True
                    break

            if solution:
                break

        # If a valid plan is found, return it
        if district == district_num and check_population(population,
            ideal_population, epsilon):
            return True, county_assignments

# add_county
# For a given county, divide it between districts based on how much population
# a given district needs to be at ideal population and the population of the
# county
def add_county(partition, county, county_to_id, counties, county_assignments,
    district, pop_col, population, ideal_population, epsilon, pieces, 
    district_num, county_populations, dof_dictionary, dof_effect):

    # Get the county ID of the county
    county_id = county_to_id[county]

    # Remove the population of any districts fully contained in the county from
    # the county population used for the below calculations
    county_population = county_populations[county]
    if county in county_assignments:
        for assignment in county_assignments[county]:
            county_population -= assignment[1]

    # If the current district is at the ideal population, put the entirity of the
    # county in a new district
    if check_population(population, ideal_population, epsilon):
        district += 1
        pieces += 1
        counties = []
        population = county_population
        add_to_assignment(county_assignments, county, district, 
            population)
        dof_dictionary = {county_id : 0}

    # If the population remaining to get the current district to the ideal 
    # population is less than the county population, split the county between
    # the current distrit and the new one such that the current district is at
    # the ideal population.
    elif county_population + population > ideal_population * (1 + epsilon):
        remaining_population = ideal_population - population
        add_to_assignment(county_assignments, county, district, 
            remaining_population)
        if district < district_num:
            district += 1
            pieces += 1
            counties = []
            population = county_population - remaining_population
            add_to_assignment(county_assignments, county, district, 
                population)
            dof_dictionary = {county_id : 0}
        else:
            population = ideal_population

    # If the population needed for the district to be at the ideal population
    # is greater than or equal to the county population, place the entire
    # county in the current district.
    else:
        population += county_population
        add_to_assignment(county_assignments, county, district, 
            county_population)
        dof_dictionary[county_id] = dof_effect
    
    # Update the counties list and partition accordingly
    counties.append(county_id)
    partition = partition.flip({county_id : district})

    return (partition, counties, county_assignments, district, population,
        pieces, dof_dictionary)

# single_county_districts
# Add as many districts as possible where the district is fully contained within
# a county
def single_county_districts(partition, county_assignments, county_col, pop_col,
    id_to_county, district, ideal_population, epsilon, county_populations, 
    pieces):

    for i in range(len(partition.graph.nodes())):
        county_population = county_populations[id_to_county[i]]

        # While additional full districts can fit within a county
        while True:

            # If the county is within epsilon of the ideal population, add the 
            # whole county to a single district
            if check_population(county_population, ideal_population, epsilon):
                add_to_assignment(county_assignments, id_to_county[i], district, 
                    county_population)
                partition = partition.flip({i : district})
                district += 1
                pieces += 1
                break

            # Otherwise if the county is larger than the ideal population, add a 
            # district the size of the ideal population to the county
            elif county_population > ideal_population:
                add_to_assignment(county_assignments, id_to_county[i], district, 
                    ideal_population)
                district += 1
                county_population -= ideal_population

            else:
                break
        
    return partition, district, pieces

# clean_assignment
# For any county that has had some of it's population assigned to a district, 
# but not the entire population, assign the remainder of the population in said
# county to district 1
def clean_assignment(county_assignments, partition, county_col, pop_col, 
    county_to_id, county_populations, county_list):

    # Loop through counties that have been assgined
    for county in county_list:

        # If the county has at least a portion not in district 1
        if county in county_assignments:

            # Calculate the population within the county that has been assigned
            population = 0
            for pair in county_assignments[county]:
                population += pair[1]

            # If this is less than the county population, allocate the 
            # difference to district 1
            real_population = county_populations[county]
            if population != real_population:
                county_assignments[county].append((1, 
                    real_population - population))

            # Sort from smallest population to largest
            county_assignments[county].sort(key = lambda x: x[1])

        # If the county is fully in district 1
        else:
            county_assignments[county] = [(1, county_populations[county])]

# get_next_county
# Returns the name of an unused county that borders the current district. If 
# unused counties exist that border two or more counties already in the district
# then one of them will be chosen
def get_next_county(partition, counties, county_to_id, id_to_county, district,
    dof_dictionary):

    # Create empty dictionaries for counties that border the district
    bordering_counties = dict()
   
    # Loop through the cut edges
    for edge in partition["cut_edges"]:

        # Create a tuple of the districts and counties on each side of each 
        # cut edge
        edge_districts = (partition.assignment[edge[0]], 
            partition.assignment[edge[1]])
        edge_counties = (edge[0], edge[1])

        # Keep if the edge has one node in the current district and one node
        # that has yet to been assigned
        if edge_districts in [(1, district), (district, 1)]:

            # Map each bordering county to the number of nodes it is away from 
            # the first node placed for said district
            for i in range(2):
                if edge[i] in counties:
                    index = dof_dictionary[edge[i]] + 1
                    if index not in bordering_counties:
                        bordering_counties[index] = set()
                    bordering_counties[index].add(edge[i - 1])
                    break
                    
    return bordering_counties