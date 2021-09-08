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

# Creates a CSV file in the specified subfolder of the Ensembles folder that 
# contains a mapping from GEOID to district assignment. This CSV can be
# used in DRA.
def write_to_csv(partition, geoid_col, assignment_col, folder, name):
    plan = pandas.DataFrame(partition.graph.data[geoid_col])
    plan[assignment_col] = partition.assignment.to_series()
    filename = './Ensembles/' + folder + '/' + name + '.csv'
    plan.to_csv(filename, index = False)

# Creates a Shapefile in the specified subfolder of the Ensembles folder that
# includes a field with the district assignment. Note that this method is both
# slower and creates more file clutter than the CSV version.
def write_to_shapefile(partition, assignment_col, vtds_file, folder, name):
    vtds = geopandas.read_file(vtds_file)
    vtds[assignment_col] = partition.assignment.to_series()
    filename = './Ensembles/' + folder + '/' + name + '.shp'
    vtds.to_file(filename, index = False)
