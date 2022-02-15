#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
create_clusters.py

Created by Charlie Murphy
15 February 2022

This file creates clusters of counties that can be divided evenly into districts
(within the allowed population deviation) so that the algorithm need to not 
create a path through the entire state at once.
'''

def create_clusters()