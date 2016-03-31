# -*- coding: utf-8 -*-
"""
@author: Ssu-Hsin Yu
"""

import os
import csv

def ConstructCountyAdjMatrix(filename, root="", STATEONLY = True, STATES = None):
    """
    Construct county adjacency matrix based on file from US Census
    
    Input:
    filename: file that stores adjacent counties of each county in US (lower 48)
    root: root directory to append to filename (default "")
    STATEONLY: whether to consider states and territory or states only (default state only)
    STATES: specify which states are considered in forming adjacency matrix (default is all states)
        It is a list where each element is a state defined in the abbreviated form (e.g. 'MA').
    
    Output:
    AdjMatrix: county adjacency matrix where each row corresponds to a county.
        Elements corresponding to adjacent counties have the values 1; otherwise 0.
    CountyName: dictionary whose keys are county names and whose values are 2-element tuples
        where the first element is the index as it appear in AdjMatrix and the second element
        is its FIPS code {(county, state): (order, FIPS)}
    CountyAdjDict: dictionary whose keys are county names and whose values are
        lists of the following components: [state, FIPS code, {county_name:FIPS}].
        The last component is itself a dictionry that stores the neighboring counties.
        Its keys are the names of the neighboring counties and values are their FIPS
        codes.
    """
    
    from scipy.sparse import lil_matrix
    
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
                    if not STATES:
                        # all of the states are considered
                        ToConsider = True
                    else:
                        # only states specified in the list variable STATES
                        if row[0][-2:] in STATES:
                            ToConsider = True
                        else:
                            ToConsider = False
                else:
                    ToConsider = False
    
                if ToConsider:
                    # this row contains the county name of interest
                    county_state = row[0]
                    state = row[0][-2:]
                    CountyAdjDict[county_state] = [state, row[1], {row[2]: row[3]}]
                    # one of the neighbors is itself [state, FIPS, {county_name: FIPS}]
                    CountyName[county_state] = (c_counter, row[1])
                    CountyName_Ordered.append(county_state)
                    c_counter = c_counter + 1
            else:
                # this row contains an adjacent county; add to the neighbor list
                if ToConsider:
                    neighbor_county_state = row[2]
                    CountyAdjDict[county_state][2][neighbor_county_state] = row[3]
    
    
    # create adjacency matrix whose elements are ordered as they appear in
    # Census (alphabetically); diagonal terms are 0 (no self neighbors)
    AdjMatrix = lil_matrix((len(CountyName), len(CountyName)))
    counties_of_interest = CountyAdjDict.keys()
    for name in counties_of_interest:
        for nbr_name in CountyAdjDict[name][2].keys():
            if ((name != nbr_name) and (nbr_name in counties_of_interest)):
                # to make sure that (1) a county is not a neighbor of itself (
                # diagnonal terms are 0) and (2) only neighbors that also fall
                # in the states of interest (STATES) are considered.
                AdjMatrix[CountyName[name][0],CountyName[nbr_name][0]] = 1

    return (AdjMatrix, CountyName, CountyAdjDict)
    

def ReadCountyLatLon(filename, root=""):
    """
    Read Latitude and Longitude coordinates of all 50 states
    
    Input:
    filename: file name
    root: root directory to append to filename (default "")
    
    Output:
    county_info: dictionary whose keys are county FIPS codes and values are
    lists of their respective coordinates. The first element of the lists is
    the latitude and the second longitude in degrees
    """
    
    county_info = {}
    with open(os.path.join(root,filename), 'rb') as gpsf:
        reader = csv.DictReader(gpsf, delimiter='\t')
        for row in reader:
            county_info[row["FIPS"]] = \
              [float(row["Latitude"]), float(row["Longitude"])]
    
    return county_info
