#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_clusters.py

Created by Charlie Murphy
15 February 2022

This file creates clusters of counties that can be divided evenly into districts
(within the allowed population deviation) so that the algorithm need to not 
create a path through the entire state at once.
'''

from copy import copy
from next_node import next_node
from partition_functions_2 import check_contiguous
import random

from write_partition import write_counties_to_csv

# creat_clusters
# Create valid cclusters of nodes in the map such that each cluster can be
# divided into an even number of districts, the total number of districts
# between all of the clusters is equivalent to the needed districts in the
# entire map and the clusters cover the entire map. Note that the VTD partition 
# is temporary argument for debuggin purposes
def create_clusters(partition, pop_col, starting_node, 
    population_deviation, district_num, ideal_population, dof_max, vtd_partition):

    # Set the starting position of the following variables
    district = 2
    dof_dictionary = dict()
    dof = 0
    population = 0
    nodes = set()
    allowed_nodes = partition.graph.nodes()

    # Add the starting node
    partition, dof_dictionary, population, nodes = add_node(partition, 
        starting_node, district, dof_dictionary, dof, pop_col, population, 
        nodes)

    # Create the list to keep track of how many districts are within each 
    # cluster
    district_list = [ 0 for i in range(district_num) ]

    # Find the next node to add to the current cluster
    bordering_nodes = next_node(partition, nodes, district, 
        dof_dictionary, allowed_nodes)

    # Call the recursive helper function the create the partition of the map
    # into node clusters
    validity, partition, district_list = cluster_helper(partition, district, nodes, 
        allowed_nodes, dof_dictionary, dof_max, population, pop_col,
        ideal_population, population_deviation, district_num, district_list,
        bordering_nodes, vtd_partition)

    # If the helper function returns a valid partition, return that partition
    if validity:
        print(district_list)
        print(sum(district_list))
        print()
        write_counties_to_csv(partition, vtd_partition, "GEOID20", "FIPS",
            "assignment", "Testing", "CLUSTER19")
        return partition

    print("No Plan Found")

def cluster_helper(partition, district, nodes, allowed_nodes, dof_dictionary,
    dof_max, population, pop_col, ideal_population, population_deviation,
    district_num, district_list, bordering_nodes, vtd_partition):

    if district == 14:
        write_counties_to_csv(partition, vtd_partition, "GEOID20", "FIPS",
            "assignment", "Testing", "CLUSTER17X")
        print("cut")
        input()

    if check_complete(partition, allowed_nodes):
        return True, partition, district_list

    # Check whether or not the unallocated nodes are contiguous on the whole
    # map
    if check_contiguous(partition):
        if district > district_num:
            district_list[0] = first_district_counties_num(partition, 
                allowed_nodes, ideal_population, population, 
                population_deviation, pop_col)
            return True, partition, district_list

    else:
        return False, None, None
        
    for dof in range(dof_max + 1):

        if dof not in bordering_nodes:

            # If we have tried every possible node, return false
            if dof == dof_max:
                print("GEORGE")
                return False, None, None
            continue

        # Shuffle the bordering counties
        max_length_keys = list(bordering_nodes[dof])
        random.shuffle(max_length_keys)

        for node in max_length_keys:

            proposed_partition, proposed_dof_dictionary, proposed_population, \
                proposed_nodes = add_node(partition, node, district, 
                dof_dictionary.copy(), dof, pop_col, population, nodes.copy())  

            counties_num = number_of_counties(proposed_population, ideal_population, 
                population_deviation)

            new_bordering_nodes = next_node(proposed_partition, proposed_nodes, 
                district, proposed_dof_dictionary, allowed_nodes)

            proposed_district = district
            proposed_district_list = district_list.copy()
            if counties_num != 0:
                proposed_district += 1
                proposed_district_list[district - 1] = counties_num

                proposed_nodes = set()
                proposed_dof_dictionary = dict()
                proposed_population = 0

                #new_bordering_nodes = reformat(new_bordering_nodes)
                print(proposed_district)

            validity, new_partition, new_district_list = cluster_helper(proposed_partition, 
                proposed_district, proposed_nodes, allowed_nodes, 
                proposed_dof_dictionary, dof_max, proposed_population, pop_col,
                ideal_population, population_deviation, district_num, 
                proposed_district_list, new_bordering_nodes, vtd_partition)

            if validity:
                return True, new_partition, new_district_list

def add_node(partition, node, district, dof_dictionary, dof_effect, pop_col,
    population, nodes):

    partition = partition.flip({node : district})

    dof_dictionary[node] = dof_effect

    population += partition.graph.nodes[node][pop_col]

    nodes.add(node)

    return partition, dof_dictionary, population, nodes

def number_of_counties(population, ideal_population, population_deviation):

    counties_num = int(population / ideal_population)

    if check_counties_num(population, counties_num, ideal_population, 
        population_deviation):
        return counties_num

    if check_counties_num(population, counties_num + 1, ideal_population, 
        population_deviation):
        return counties_num + 1

    else:
        return 0

def check_counties_num(population, counties_num, ideal_population, 
    population_deviation):
    return abs(population - (counties_num * ideal_population)) <= \
        counties_num * population_deviation

def check_complete(partition, allowed_nodes):
    count = 0
    for node in allowed_nodes:
        if partition.assignment[node] == 1:
            count += 1
    return count == 0

def reformat(bordering_nodes):
    new_bordering_nodes = dict()
    new_bordering_nodes[0] = set()

    for dof in bordering_nodes.keys():
        for node in bordering_nodes[dof]:
            new_bordering_nodes[0].add(node)

    return new_bordering_nodes

def first_district_counties_num(partition, allowed_nodes, ideal_population, 
    population, population_deviation, pop_col):

    population = 0
    for node in allowed_nodes:
        if partition.assignment[node] == 1:
            population += partition.graph.nodes[node][pop_col]

    return number_of_counties(population, ideal_population, 
        population_deviation)