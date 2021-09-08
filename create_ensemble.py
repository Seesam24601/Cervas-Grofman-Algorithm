#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_ensemble.py

Created by Charlie Murphy
19 August 2021

This file creates an ensemble of redistricting plans with n-1 county splits.
'''

from create_map import create_map, get_county
import geopandas
from gerrychain import Election, GeographicPartition, Graph, updaters
from write_partition import write_to_csv

# Input Values
exec(open("input_template.py").read())

# Add Blank Assignment
assignment_col = 'assignment'
data = geopandas.read_file(state_file)
data[assignment_col] = 1

# Add Other Districts
district = 2
for i in range(len(data[assignment_col])):

    if data[county_col][i] == starting_county:
        data[assignment_col][i] = district
        district += 1

        if district > district_num:
            break

# Create Graph
graph = Graph.from_geodataframe(data)

# Population Updater
my_updaters = {"population": updaters.Tally(pop_col, alias = "population")}

# Election Updater
elections = []
for election in election_cols:
    elections.append(Election(election, election_cols[election]))
my_updaters.update({election.name: election for election in elections})

# Cut Edges Updater
my_updaters.update({"cut_edges": updaters.cut_edges})

# Create Initial Partition
partition = GeographicPartition(graph, assignment = assignment_col,
    updaters = my_updaters)

# Ideal Population
ideal_population = int(sum(list(partition["population"].values())) 
    / len(partition))

# Create Map
partition = create_map(partition, county_col, pop_col, starting_county, 
    pop_deviation_max, district_num, ideal_population)

# Write to CSV
# Replace this with write_to_shapefile to write the results using a shapefile.
write_to_csv(partition, geoid_col, assignment_col, folder, 'test')

print("complete")