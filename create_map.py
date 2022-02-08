#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_map.py

Created by Charlie Murphy
17 December 2021

This file creates a single redistricting plan with n-1 county splits by
applying the Cervas-Groffman Algorithm.
'''

from add_node import add_node, flip_node
from copy import copy
from gerrychain import GeographicPartition
from partition_functions_2 import (check_contiguous, check_population, safe_add, 
    check_split_nodes, check_subgraph)
from make_partition import get_updaters, make_partition
from next_node import next_node
import random

from write_partition import write_to_csv


# create_map
# Crate a single redistricting plan with n-1 county splits by applying the 
# Cervas-Groffman Algorithm.
def create_map(county_partition, muni_partition, vtd_partition, county_col, 
    muni_col, pop_col, starting_node, population_deviation, district_num, 
    ideal_population, dof_max, level_conversions, counties, assignment_col):

    # Start with district 2 since district 1 represents unallocated nodes
    district = 2

    # Create partitions list
    partitions = [county_partition, muni_partition, vtd_partition]

    # Add single county nodes
    """
    start_partitions, district, single_dict = single_county_districts(
        partitions, pop_col, district, ideal_population, population_deviation, 
        level_conversions)
    """
    start_partitions = partitions
    single_dict = dict()
    split_nodes = [set(),set()]

    # Create initial population goal list
    goals = [ideal_population for i in range(district_num)]

    # Continue until a valid plan is found
    while True:
        validity, completition, partitions, goals, districts, \
            remaining_population = attempt_map(start_partitions, county_col, 
            muni_col, pop_col, starting_node, population_deviation, 
            district_num, goals, dof_max, district, single_dict, 0, 
            level_conversions, counties, 0, split_nodes, assignment_col)

        if validity:
            return partitions[2]

# attempt_map
# Try to make a valid map if one exists.
def attempt_map(partitions, county_col, muni_col, pop_col, starting_node,
    population_deviation, district_num, goals, dof_max, district, single_dict, 
    level, level_conversions, allowed_nodes, subgraph_population, split_nodes,
    assignment_col):

    unused_nodes = allowed_nodes.copy()

    subgraph_partition = None
    if level !=0 :
        subgraph = partitions[level].graph.subgraph(allowed_nodes)
        my_updaters = get_updaters(pop_col)
        subgraph_partition = make_partition(subgraph, district_num, assignment_col,
            my_updaters)

    # Add starting county
    validity, completition, partitions, nodes, district, population, \
        dof_dictionary, goals, split_nodes, unused_nodes, subgraph_partition = \
        add_node(partitions, starting_node, district, 0, goals, pop_col, 
        {}, 0, single_dict, population_deviation, set(), district_num, level,
        level_conversions, county_col, muni_col, dof_max, allowed_nodes, 
        subgraph_population, split_nodes, unused_nodes, subgraph_partition,
        assignment_col)

    # Continue adding counties until either you create a full plan you the 
    # program gets stuck
    count = 1
    while True:

        # Find the unallocated counties that border the current district
        solution = False
        bordering_nodes = next_node(partitions[level], nodes, district, 
            dof_dictionary, allowed_nodes)

        # Start at the minimum number of nodes away from the starting node and
        # move upward
        for dof in range(dof_max + 1):
            if dof not in bordering_nodes:

                # If we have tried every possible node, return false
                if dof == dof_max:
                    print("GEORGE")
                    return False, False, partitions, goals, district, population
                continue

            # Shuffle the bordering counties
            max_length_keys = list(bordering_nodes[dof])
            random.shuffle(max_length_keys)

            # For each bordering county, try to add it to the plan
            for node in max_length_keys:
                
                # Attempt to add the county
                validity, completion, proposed_partitions, proposed_nodes, \
                    proposed_district, proposed_population, \
                    proposed_dof_dictionary, proposed_goals, \
                    proposed_split_nodes, proposed_unused_nodes, \
                    proposed_subgraph_partition = add_node(partitions.copy(), 
                    node, district, population, goals, pop_col, 
                    dof_dictionary.copy(), dof, single_dict, 
                    population_deviation, nodes.copy(), district_num, level,
                    level_conversions, county_col, muni_col, dof_max, 
                    subgraph_population, allowed_nodes, split_nodes.copy(), 
                    unused_nodes.copy(), subgraph_partition, assignment_col)

                # If this is a lower level (muni or VTD) and the rest of the
                # superset has been filled in, then declare the subgraph
                # complete
                if completion:
                    partitions = proposed_partitions
                    nodes = proposed_nodes
                    district = proposed_district
                    population = proposed_population
                    dof_dictionary = proposed_dof_dictionary
                    goals = proposed_goals
                    split_nodes = proposed_split_nodes
                    unused_nodes = proposed_unused_nodes
                    subgraph_partition = proposed_subgraph_partition

                    return (True, False, partitions, goals, proposed_district, 
                        population)

                # Check whether this addition preserves the contiguity of the
                # plan
                if (validity and check_contiguous(proposed_partitions[level])
                    and check_subgraph(proposed_subgraph_partition, level)
                    and check_split_nodes(proposed_partitions, level, 
                    proposed_split_nodes, node, proposed_district)):
                    partitions = proposed_partitions
                    nodes = proposed_nodes
                    district = proposed_district
                    population = proposed_population
                    dof_dictionary = proposed_dof_dictionary
                    goals = proposed_goals
                    split_nodes = proposed_split_nodes
                    unused_nodes = proposed_unused_nodes
                    subgraph_partition = proposed_subgraph_partition

                    solution = True
                    count += 1
                    break

            if solution:
                break

        # If a valid plan is found, return it
        if district == district_num and check_population(population,
            goals[district_num - 1], population_deviation):
            return True, True, partitions, goals, district, population

# single_county_districts
# Add as many districts as possible where the district is fully contained within
# a county
def single_county_districts(partitions, pop_col, district, ideal_population, 
    population_deviation, level_conversions):

    single_dict = dict()

    for node in partitions[0].graph.nodes():
        county_population = partitions[0].graph.nodes[node][pop_col]

        # While additional full districts can fit within a county
        while True:

            # If the county is within epsilon of the ideal population, add the 
            # whole county to a single district
            if check_population(county_population, ideal_population, 
                population_deviation):
                partitions = flip_node(partitions, node, district, level, 
                    level_conversions)
                safe_add(single_dict, node, county_population)
                district += 1
                break

            # Otherwise if the county is larger than the ideal population, add a 
            # district the size of the ideal population to the county
            elif county_population > ideal_population:
                partitions = flip_node(partitions, node, district, level, 
                    level_conversions)              
                safe_add(single_dict, node, ideal_population)
                district += 1
                county_population -= ideal_population

            else:
                break
        
    return partitions, district, single_dict