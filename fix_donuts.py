#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
fix_donuts.py

Created by Charlie Murphy
23 December 2021

This file merges any nodes (either municipalities or VTDs) that are 
completely surrounded by another node into said node.
'''

from discontiguous_counties import check_donuts
import geopandas
from gerrychain import Graph
from reusable_data_2 import get_county_subgraphs
from tqdm import tqdm

# fix_donuts
# Create a GeoDataFrame for the municipalities without donuts and update the
# municipality column of the VTD data to match the labelling.
def fix_donuts(county_filename, muni_filename, vtd_filename, assignment_col,
    county_col, geoid_col, muni_col, name_col, pop_col, geom_col):

    # Create list of columns
    columns = [county_col, geoid_col, muni_col, name_col, pop_col, geom_col]

    # Read the data into GeoDataFrames
    vtd_data = geopandas.read_file(vtd_filename)
    muni_data = geopandas.read_file(muni_filename)
    county_data = geopandas.read_file(county_filename)

    # Create a graph for the purpose of finding donuts
    muni_data[assignment_col] = 1
    muni_graph = Graph.from_geodataframe(muni_data)
    county_graph = Graph.from_geodataframe(county_data)

    # Get Subgraphs
    subgraphs = get_county_subgraphs(county_graph, muni_graph, county_col)

    # Find Donuts
    donuts = check_donuts(muni_graph, list(county_graph.nodes()), subgraphs, 
        assignment_col)

    # Create New GeoDataFrame
    muni_results = muni_data[columns]

    # Create list of used holes
    holes = set()

    # Merge holes into donuts
    for donut in tqdm(donuts):
        for hole in donuts[donut]:
            if hole not in holes:
                holes.add(hole)

                # Merge geometry
                muni_results[geom_col][donut] = muni_results[geom_col][donut].union(muni_results[geom_col][hole])

                # Sum Population
                muni_results[pop_col][donut] = muni_results[pop_col][donut] + muni_results[pop_col][hole]

                # Combine Name
                muni_results[name_col][donut] = muni_results[name_col][donut] + " / " + muni_results[name_col][hole]

                # Remove old hole entry
                muni_results = muni_results.drop(labels = hole, axis = 0)

                # Update muni name in 
                for i in range(len(vtd_data)):
                    if vtd_data[muni_col][i] == muni_data[muni_col][hole]:
                        vtd_data[muni_col][i] = muni_results[muni_col][donut]

    return muni_results, vtd_data