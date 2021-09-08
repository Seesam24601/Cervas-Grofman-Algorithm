#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
input_template.py

Created by Charlie Murphy
19 August 2021

This file is used to give the correct file paths to create_ensemble.py
'''

# SHP file with election data
state_file  = r'C:\Users\charl\Box\Internships\Gerry Chain 2\States\Pennsylvania\2020 Data\PA_2020_vtds.shp'

# Destination folder for ensemble. 
# Must be placed within the Ensembles folder
folder = 'Testing'

# GEOID Column
geoid_col = 'GEOID20'

# Population Column
pop_col = 'POP100'

# County Column
county_col = 'COUNTYFP20'

# Starting County
# The number in the county_col of the starting county.
starting_county = '049'

# Election Columns
# These must be formatted as a dictionary of dictionary where the keys in the 
# outer dictionary are the elections and the keys in the inner dictionary are
# the political parties
election_cols = {"SEN18": {"Democratic": "G18DemSen", "Republican": "G18RepSen"},
    "GOV18": {"Democratic": "G18DemGov", "Republican": "G18RepGv"},
    "SEN16": {"Democratic": "T16SEND", "Republican": "T16SENR"},
    "PRES12": {"Democratic": "PRES12D", "Republican": "PRES12R"},
    "PRES16": {"Democratic": "T16PRESD", "Republican": "T16PRESR"},
    "ATG16": {"Democratic": "T16ATGD", "Republican": "T16ATGR"}}

# Population Deviation
# The amount of allowable population deviation for the redistricting plans
pop_deviation_max = 0.05

# Number of Districts
district_num = 17