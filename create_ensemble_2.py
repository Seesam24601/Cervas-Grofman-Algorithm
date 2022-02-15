#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_ensemble.py

Created by Charlie Murphy
17 December 2021

This file creates an ensemble of redistricting plans with n-1 county splits by
applying the Cervas-Groffman Algorithm.
'''

from create_clusters import create_clusters
from create_map import create_map
from discontiguous_counties import (correct_PA, check_contiguity, 
    muni_over_county, check_donuts)
import geopandas
from gerrychain import Graph
from make_partition import get_updaters, make_partition
import pickle
from reusable_data_2 import (get_ideal_population, get_starting_node, 
    get_county_subgraphs)
import time

from write_partition import write_to_csv, write_to_shapefile

# Update the recursion limit
# By default, Python has a recursion limit of around 1000. However, when 
# flipping nodes at the VTD level it is easy to exceed this because updating
# the cut edges and population are also achieved recursively
import sys
sys.setrecursionlimit(5000)

# Input Values
exec(open("input_template_2.py").read())

# Generate graphs if necessary
if new_graphs:
    exec(open("pickle_graph_2.py").read())

# Otherwise, Load graphs and flipped entitites
else:
    graph_list = pickle.load(open(graph_dump, "rb"))
    county_graph = graph_list[0]
    muni_graph = graph_list[1]
    vtd_graph = graph_list[2]

# Create initial partitions
my_updaters = get_updaters(pop_col)
county_partition = make_partition(county_graph, district_num, assignment_col, 
    my_updaters.copy())
muni_partition = make_partition(muni_graph, district_num, assignment_col,
    my_updaters.copy())
vtd_partition = make_partition(vtd_graph, district_num, assignment_col, 
    my_updaters.copy())

# Create relationships between levels
muni_to_county = get_county_subgraphs(county_graph, muni_graph, county_col)
vtd_to_county = get_county_subgraphs(county_graph, vtd_graph, county_col)
vtd_to_muni = get_county_subgraphs(muni_graph, vtd_graph, muni_col)
level_conversions = [muni_to_county, vtd_to_county, vtd_to_muni, muni_col]

# Get Set of Counties
counties = set(county_graph.nodes())

# Ideal Population
ideal_population = get_ideal_population(county_partition, district_num)

print(ideal_population)

# Population Deviation
population_deviation = ideal_population * epsilon

print(population_deviation)
print()

# Starting Node
starting_node = get_starting_node(county_graph, county_col, starting_county)

t0_all = t0 = time.time()
for i in range(runs):

    partition = create_map(county_partition, muni_partition, vtd_partition,
        county_col, muni_col, pop_col, starting_node, population_deviation, 
        district_num, ideal_population, dof_max, level_conversions, counties,
        assignment_col) 

    write_to_csv(partition, "GEOID20", "assignment", "Testing", "TEST48")

    t1 = time.time()

    #vtds_file = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2021 Data Set 2 Philly Removed\PA_2020_vtds.shp'
    #write_to_shapefile(partition, "assignment", vtds_file, "Testing", "TEST33")

    print(t1 - t0)
    print()

t1_all = time.time()
print("Total Time: ", t1_all - t0_all)
print("Average Time: ", (t1_all - t0_all) / runs)