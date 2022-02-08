#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
pickle_graph.py

Created by Charlie Murphy
7 November 2021

This file pickles graph objects so that they can be used successively by the
algorithm without having to be regenerated.
'''

from fix_donuts import fix_donuts

# Load Data
data_county = geopandas.read_file(county_file)
data_vtd = geopandas.read_file(vtd_file)

# Fix Donuts
data_muni, data_vtd = fix_donuts(county_file, muni_file, vtd_file, 
    assignment_col, county_col, geoid_col, muni_col, name_col, pop_col, 
    geom_col)
data_muni = data_muni.reset_index()

# Add assignment column
data_county[assignment_col] = 1
data_muni[assignment_col] = 1
data_vtd[assignment_col] = 1

# Create Graphs
county_graph = Graph.from_geodataframe(data_county)
muni_graph = Graph.from_geodataframe(data_muni)
vtd_graph = Graph.from_geodataframe(data_vtd)

# Make sure that the precincts of every county are contiguous. This line is 
# specific to PA
vtd_graph = correct_PA(vtd_graph, geoid_col, assignment_col)

# Verify that municipalities and counties are made out contiguous districts
check_contiguity(vtd_graph, data_county, county_col, name_col)
check_contiguity(vtd_graph, data_muni, muni_col, name_col)
check_contiguity(muni_graph, data_county, county_col, name_col)
muni_over_county(muni_graph, muni_col, name_col)

# Create list of graphs
graph_list = [county_graph, muni_graph, vtd_graph]

# Pickle Graphs
pickle.dump(graph_list, open(graph_dump, 'wb'))
