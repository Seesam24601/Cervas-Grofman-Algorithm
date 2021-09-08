#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_map.py

Created by Charlie Murphy
19 August 2021

This file creates a single redistricting plan with n-1 county splits.
'''

from gerrychain.constraints import deviation_from_ideal
from gerrychain.proposals import recom_frack
from networkx import number_connected_components, connected_components
import random
from write_partition import write_to_csv

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
def new_county(partition, county_col, counties, district):
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
            if edge_counties[0] in counties:
                return edge_counties[1]
            elif edge_counties[1] in counties:
                return edge_counties[0]

# Use Recom
# Make use of the recom algorithm within gerrychain to split a county between
# two districts where each district is given a specified population within
# that county
def use_recom(partition, county_col, pop_col, county, districts, populations):
    
    locality_intersections = get_intersections(partition, county_col)

    county_subgraph = []

    # Create a subgraph of the nodes located within the county
    for locality in locality_intersections:
        if locality == county:
            for d in locality_intersections[locality]:
                for x in partition.parts[d]:
                    if partition.graph.nodes[x][county_col] == locality:
                        subgraph = partition.graph.subgraph(    
                            [x for x in partition.parts[d]
                            if partition.graph.nodes[x][county_col] == locality])
            
            for node in subgraph:
                if partition.assignment[node] == 1:
                    county_subgraph.append(subgraph.nodes)
                    break

    subgraph = partition.graph.subgraph(county_subgraph[0])

    # Remember to change when adding better population management
    epsilon = 0.1

    return recom_frack(partition, subgraph, districts, populations, pop_col, 
        epsilon)

# Check Contiguous
# Return true if no districts are split between multiple discontiguous parts
def check_contiguous(partition, districts_added):

    # Count the number of connected components
    pieces = 0
    for part, subgraph in partition.subgraphs.items():
        pieces += number_connected_components(subgraph)

    # Make sure the number of connected components is equal to the number of
    # districts
    return pieces == len(districts_added)

# Check Free Border
# Returns whether or not the district has a cut edge with an unused county
def check_free_border(partition, district):

    # If this is the last county split, return true regardless
    if district == 1:
        return True

    # Find a cut edge where one side is the specified district
    for edge in partition["cut_edges"]:
        edge_districts = (partition.assignment[edge[0]], 
            partition.assignment[edge[1]])

        # Return true if the other side of the cut edge is unused
        if edge_districts in [(1, district), (district, 1)]:
            return True
    
    # Return false if no such edge exists
    return False

# Districts and Populations
# This returns the pair of districts that should be split using recom and what
# population the portion of each district within the given county should have.
def districts_and_populations(districts, districts_added, full_districts, 
    next_district, county_population, remaining_population, ideal_population, 
    unused_county_population, return_population, i):

    # If this is the first split being made in this county
    if i == 0:

        # If the population of the county is less than the ideal population, 
        # then split the county between the current district and the next 
        # district.
        if full_districts == 0:
            print('A')
            recom_districts = (next_district, districts[0])
            districts.pop(0)
            districts_added.add(districts[0])
            populations = [county_population - remaining_population,
                remaining_population]
            return_population = 0

        # Otherwise, if population in the county leftover after adding as many
        # full districts as possible is less than the remaining population
        # needed to get the current district to the ideal population.
        elif (remaining_population >= county_population - (ideal_population 
            * full_districts)):

            # If the county can only fit one full district, add one full
            # district and give the rest of the county to the current district
            if full_districts == 1:
                print('B')
                recom_districts = (next_district, districts[0])
                districts_added.add(districts.pop(1))
                populations = [ideal_population, 
                    county_population - ideal_population]
                i = 1

            # Otherwise, first split the county between the portion of the 
            # county that is leftover and unused area.
            else:
                print('C')
                recom_districts = (1, districts[0])
                populations = [ideal_population * full_districts, 
                    county_population - (ideal_population * full_districts)]
            
            return_population += county_population - ideal_population

        # Otherwise, split the remaining population necessary to get the
        # current district to the ideal population and the unused area.
        else:
            print('D')
            recom_districts = (1, districts[0])
            districts.pop(0)
            districts_added.add(districts[0])
            populations = [unused_county_population - remaining_population, 
                remaining_population]
            return_population = 0

    # If this the final split in this county and the county has more than one
    # split, split between two additional districts, where one is a full 
    # district and the other is whatever population is left. If the county
    # is large enough for more than 1 full district and the remaining population
    # of the current district was larger than the leftover population in the 
    # county, this second district will also be a full district.
    elif i == full_districts:
        print('E')
        recom_districts = (next_district, next_district + 1)
        districts.remove(new_district)
        districts.remove(new_district + 1)
        districts_added.add(new_district)
        districts_added.add(new_district + 1)
        next_district += 2
        populations = [ideal_population, 
            unused_county_population - ideal_population]

    # Finally, split between an additional full district and the unused area.
    else:
        prit('F')
        recom_districts = (1, next_district)
        districts.remove(next_district)
        districts_added.add(next_district)
        populations = [unused_county_population - ideal_population,
            ideal_population]

    # Temporary until population properly implemented
    for i in range(2):
        if populations[i] <= 2000:
            populations[i - 1] -= 2000
            populations[i] += 2000
            
    print(populations)


    return (districts, districts_added, recom_districts, next_district, 
        populations, populations[0], return_population, i)

# Split County
# In the case where the remaining population necessary to get the current
# district to the ideal population is less than the population of the current
# county, introduce a county split using recom so that the current district is
# at the ideal population and with the remainder of the county start the next
# district. In the case of a county that is lare enough to contain one or more
# full districts, add those first.    
def split_county(partition, county_col, pop_col, county, districts,
    population, ideal_population, county_population, districts_added):

    # The population in the county that has yet to be assigned to a district
    unused_county_population = county_population

    # The population required to get the current district to the ideal
    #  population
    remaining_population = ideal_population - population

    # The population of the current district
    return_population = population

    # The number of full districts that can be added to a given county
    full_districts = county_population // ideal_population

    # The next district that has yet to be assigned any area at all
    next_district = districts[1]

    # Loop through all of the districts that will have land within this county
    for i in range(full_districts + 1):

        # Determine which districts to partition the unused portion of the 
        # county
        districts, districts_added, recom_districts, next_district, \
            populations, unused_county_population, return_population, i = \
            districts_and_populations(districts, districts_added,full_districts,
            next_district, county_population, remaining_population, 
            ideal_population, unused_county_population, return_population, i)

        # Split the county as determined
        tries = 0
        while True:
            tries += 1

            # Used recom to find a proposed partition of the county
            proposed_partition = use_recom(partition, county_col, pop_col, county, 
                recom_districts, populations) 

            # Accept the proposed partition if it keeps all districts contiguous
            # and any new districts added must have a cut edge that connects to
            # unused area.
            if (check_free_border(proposed_partition, next_district) and
                check_contiguous(proposed_partition, districts_added)):
                    partition = proposed_partition
                    break

            trymax = 25
            if tries > trymax:
                return False, None, proposed_partition, None

        # If the total number of districts being added is reached prematurely,
        # leave the loop
        if i == full_districts:
            break

        # Find the new next_district
        next_district += 1
   
    return True, return_population, partition, districts  

# Add the first county to the specified district
def first_county(partition, county_col, pop_col, counties, district):

    # Get nodes and population of first county
    nodes, county_population = get_county(partition, county_col, pop_col, 
        counties[-1], district)

    # Place the first county into the specified district
    partition = partition.flip(nodes)
    population = county_population

    return partition, population

# Create Map
# Create a single redistricting plan using the Cervas-Grofman algorithm
def create_map(partition, county_col, pop_col, starting_county, 
    pop_deviation_max, district_num, ideal_population):

    n = 0

    while True:
        n += 1
        print(n)
        validity, proposed_partition = create_partition(partition, county_col,
        pop_col, starting_county, pop_deviation_max, district_num, 
        ideal_population)

        name = 'test_25_' + str(n)
        write_to_csv(proposed_partition, 'GEOID20', 'assignment', 'Testing', 
            name)

        print()

        if validity:
            print(n)
            return proposed_partition

def create_partition(partition, county_col, pop_col, starting_county, 
    pop_deviation_max, district_num, ideal_population):

    # Create lists to keep track of which districts have been used
    districts = [i for i in range(2, district_num + 1)]
    districts.append(1)
    districts_added = {1, 2}

    # Get first county
    counties = [starting_county]
    partition, population = first_county(partition, county_col, pop_col, 
        counties, districts[0])

    # Remember to change when adding better population management
    epsilon = 0.01

    # Loop through every district except for the last one which will be created 
    # by the remaining vtds
    while True:

        # While the next county chosen is a full county
        while True:

            # While the population of the next county is less than the
            # population needed to get the current county to the ideal
            # population.
            split_needed = False
            tries = 0
            while True:
                tries += 1

                # Find the next county.
                counties.append(new_county(partition, county_col, counties, 
                    districts[0]))

                print(counties)

                # Get nodes and population of current county
                nodes, county_population = get_county(partition, county_col, pop_col, 
                    counties[-1], districts[0])
                proposed_partition = partition.flip(nodes)

                # Make sure that the doesn't split the unused area
                if check_contiguous(proposed_partition, districts_added):

                    # If the county is too large, a split is needed
                    if county_population > ideal_population - population:
                        split_needed = True
                    else:
                        partition = proposed_partition
                        population += county_population
                    break

                # If the county split the unused area, remove it and try again
                counties.pop()

                trymax = 10
                if tries > trymax:
                    return False, proposed_partition

            # If the population of this county would make the population of the 
            # district greater than the ideal population, leave the loop
            if split_needed:
                break

        # If the county must be split
        if (ideal_population * (1 + epsilon) < population or
            ideal_population * (1 - epsilon) > population):
            print('havana')

            validity, population, partition, districts = split_county(partition, 
                county_col, pop_col, counties[-1], districts, population, 
                ideal_population, county_population, districts_added)

            if not validity:
                return False, partition

            counties = [counties[-1]]

        # If the population is close enough, then don't require a county split
        else:
            print('cactoose')
            if districts != [district_num, 1]:
                population = 0
                old_counties = counties.copy()
                old_districts = districts.copy()
                old_districts_added = districts_added.copy()
                
                tries = 0
                while True:
                    tries += 1
                
                    # Add the current county
                    counties.append(new_county(partition, county_col, counties, 
                        districts[0]))
                    counties = [counties[-1]]
                    districts.pop(0)
                    districts_added.add(districts[0])
                    
                    # Add an adjacent county to the next district
                    proposed_partition, county_population = first_county(partition, 
                        county_col, pop_col, counties, districts[0])

                    # Make sure that the adjacent county does not split the 
                    # unused area
                    if check_contiguous(proposed_partition, districts_added):
                        partition = proposed_partition
                        population += county_population
                        break

                    # Otherwise, try a different county
                    counties = old_counties.copy()
                    districts = old_districts.copy()
                    districts_added = old_districts_added.copy()

                    trymax = 10
                    if tries > trymax:
                        return False, proposed_partition

            # If this is the last district, a split does not need to be made
            else:
                districts = []

        # If the corrct number of districts has been added, return the partition
        if districts == [] or districts == [1]:
            return True, partition
        

            

            
