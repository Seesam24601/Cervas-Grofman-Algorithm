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
import pandas

# Input Values
exec(open("input_template.py").read())

# Add Blank Assignment
assignment_col = 'assignment'
data = geopandas.read_file(state_file)
data[assignment_col] = 1

# Add Other Districts
for district in range(2, district_num + 1):
    data.loc[:, (assignment_col, district)] = district

# Create Graph
graph = Graph.from_geodataframe(data)

# Population Updater
my_updaters = {"population": updaters.Tally(pop_col, alias = "population")}

# Election Updater
elections = []
for election in election_cols:
    elections.append(Election(election, election_cols[election]))
my_updaters.update({election.name: election for election in elections})

# Create Initial Partition
partition = GeographicPartition(graph, assignment = assignment_col,
    updaters = my_updaters)

# Ideal Population
ideal_population = sum(list(partition["population"].values())) / len(partition)

###
partition = create_map(partition, county_col, pop_col, starting_county, 
    pop_deviation_max, district_num, ideal_population)

# Write to CSV
plan = pandas.DataFrame(partition.graph.data[geoid_col])
plan[assignment_col] = partition.assignment.to_series()
filename = './Ensembles/' + folder + '/test.csv'
plan.to_csv(filename, index = False)

# Write to Shapefile
vtds = geopandas.read_file(r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\TIGER\tl_2020_42_vtd20.shp')
vtds[assignment_col] = partition.assignment.to_series()
filename = './Ensembles/' + folder + '/test.shp'
vtds.to_file(filename, index = False)

print("complete")