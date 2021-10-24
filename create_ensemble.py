#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_ensemble.py

Created by Charlie Murphy
19 August 2021

This file creates an ensemble of redistricting plans with n-1 county splits by
applying the Cervas-Groffman Algorithm.
'''

from discontiguous_counties import correct_PA
import geopandas
from gerrychain import Election, GeographicPartition, Graph, updaters
from partition_counties import partition_counties
from reusable_data import reusable_data
from split_counties import split_counties
from write_partition import write_to_csv
import time

# Input Values
exec(open("input_template.py").read())

# Add Blank Assignment
assignment_col = 'assignment'
data_county = geopandas.read_file(county_file)
data_vtd = geopandas.read_file(vtd_file)

# Add Districts to data_county
data_county[assignment_col] = 1
district = 2
flipped_counties = set()
for i in range(len(data_county[assignment_col])):
    flipped_counties.add(data_county[county_col][i])
    data_county[assignment_col][i] = district
    district += 1
    if district > district_num:
        break

# Add Districts to data_vtd
data_vtd[assignment_col] = 1
district = 2
for i in range(len(data_vtd[assignment_col])):
    if data_vtd[county_col][i] == starting_county:
        data_vtd[assignment_col][i] = district
        district += 1
        if district > district_num:
            break

# Make sure that all the districts were added
if district != district_num + 1:
    print("WARNING: Starting county did not contain enough precincts")

# Create Graphs
county_graph = Graph.from_geodataframe(data_county)
vtd_graph = Graph.from_geodataframe(data_vtd)

# Make sure that the precincts of every county are contiguous. This line is 
# specific to PA
vtd_graph = correct_PA(vtd_graph, geoid_col, assignment_col)

# Population Updater
my_updaters = {"population": updaters.Tally(pop_col, alias = "population")}

# Cut Edges Updater
my_updaters.update({"cut_edges": updaters.cut_edges})

# Create Initial Partitions
county_partition = GeographicPartition(county_graph, assignment = assignment_col,
    updaters = my_updaters)
vtd_partition = GeographicPartition(vtd_graph, assignment = assignment_col,
    updaters = my_updaters)

# Ideal Population
ideal_population = int(sum(list(county_partition["population"].values())) 
    / len(county_partition))

county_to_id, id_to_county, county_list, border_counties, border_edges, \
    county_populations, county_subgraphs  = reusable_data(county_graph, 
    vtd_graph, county_col, pop_col)

# Create Map
t0_all = t0 = time.time()
for i in range(runs):

    count = 0
    while True:
        county_assignments = partition_counties(county_partition, county_col, 
            pop_col, starting_county, flipped_counties, epsilon, district_num, 
            ideal_population, county_to_id, id_to_county, county_populations,
            county_list)
        
        count += 1

        validity, proposed_partition = split_counties(vtd_partition, county_col, 
            pop_col, county_assignments, epsilon, border_counties,
            border_edges, county_populations, county_subgraphs, max_tries)
        if validity:
            break

    # Write to CSV
    # Replace this with write_to_shapefile to write the results using a shapefile.
    write_to_csv(proposed_partition, geoid_col, assignment_col, folder, 
        filename + "_" + str(i))

    # Print Time 
    t1 = time.time()
    print(t1 - t0)
    t0 = t1

t1_all = time.time()
print()
print("Total Time: ", t1 - t0_all)
print("Average Time: ", (t1_all - t0_all) / runs)