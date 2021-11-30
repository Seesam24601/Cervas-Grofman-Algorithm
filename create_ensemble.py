#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_ensemble.py

Created by Charlie Murphy
19 August 2021

This file creates an ensemble of redistricting plans with n-1 county splits by
applying the Cervas-Groffman Algorithm.
'''

"""
Border munis is adding duplicate municiplaities? 
What prevents this for counties?
How to fix?
"""

from discontiguous_counties import (correct_PA, check_contiguity, 
    muni_over_county, check_donuts)
import geopandas
from gerrychain import Election, GeographicPartition, Graph, updaters
from partition_counties import partition_counties
from partition_functions import add_districts
from partition_municipalities import partition_municipalities
import pickle
from reusable_data import reusable_data
from split_counties import split_counties
from write_partition import write_to_csv, write_to_shapefile
import time

# Input Values
exec(open("input_template.py").read())

# Generate graphs if necessary
if new_graphs:
    exec(open("pickle_graph.py").read())

# Otherwise, Load graphs and flipped entitites
else:
    county_graph = pickle.load(open(county_graph_dump, "rb"))
    muni_graph = pickle.load(open(muni_graph_dump, "rb"))
    vtd_graph = pickle.load(open(vtd_graph_dump, "rb"))
    flipped_counties = pickle.load(open(flipped_counties_dump, "rb"))
    flipped_munis = pickle.load(open(flipped_munis_dump, "rb"))

# Population Updater
my_updaters = {"population": updaters.Tally(pop_col, alias = "population")}

# Cut Edges Updater
my_updaters.update({"cut_edges": updaters.cut_edges})

# Create Initial Partitions
county_partition = GeographicPartition(county_graph, assignment = assignment_col,
    updaters = my_updaters)
muni_partition = GeographicPartition(muni_graph, assignment = assignment_col,
    updaters = my_updaters)
test_p = muni_partition
vtd_partition = GeographicPartition(vtd_graph, assignment = assignment_col,
    updaters = my_updaters)

partition_by_counties = GeographicPartition(muni_graph, 
    assignment = county_col, updaters = my_updaters)

# Ideal Population
ideal_population = int(sum(list(county_partition["population"].values())) 
    / len(county_partition))

# Get Reusable Data
county_to_id, id_to_county, muni_to_id, id_to_muni, border_muni, border_county, \
    border_edges, border_nodes, county_populations, counties, \
    muni_populations, munis, county_subgraphs, muni_subgraphs, border_edges_county = \
    reusable_data(county_graph, muni_graph, vtd_graph, county_col, muni_col, 
    pop_col)

donuts_muni = check_donuts(muni_graph, counties, county_subgraphs, 
    assignment_col)

print("ARGO")

# Create Map
t0_all = t0 = time.time()
for i in range(runs):

    while True:
        county_assignments = partition_counties(county_partition, county_col, 
            pop_col, starting_county, flipped_counties, epsilon, district_num, 
            ideal_population, county_to_id, id_to_county, county_populations,
            counties)
      

        validity, muni_assignments = partition_municipalities(muni_partition,
            muni_col, pop_col, epsilon, county_assignments, muni_to_id,
            id_to_muni, muni_populations, munis, county_subgraphs, border_nodes,
            flipped_munis, max_tries, county_col, border_county, donuts_muni,
            assignment_col, muni_graph, partition_by_counties, 
            border_edges_county, counties)

        if not validity:
            continue

        print(muni_assignments)
        print(len(muni_assignments))
        print(validity)

        t1 = time.time()
        print(t1 - t0)
        print()

        for muni in muni_assignments:
            if len(muni_assignments[muni]) == 1:
                test_p = test_p.flip({muni_to_id[muni] : muni_assignments[muni][0][0]})
            else:
                print(muni)
        print()

        vtd_file = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2021 Data Set 2 Edited\PA_2020_muni.shp'
        write_to_shapefile(test_p, "assignment", vtd_file, "Testing", 
            "MUNI_2_" + str(len(muni_assignments)))

        print("DONE")
        input()

        if not validity:
            continue

        validity, proposed_partition = split_counties(vtd_partition, muni_col, 
            pop_col, muni_assignments, epsilon, border_muni,
            border_edges, muni_populations, muni_subgraphs, max_tries)
        input()
        if validity:
            solution = True
            break

    if solution:
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