#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
input_template.py

Created by Charlie Murphy
19 August 2021

This file is used to give the correct file paths to create_ensemble.py
'''

# SHP file with vtds
vtd_file  = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2021 Data Set 2 Edited\PA_2020_vtds.shp'

# SHP file with counties
county_file = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2021 Data Set 2 Edited\PA_2020_counties.shp'

# SHP file with municipalities
muni_file = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2021 Data Set 2 Edited\PA_2020_muni.shp'

# Destination folder for ensemble.  
# Must be placed within the Ensembles folder
folder = 'Testing'

# File name
filename = "MUNI_2"

# If this is set to false, pickled versions of the graphs with the specified 
# file names must exist and will be used. Not generating new graphs will improve
# start-up speed.
new_graphs = True

# Pickled Names
county_graph_dump = "county_graph_PAcongr.dump"
muni_graph_dump = "muni_graph_PAcongr.dump"
vtd_graph_dump = "vtd_graph_PAcongr.dump"
flipped_counties_dump = "flipped_counties_PAcongr.dump"
flipped_munis_dump = "flipped_munis_PAcongr.dump"

# GEOID Column
geoid_col = 'GEOID20'

# Population Column
pop_col = 'P0010001'

# County Column
county_col = 'FIPS'

# Municipality Column
muni_col = "MUNI"

# Name Column
name_col = "NAME"

# Assignment Column
# Name of the column in the graph objects that will be used to record the 
# redistricting plan
assignment_col = 'assignment'

# Starting County
# The number in the county_col of the starting county. The population of this 
# county must be greater than (1 + epsilon) * the ideal population and have
# more
starting_county = '049'

# Epsilon
# The percentage any given district is allowed to be different from the ideal
# population. Note that this does not apply to the final district.
epsilon = 0.05

# Number of Districtsx`
district_num = 17

# Number of Tries
# How many times the program will try to split a county before it assumes that
# no valid split is possible
max_tries = 20

# Number of plans
runs = 1