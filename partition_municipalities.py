#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
partition_municipalities.py

Created by Charlie Murphy
25 October 2021

This file takes in a county_assignments dictionary and a graph of municipalities
and splits counties that need to be split by municipality. It returns a 
muni_assignments dictionary in the same format of the county_assignments
dictionary
'''

from copy import copy, deepcopy
from partition_functions import (get_county_nodes, check_population, 
    add_to_assignment, check_contiguous)
import random

# partition_municipalities
# Continue to try to make valid municipality assignment dictionaries. If one can
# be created return it. If the maximum number of tries is found first, return
# a failure
def partition_municipalities(partition, muni_col, pop_col, epsilon, 
    county_assignments, muni_to_id, id_to_muni, muni_populations, muni_list,
    county_subgraphs, border_nodes, flipped_munis, max_tries, county_col):

    # Flip all of the counties to district 1
    for muni in flipped_munis:
        partition = partition.flip({muni_to_id[muni] : 1})
    
    muni_assignments, partition, districts_used = add_unsplit_counties(partition, 
        county_assignments, county_subgraphs, id_to_muni, muni_populations)

    for county in county_assignments:

        if len(county_assignments[county]) != 1:

            print(county)
            print(county_assignments[county])

            for count in range(max_tries):
                validity, proposed_muni_assignments, proposed_partition,\
                    proposed_districts_used = attempt_muni_partition(partition, 
                    deepcopy(muni_assignments), county, 
                    county_assignments[county], border_nodes, muni_to_id, 
                    id_to_muni, muni_populations, epsilon, copy(districts_used),
                    county_col)
                print(count)

                if validity:
                    muni_assignments = proposed_muni_assignments
                    partition = proposed_partition
                    districts_used = proposed_districts_used
                    print("SUCCESS")
                    break

            if not validity:
                print("FAILED")
                return False, muni_assignments

            print()

    return True, muni_assignments

# add_unsplit_counties
# For every county that is not split, add the unsplit county both to the
# partition and to the muni_assignmentSSs dictionary
def add_unsplit_counties(partition, county_assignments, county_subgraphs,
    id_to_muni, muni_populations):

    muni_assignments = dict()

    districts_used = set()

    # Loop through the un-split counties
    for county in county_assignments:
        if len(county_assignments[county]) == 1:
            nodes = county_subgraphs[county]
            district = county_assignments[county][0][0]
            districts_used.add(district)

            # Add municipalities to muni_assignment
            for muni in nodes:
                muni_assignments[id_to_muni[muni]] = [(district, 
                    muni_populations[id_to_muni[muni]])]

            # Add municipalities to partition
            partition = partition.flip(get_county_nodes(nodes, district))
    
    return muni_assignments, partition, districts_used

# attempt_muni_partition
# Loop through each split county and for each one partition between 
# municipalities
def attempt_muni_partition(partition, muni_assignments, county, districts, 
    border_nodes, muni_to_id, id_to_muni, muni_populations, epsilon, 
    districts_used, county_col):

    index = 0
    index_max = len(districts) - 1
    if districts[index][0] == 1:
        index += 1

    population = 0
    final_ideal_population = districts[index_max][1]

    munis = []

    # Add first municipality
    start_muni = get_start_muni(county, border_nodes, id_to_muni)
    while index <= index_max and munis == []:
        partition, munis, muni_assignments, index, population, districts_used \
            = add_muni(partition, muni_assignments, start_muni, muni_to_id, 
            index, population, districts, muni_populations, epsilon, munis,
            districts_used)

    if index >= index_max:
        return True, muni_assignments, partition, districts_used

    print()
    print(muni_assignments[start_muni])

    count = 0
    while True:
        count +=1

        # print(munis)
        # print(population)
        # print()

        # Find the unallocated counties that border the current district
        solution = False
        bordering_munis = get_next_muni(partition, munis, 
            muni_to_id, id_to_muni, districts[index][0], county, county_col)

        print(id_to_muni[munis[0]])
        # print(bordering_munis)

        # Find the maximum number of counties in the district that a bordering
        # county borders
        max_length = max(map(len, bordering_munis.values()))

        # Start at the maximum number and move downwards for how many counties
        # in the district are bordered
        for length in range(max_length, -1, -1):
            if length == 0: 
                return False, muni_assignments, partition, districts_used

            # Shuffle the bordering counties
            max_length_keys = [key for key, value in bordering_munis.items() 
                if len(value) == length]
            random.shuffle(max_length_keys)

            # For each bordering county, try to add it to the plan
            for key in max_length_keys:
                muni = id_to_muni[key]

                # Attempt to add the county
                proposed_partition, proposed_munis, proposed_muni_assignments, \
                    proposed_index, proposed_population, proposed_districts_used \
                    = add_muni(partition, deepcopy(muni_assignments), muni, 
                    muni_to_id, index, population, districts, muni_populations, 
                    epsilon, munis, districts_used)

                # Check whether this addition preserves the contiguity of the
                # plan

                # note: may be issue when district = 1
                # if check_contiguous(proposed_partition, 
                # len(proposed_districts_used)):
                partition = proposed_partition
                munis = proposed_munis
                muni_assignments = proposed_muni_assignments
                index = proposed_index
                population = proposed_population
                districts_used = proposed_districts_used

                solution = True

                #print()
                print("POP:", population)
                #print()

                break

            if solution:
                break

        # If a valid plan is found, return it
        print(index, index_max, count)
        if districts[index][0] == 1:
            index += 1
        if index >= index_max and check_population(population,
            final_ideal_population, epsilon):
            return True, muni_assignments, partition, districts_used

def get_start_muni(county, border_nodes, id_to_muni):
    return id_to_muni[random.choice(border_nodes[county])]

def add_muni(partition, muni_assignments, muni, muni_to_id, index, population,
    districts, muni_populations, epsilon, munis, districts_used):

    muni_id = muni_to_id[muni]
    district = districts[index][0]
    districts_used.add(district)
    ideal_population = districts[index][1]

    muni_population = muni_populations[muni]
    if muni in muni_assignments:
        for assignment in muni_assignments[muni]:
            muni_population -= assignment[1]

    # print(muni_population)

    if check_population(population, ideal_population, epsilon):
        index += 1
        population = 0
        munis = [muni_id]
        print("A")

        partition, munis, muni_assignments, index, population, districts_used =\
            add_muni(partition, muni_assignments, muni, muni_to_id, index, 
            population, districts, muni_populations, epsilon, munis, 
            districts_used)

    elif muni_population > (ideal_population * (1 + epsilon) - population):
        add_to_assignment(muni_assignments, muni, district, 
            ideal_population - population)

        muni_population = muni_population - (ideal_population - population)
        index += 1
        population = 0
        munis = [muni_id]
        print("B")

        partition, munis, muni_assignments, index, population, districts_used =\
            add_muni(partition, muni_assignments, muni, muni_to_id, index, 
            population, districts, muni_populations, epsilon, munis, 
            districts_used)
    
    else:
        population += muni_population
        munis.append(muni_id)
        add_to_assignment(muni_assignments, muni, district, muni_population)
        partition = partition.flip({muni_id : district})

    print(population, ideal_population, muni_population)
    # print(muni_assignments[muni])

    return (partition, munis, muni_assignments, index, population, 
        districts_used)

def get_next_muni(partition, munis, muni_to_id, id_to_muni, district, county,
    county_col):

    # Create empty dictionaries for counties that border the district
    bordering_munis = dict()
   
    # Loop through the cut edges
    for edge in partition["cut_edges"]:

        # Create a tuple of the districts and counties on each side of each 
        # cut edge
        edge_districts = (partition.assignment[edge[0]], 
            partition.assignment[edge[1]])
        edge_munis = (edge[0], edge[1])
        edge_counties = (partition.graph.nodes[edge[0]][county_col], 
            partition.graph.nodes[edge[1]][county_col])

        # Keep if the edge has one node in the current district and one node
        # that has yet to been assigned
        if (edge_counties == (county, county) and 
            edge_districts in [(1, district), (district, 1)]):

            # If a cut edge exists between a county in the district and an
            # unused county, add the id of the unused county to the bordering
            # county dictionary
            for i in range(0, 2):
                if edge_munis[i] in munis:
                    if edge_munis[i - 1] not in bordering_munis:
                        bordering_munis[edge_munis[i - 1]] = \
                            [edge_munis[i]]
                    else:
                        bordering_munis[edge_munis[i - 1]].append(
                                edge_munis[i])
                    break

    return bordering_munis