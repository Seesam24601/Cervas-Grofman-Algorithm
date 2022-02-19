#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
write_partition.py

Created by Charlie Murphy
26 August 2021

This file contains functions that can write a partition either to a shapefile 
or to a CSV that can be opened by DRA.
'''

import geopandas
import pandas
from reusable_data_2 import get_county_subgraphs

# write_to_csv
# Creates a CSV file in the specified subfolder of the Ensembles folder that 
# contains a mapping from GEOID to district assignment. This CSV can be
# used in DRA.
def write_to_csv(partition, geoid_col, assignment_col, folder, name):
    plan = pandas.DataFrame(partition.graph.data[geoid_col])
    plan[assignment_col] = partition.assignment.to_series()
    filename = './Ensembles/' + folder + '/' + name + '.csv'
    plan.to_csv(filename, index = False)

# write_to_shapefile
# Creates a Shapefile in the specified subfolder of the Ensembles folder that
# includes a field with the district assignment. Note that this method is both
# slower and creates more file clutter than the CSV version.
def write_to_shapefile(partition, assignment_col, vtds_file, folder, name):
    vtds = geopandas.read_file(vtds_file)
    vtds[assignment_col] = partition.assignment.to_series()
    filename = './Ensembles/' + folder + '/' + name + '.shp'
    vtds.to_file(filename, index = False)

# write_counties_to_csv
# This converts a partition at the county level to one at the VTD level so that
# it can be saved to a CSV that can be viewed in DRA.
def write_counties_to_csv(county_partition, vtd_partition, geoid_col, county_col,
    assignment_col, folder, name):

    subgraphs = get_county_subgraphs(county_partition.graph, 
        vtd_partition.graph, county_col)

    for node in county_partition.graph.nodes():
        district = county_partition.assignment[node]
        if district != 1:
            for vtd_node in subgraphs[node]:
                vtd_partition = vtd_partition.flip({vtd_node: district})

    write_to_csv(vtd_partition, geoid_col, assignment_col, folder, name)
