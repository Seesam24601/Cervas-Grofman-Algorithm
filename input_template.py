#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
input_template.py

Created by Charlie Murphy
19 August 2021

This file is used to give the correct file paths to create_ensemble.py
'''

# SHP file with vtds
vtd_file  = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2020 Data\PA_2020_vtds.shp'

# SHP file with counties
county_file = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2020 Data\PA_2020_county.shp'

# Destination folder for ensemble. 
# Must be placed within the Ensembles folder
folder = 'Testing'

# File name
filename = "Test_beta_8"

# GEOID Column
geoid_col = 'GEOID20'

# Population Column
pop_col = 'POP100'

# County Column
county_col = 'COUNTYFP20'

# Starting County
# The number in the county_col of the starting county. The population of this 
# county must be greater than (1 + epsilon) * the ideal population and have
# more
starting_county = '089'

# Epsilon
# The percentage any given district is allowed to be different from the ideal
# population. Note that this does not apply to the final district.
epsilon = 0.2

# Number of Districtsx`
district_num = 50

# Number of Tries
# How many times the program will try to split a county before it assumes that
# no valid split is possible
max_tries = 50

# Number of plans
runs = 1