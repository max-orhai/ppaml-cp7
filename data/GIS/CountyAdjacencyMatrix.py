# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 14:35:21 2015

@author: syu
"""

import os
import csv
from scipy.sparse import lil_matrix
import matplotlib.pyplot as plt
import networkx as nx

# county adjacency file
#root = "C:/Users/syu/project/1614/data/GIS"
root = ""
filename = "county_adjacency.txt"

# if only considering the 50 states, then FIPS is less than 59999
STATEONLY = True

CountyAdjDict = {} # county name as key and value is a list containing nbr info
CountyName = {} # county name as key and counter as its value
CountyName_Ordered = [] # ordered county names that match the order in adjacency matrix
c_counter = 0

# read county adjacency from the file downloaded from US Census
# https://www.census.gov/geo/reference/county-adjacency.html (data has error)
with open(os.path.join(root,filename), 'rb') as adjObj:
    reader = csv.reader(adjObj, delimiter='\t', quotechar='\"')
    for row in reader:
        if row[0]:
            # leading row -- county of interest
            if (not(STATEONLY) or int(row[1]) < 60000):
                # FIPS < 60000 correponds to the 50 states
                ToConsider = True
            else:
                ToConsider = False

            if ToConsider:
                # this row contains the county name of interest
                county_state = row[0]
                state = row[0][-2:]
                CountyAdjDict[county_state] = [state, row[1], {row[2]: row[3]}]
                # first neighbor is itself [state, FIPS, {county_name: FIPS}]
                CountyName[county_state] = c_counter
                CountyName_Ordered.append(county_state)
                c_counter = c_counter + 1
        else:
            # this row contains an adjacent county; add to the neighbor list
            if ToConsider:
                neighbor_county_state = row[2]
                CountyAdjDict[county_state][2][neighbor_county_state] = row[3]


# create adjacency matrix whose elements are ordered as they appear in
# Census (alphabetically) diagonal terms are 0 (no self neighbors)
AdjMatrix = lil_matrix((len(CountyName), len(CountyName)))
for name in CountyAdjDict.keys():
    for nbr_name in CountyAdjDict[name][2].keys():
        if name != nbr_name:
            AdjMatrix[CountyName[name],CountyName[nbr_name]] = 1

#plt.spy(ca.AdjMatrix) # plot sparse adjacency matrix
#G=nx.from_scipy_sparse_matrix(AdjMatrix)
#nx.draw_networkx(G)


    
