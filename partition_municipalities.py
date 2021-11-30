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
from gerrychain import GeographicPartition
from networkx import number_connected_components
from partition_functions import (get_county_nodes, check_population, 
    add_to_assignment, check_contiguous, get_pieces, check_borders)
import random
from write_partition import write_to_shapefile

# partition_municipalities
# Continue to try to make valid municipality assignment dictionaries. If one can
# be created return it. If the maximum number of tries is found first, return
# a failure
def partition_municipalities(partition, muni_col, pop_col, epsilon, 
    county_assignments, muni_to_id, id_to_muni, muni_populations, muni_list,
    county_subgraphs, border_nodes, flipped_munis, max_tries, county_col,
    border_counties, donuts_muni, assignment_col, graph, partition_by_counties,
    border_edges, counties):

    # Flip all of the counties to district 1
    for muni in flipped_munis:
        partition = partition.flip({muni_to_id[muni] : 1})
    
    # Add unsplit counties to the partition
    muni_assignments, partition, districts_used, counties_visited = \
        add_unsplit_counties(partition, county_assignments, county_subgraphs, 
        id_to_muni, muni_populations)

    # Loop through the counties that need to be split and split them by 
    # municipaliti
    for county in county_assignments:
        if len(county_assignments[county]) != 1:

            # Add the current county to the set of counties that have been
            # partitioned
            counties_visited.add(county)

            # Create a graph only of the current county with each node 
            # representing a municipality
            current_graph = graph.subgraph(county_subgraphs[county])

            # If there is only one municipality in the county, remove the county
            # from the list of counties that have been partitioned and restart
            # the loop with the next county
            if len(current_graph.nodes()) <= len(county_assignments[county]):
                counties_visited.remove(county)
                continue

            # Create a partition of the graph of the current county that is
            # capable of handling the correct districts
            i = 0
            for node in current_graph.nodes():
                current_graph.nodes()[node][assignment_col] = \
                    county_assignments[county][i][0]  
                i += 1   
                if i >= len(county_assignments[county]):
                    break
            current_partition = GeographicPartition(current_graph, 
                assignment = assignment_col)

            # Return the district of every municipality to 1 (unassigned)
            for node in current_partition.graph.nodes():
                current_partition = current_partition.flip({node : 1})

            # Attempt to partition the current county max_tries number of times
            for count in range(max_tries):
                validity, proposed_muni_assignments, \
                    proposed_districts_used, proposed_partition = attempt_muni_partition(
                    current_partition, 
                    deepcopy(muni_assignments), county, 
                    county_assignments[county], border_edges, muni_to_id, 
                    id_to_muni, muni_populations, epsilon, copy(districts_used),
                    county_col, county_assignments, border_counties, 
                    donuts_muni, partition, border_nodes, counties_visited)

                # If a valid partition is found, make sure that it is
                # contiguous with respect to the rest of the map. If so,
                # accept the partition
                if validity:

                    solution = check_all_borders(proposed_partition, border_edges, 
                        county_col, county, county_assignments, border_counties,
                        counties, counties_visited)

                    if solution:
                        muni_assignments = proposed_muni_assignments
                        districts_used = proposed_districts_used
                        partition = proposed_partition
                        break

            # If no such partition is found, return a failure to find a
            # partition for the current county and thus for the given
            # county_assignments
            if not validity or not solution:
                return False, muni_assignments

    return True, muni_assignments

# add_unsplit_counties
# For every county that is not split, add the unsplit county both to the
# partition and to the muni_assignmentSSs dictionary
def add_unsplit_counties(partition, county_assignments, county_subgraphs,
    id_to_muni, muni_populations):

    muni_assignments = dict()
    districts_used = set()
    counties_visited = set()

    # Loop through the un-split counties
    for county in county_assignments:
        if len(county_assignments[county]) == 1:
            nodes = county_subgraphs[county]
            district = county_assignments[county][0][0]
            districts_used.add(district)
            counties_visited.add(county)

            # Add municipalities to muni_assignment
            for muni in nodes:
                muni_assignments[id_to_muni[muni]] = [(district, 
                    muni_populations[id_to_muni[muni]])]

            # Add municipalities to partition
            partition = partition.flip(get_county_nodes(nodes, district))
    
    return muni_assignments, partition, districts_used, counties_visited

# attempt_muni_partition
# Loop through each split county and for each one partition between 
# municipalities
def attempt_muni_partition(partition, muni_assignments, county, districts, 
    border_edges, muni_to_id, id_to_muni, muni_populations, epsilon, 
    districts_used, county_col, county_assignments, border_counties,
    donuts_muni, full_partition, border_nodes, counties_visited):

    districts_used = set()

    # Find the first district to add to the current county
    index = 0
    index_max = len(districts) - 1
    if districts[index][0] == 1:
        index += 1

    population = 0
    final_ideal_population = districts[index_max][1]
    munis = []

    # Select the first municipality to be added. Consider using a more
    # efficient edge representation
    start_muni = get_start_muni(county, border_nodes, id_to_muni, 
        districts[index][0], full_partition.graph.edges(), county_assignments, 
        full_partition, county_col)

    # Add the first municipality to the partition and muni_assignments
    while index <= index_max and munis == []:
        validity, partition, munis, muni_assignments, index, population, \
            districts_used, dof_dictionary, full_partition = add_muni(partition, 
            muni_assignments, start_muni, muni_to_id, id_to_muni, index, 
            population, districts, muni_populations, epsilon, munis, 
            districts_used, donuts_muni, {}, 0, full_partition)

    # If every district has already been partitioned, return true since only
    # municipality needed to be changed.
    if index >= index_max:
        counties_visited.remove(county)
        return True, muni_assignments, districts_used, full_partition

    # Continue adding municipalities until every district has enough population
    # allocated to it.
    count = 0
    while True:
        count += 1

        # Find the unallocated counties that border the current district
        solution = False
        bordering_munis = get_next_muni(partition, munis, 
            muni_to_id, id_to_muni, districts[index][0], county, county_col,
            dof_dictionary)

        # Prioritize adding municipalities that have a lower DOF. This means 
        # prioritizing municipalities that have a pathway of fewer edges to the
        # first municipality added to a given district 
        for dof in range(50):
            if dof not in bordering_munis:
                if dof == 49:
                    return False, None, None, None
                continue

            # Shuffle the unassigned municipalities with a given number of DOF
            max_length_keys = list(bordering_munis[dof])
            random.shuffle(max_length_keys)

            # For each bordering county, try to add it to the plan
            for key in max_length_keys:
                muni = id_to_muni[key]

                # Attempt to add the municipality
                validity, proposed_partition, proposed_munis, proposed_muni_assignments, \
                    proposed_index, proposed_population, proposed_districts_used, \
                    proposed_dof_dictionary, proposed_full_partition = add_muni(
                    partition, 
                    deepcopy(muni_assignments), muni, 
                    muni_to_id, id_to_muni, index, population, districts,
                    muni_populations, epsilon, copy(munis), districts_used, 
                    donuts_muni, copy(dof_dictionary), dof, full_partition)

                # Check whether this addition preserves the contiguity of the
                # plan. Note: may be issue when district = 1
                if validity and unused_contiguous(proposed_partition):
                    partition = proposed_partition
                    munis = proposed_munis
                    muni_assignments = proposed_muni_assignments
                    index = proposed_index
                    population = proposed_population
                    districts_used = proposed_districts_used
                    dof_dictionary = proposed_dof_dictionary
                    full_partition = proposed_full_partition
                    solution = True
                    break

            # If a solution is found, break out of the loop of bordering 
            # municipalities
            if solution:
                break

        # If the current district is 1 (unassigned), proceed to allocating the
        # next district
        if districts[index][0] == 1:
            index += 1

        # If every district has been allocated with enough population, 
        # return the partition
        if index >= index_max and check_population(population,
            final_ideal_population, epsilon):

            # For any remaining unassigned municipalities within the district,
            # assign to the district with the greatest population within the 
            # county
            full_partition = clean_muni_assignments(muni_assignments, partition, 
                districts[index][0], muni_populations, id_to_muni, 
                full_partition)

            return True, muni_assignments, districts_used, full_partition

# clean_muni_assignments
# For any remaining unassigned municipalities within the district, assign to the 
# district with the greatest population within the county
def clean_muni_assignments(muni_assignments, partition, district,
    muni_populations, id_to_muni, full_partition):

    # Loop through every partition in the given county
    for node in partition.graph.nodes():
        if partition.assignment[node] == 1:

            # Add every unallocated municipality to the district with the 
            # largest population within the county.
            muni = id_to_muni[node]
            add_to_assignment(muni_assignments, muni, district, 
                muni_populations[muni])
            full_partition = full_partition.flip({node : district})

    return full_partition

# get_start_muni
# Find a municipality within the county that shares a border with a county that
# also contains the first district
def get_start_muni(county, border_nodes, id_to_muni, district, edges, 
    county_assignments, partition, county_col):
    result = False

    # Continue to search until such a municpalitiy is found
    while not result:

        # Select a random border node
        start = random.choice(border_nodes[county])

        # Find every possible edge from the given node
        for edge in edges:
            for i in range(2):
                if start == edge[i]:

                    # If that edge goes between counties and the given district
                    # can be found in the county not containing the selected 
                    # starting municipality, return the starting municipality
                    edge_county = partition.graph.nodes()[edge[i - 1]][county_col]
                    if edge_county != county:
                        for pair in county_assignments[edge_county]:
                            if district == pair[0]:
                                result = True

    return id_to_muni[start]                   

# add_mnui
# Add a given municipality to the partition and muni_assignments
def add_muni(partition, muni_assignments, muni, muni_to_id, id_to_muni, index, 
    population, districts, muni_populations, epsilon, munis, districts_used, 
    donuts_muni, dof_dictionary, dof_effect, full_partition):

    # Get additional data about where the municipality is being assigned
    muni_id = muni_to_id[muni]
    district = districts[index][0]
    districts_used.add(district)
    ideal_population = districts[index][1]

    # Find the population of the municipality, subtracting any partial 
    # population that has already been allocated
    muni_population = muni_populations[muni]
    if muni in muni_assignments:
        for assignment in muni_assignments[muni]:
            muni_population -= assignment[1]

    # If the municipality is a donut municipality, add the population of all of
    # its associated donut holes.
    donut = False
    if muni_id in donuts_muni:
        donut = True
        for donut_hole in donuts_muni[muni_id]:
            muni_population += muni_populations[id_to_muni[donut_hole]]

    # If the current district is within epsilon of the ideal population, begin 
    # allocating the next district recursively.
    if check_population(population, ideal_population, epsilon):
        index += 1
        population = 0
        munis = []
        dof_dictionary = dict()

        validity, partition, munis, muni_assignments, index, population, \
            districts_used, dof_dictionary, full_partition = add_muni(partition,
            muni_assignments, muni, muni_to_id, id_to_muni, index, population, 
            districts, muni_populations, epsilon, munis, districts_used, 
            donuts_muni, dof_dictionary, 0, full_partition)

        if not validity:
            return False, None, None, None, None, None, None, None

    # If the current municipality needs to be split, attempt to do so.
    elif muni_population > (ideal_population * (1 + epsilon) - population):
        add_to_assignment(muni_assignments, muni, district, 
            ideal_population - population)

        # If the municipality is a donut municipality, it cannot be split and 
        # thus said municipality cannot be added
        if donut:
            return False, None, None, None, None, None, None, None, None

        # Otherwise split the municipality such that the current district is 
        # within epsilon of its ideal population and recursively add the 
        # remaining population of the municipality to the next district.
        muni_population = muni_population - (ideal_population - population)
        partition = partition.flip({muni_id : district})
        full_partition = full_partition.flip({muni_id : district})
        index += 1
        population = 0
        munis = []
        dof_dictionary = dict()

        validity, partition, munis, muni_assignments, index, population, \
            districts_used, dof_dictionary, full_partition = add_muni(partition, muni_assignments, muni, 
            muni_to_id, id_to_muni, index, population, districts, 
            muni_populations, epsilon, munis, districts_used, donuts_muni, 
            dof_dictionary, 0, full_partition)
        
        if not validity:
            return False, None, None, None, None, None, None, None, None
    
    # Otherwise, add the entirity of the municipality to the give district
    else:
        population += muni_population
        munis.append(muni_id)
        dof_dictionary[muni_id] = dof_effect
        if not donut: 
            add_to_assignment(muni_assignments, muni, district, muni_population)
        partition = partition.flip({muni_id : district})
        full_partition = full_partition.flip({muni_id : district})

        # If the municipality is a donut municipality, also add of it's
        # associated donut holes
        if donut:
            add_to_assignment(muni_assignments, muni, district, 
                muni_populations[muni])
            for donut_hole in donuts_muni[muni_id]:
                munis.append(donut_hole)
                add_to_assignment(muni_assignments, id_to_muni[donut_hole], 
                    district, muni_populations[id_to_muni[donut_hole]])
                partition = partition.flip({donut_hole : district})
                full_partition = full_partition.flip({donut_hole : district})

    return (True, partition, munis, muni_assignments, index, population, 
        districts_used, dof_dictionary, full_partition)

# get_next_muni
# Given the current municipality, find the set of unallocated municipalities
# within the current county and organize them by DOF.
def get_next_muni(partition, munis, muni_to_id, id_to_muni, district, county,
    county_col, dof_dictionary):

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

            for i in range(2):
                if edge[i] in munis:
                    index = dof_dictionary[edge[i]] + 1
                    if index not in bordering_munis:
                        bordering_munis[index] = set()
                    bordering_munis[index].add(edge[i - 1])
                    break

    return bordering_munis

# unused_continguous
# Return whether or not the unallocated municipalities are contiguous within the
# given partition
def unused_contiguous(partition):
    for part, subgraph in partition.subgraphs.items():
        if (part == 1 and 
            number_connected_components(subgraph) != 1): 
            return False
    return True

# check_all_borders
# Check that all borders within a given county meet the requirements in 
# county_assignments such that a valid partition of the entire map is possible
def check_all_borders(partition, border_edges, county_col, county, 
    county_assignments, border_counties, counties, counties_visited):

    # Find the counties that border the given county
    for pair in border_counties:
        for i in range(2):
            if county == pair[i] and pair[i - 1] in counties_visited:

                # For each bordering county, check to see if there exists a
                # district within both the county and the bodering county
                if pair[i - 1] in county_assignments:
                    for d1 in county_assignments[pair[i - 1]]:
                        for d2 in county_assignments[county]:
                            if d1[0] == d2[0]:

                                # If such a district exists, check that there
                                # is a valid border between them
                                if not check_borders(partition, border_edges, 
                                    county_col, d1[0], county, pair[i - 1],
                                    counties):
                                        return False

    return True 