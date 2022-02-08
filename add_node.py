#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
add_node.py

Created by Charlie Murphy
17 December 2021

This file adds a node in a given graph to the correct district.
'''

from partition_functions_2 import check_population, get_split_nodes
import random

from write_partition import write_to_shapefile, write_to_csv

# add_node
# Add a given node to the partition according to the current population of the
# district and it's ideal_population
def add_node(partitions, node, district, population, goals, pop_col, 
    dof_dictionary, dof_effect, single_dict, population_deviation, nodes, 
    district_num, level, level_conversions, county_col, muni_col, dof_max,
    subgraph_population, allowed_nodes, split_nodes, unused_nodes, 
    subgraph_partition, assignment_col):

    # Calculate Ideal Population
    ideal_population = goals[district - 1]

    # Remove the population of any districts fully contained in the node from
    # the node population used for the below calculations
    node_population = partitions[level].graph.nodes[node][pop_col]
    if node in single_dict:
        node_population -= single_dict[1]

    # If the current district is at the ideal population, put the entirity of the
    # node in a new district
    if check_population(population, ideal_population, population_deviation):
        district += 1
        dof_dictionary = {node : 0}
        nodes = set()

        # If the program is not at the county level, the current district is
        # within epsilon of the ideal_popultion, and the population goal of the
        # next district is greater than the remaining population in the
        # subgraph, add the remaining population in the subgraph to the next
        # district
        if (level != 0 and 
            goals[district - 1] > subgraph_population - population):

            # Get the current population of the next district
            population = subgraph_population - population

            # Allocate the rest of the nodes in the subgraph
            for node in unused_nodes:
                partitions = flip_node(partitions, node, district, level, 
                    level_conversions)

            # Update unused nodes to reflect that all nodes have been 
            # allocated
            unused_nodes = set()

            return (True, True, partitions, nodes, district, population, 
                dof_dictionary, goals, split_nodes, unused_nodes, subgraph_partition)

        else:
            population = 0
            validity, completition, partitions, nodes, district, population, \
                dof_dictionary, goals, split_nodes, unused_nodes, \
                subgraph_partition = add_node(partitions, node, district, 
                population, goals, pop_col, dof_dictionary, 0, single_dict, 
                population_deviation, nodes, district_num, level, 
                level_conversions, county_col, muni_col, dof_max, 
                subgraph_population, allowed_nodes, split_nodes, unused_nodes, 
                subgraph_partition, assignment_col)

            if not validity:
                return (False, False, None, None, None, None, None, None, None, 
                    None, None)

    # If the population remaining to get the current district to the ideal 
    # population is less than the node population, split the node between
    # the current distrit and the new one such that the current district is at
    # the ideal population.
    elif node_population + population > ideal_population + population_deviation:

        # Cannot split VTDs
        if level == 2:
            return (False, False, None, None, None, None, None, None, None, 
                None, None)

        # Calculate the remaining population
        remaining_population = ideal_population - population

        # Get the list of nodes that have been split and thus need to be 
        # given additional consideration to ensure continuity
        get_split_nodes(partitions, level, split_nodes, node)

        # Call Step Down
        validity, partitions, district, population, nodes = step_down(partitions, 
            county_col, muni_col, pop_col, population_deviation, district_num, 
            goals, dof_max, district, level, level_conversions, 
            remaining_population, node, ideal_population, node_population,
            population, split_nodes, assignment_col)

        if not validity:
            return (False, False, None, None, None, None, None, None, None, 
                None, None)

        # Update dof_dictionary and unused nodes list
        dof_dictionary = {node : 0}
        unused_nodes.remove(node)

    # If the population needed for the district to be at the ideal population
    # is greater than or equal to the node population, place the entire
    # node in the current district.
    else:
        population += node_population
        dof_dictionary[node] = dof_effect
    
        # Update the nodes list, unused nodes list and partition accordingly
        nodes.add(node)
        unused_nodes.remove(node)
        partitions = flip_node(partitions, node, district, level, 
            level_conversions)

        # If not at county level, add the node to the partition of just the
        # current outer node
        if level!=0:
            subgraph_partition = subgraph_partition.flip({node : district})

    return (True, False, partitions, nodes, district, population, 
        dof_dictionary, goals, split_nodes, unused_nodes, subgraph_partition)

# flip_node
# Flip the node and all sub-nodes at lower levels
def flip_node(partitions, node, district, level, level_conversions):
    
    # County Level
    if level == 0:

        # County
        partitions[0] = partitions[0].flip({node : district})

        # Municipalities within County
        for muni_node in level_conversions[0][node]:
            partitions[1] = partitions[1].flip({muni_node : district})

        # Update updaters to avoid recursion issues
        partitions[1]["cut_edges"]
        partitions[1]["population"]

        # VTDs within County
        for vtd_node in level_conversions[1][node]:
            partitions[2] = partitions[2].flip({vtd_node : district})
            
            # Update updaters to avoid recursion issues
            partitions[2]["cut_edges"]
            partitions[2]["population"]
    
    # Muni Level
    if level == 1:

        # Municipality
        partitions[1] = partitions[1].flip({node : district})

        # VTDs within County
        for vtd_node in level_conversions[2][node]:
            partitions[2] = partitions[2].flip({vtd_node : district})

            # Update updaters to avoid recursion issues
            partitions[2]["cut_edges"]
            partitions[2]["population"]

    # VTD Level
    if level == 2:

        # VTDs
        partitions[2] = partitions[2].flip({node : district})

    return partitions

# step_down
# This function allows the program to go down to another level to split either
# a municipality or county where necessary to maintain population balance.
def step_down(partitions, county_col, muni_col, pop_col, population_deviation, 
    district_num, goals, dof_max, district, level, level_conversions, 
    remaining_population, node, ideal_population, node_population, 
    current_population, split_nodes, assignment_col):

    # Create the new goals for the program while at the lower levels
    goals = new_goals(goals, district, district_num, remaining_population)
    goals_copy = goals.copy()

    # Determine which nodes at the lower level are within the current nodes and
    # only allow them
    if level == 0:
        allowed_nodes = level_conversions[0][node]
    else:
        allowed_nodes = level_conversions[2][node]

    # Move to the lower level and find a starting node
    level += 1
    starting_node = get_first_node(partitions[level], allowed_nodes, district)

    while True:

        # Run the algorithm on the subset of the lower level determined by 
        # allowed_nodes
        import create_map
        validity, completition, proposed_partitions, proposed_goals,  \
            proposed_district, proposed_population =  \
            create_map.attempt_map(partitions, county_col, muni_col, pop_col, 
            starting_node, population_deviation, district_num, goals, dof_max, 
            district, dict(), level, level_conversions, allowed_nodes, 
            node_population, split_nodes, assignment_col)

        # If the attempt at the lower level is successful
        if validity:

            partitions = proposed_partitions
            goals = proposed_goals
            district = proposed_district
            population = proposed_population

            # Jump back to the higher level
            level -= 1

            # CHANGE THIS!!!
            partitions[level] = partitions[level].flip({node : district})
            nodes = {node}

            # Update the goals to reflect the changes made at the lower level
            remaining_population = ideal_population - population

            # If the entire map is finished, then update the population of the 
            # final district at the county level to reflect that fact
            if completition:
                population = population + current_population

            return True, partitions, district, population, nodes

        # If it is not, throw an error. This needs additional updating.
        else:
            write_to_csv(partitions[2], "GEOID20", "assignment", "Testing", "TEST_ERROR")
            print("ERROR: add_node line 222")
            return False, None, None, None, None

# new_goals
# Create a new goals list when stepping down
def new_goals(old_goals, district, district_num, remaining_population):
    goals = []
    for i in range(district_num):

        # For districts that have already been aportioned, the goal population
        # is 0
        if i < district - 1:
            goals.append(0)

        # For the current district, the goal population is the current 
        # population
        elif i == district - 1:
            goals.append(remaining_population)

        # For districts that have not be aportioned yet, the goal population 
        # remains the same
        else:
            goals.append(old_goals[i])

    return goals

# get_first_node
# Return a randomized node when stepping down that maintains the contiguity of 
# the district.
def get_first_node(partition, allowed_nodes, district):

    # Create set of all valid first nodes
    bordering_nodes = []
   
    # Loop through the cut edges
    for edge in partition["cut_edges"]:

        # If an edge exists between the current district and an unallocated 
        # allowed nodes, add said node the set of valid first nodes
        for i in range(2):
            if (edge[i - 1] in allowed_nodes 
                and partition.assignment[edge[i - 1]] == 1
                and partition.assignment[edge[i]] == district):
                bordering_nodes.append(edge[i - 1])

    if bordering_nodes == []:
        print("BAM!")
        return get_first_node(partition, allowed_nodes, district - 1)

    # Return a random valid first node          
    return random.choice(bordering_nodes)