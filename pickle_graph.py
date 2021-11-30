#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
pickle_graph.py

Created by Charlie Murphy
7 November 2021

This file pickles graph objects so that they can be used successively by the
algorithm without having to be regenerated.
'''

# Add Blank Assignment
data_county = geopandas.read_file(county_file)
data_muni = geopandas.read_file(muni_file)
data_vtd = geopandas.read_file(vtd_file)

# Add Districts to data_county
data_county, flipped_counties = add_districts(data_county, assignment_col,
    county_col, district_num)

# Add Districts to data_muni
data_muni, flipped_munis = add_districts(data_muni, assignment_col, muni_col,
    district_num)

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

# Pickle Graphs
pickle.dump(county_graph, open(county_graph_dump, 'wb'))
pickle.dump(muni_graph, open(muni_graph_dump, 'wb'))
pickle.dump(vtd_graph, open(vtd_graph_dump, 'wb'))

# Pickle Flipped Dictionaries
pickle.dump(flipped_counties, open(flipped_counties_dump, 'wb'))
pickle.dump(flipped_munis, open(flipped_munis_dump, 'wb'))