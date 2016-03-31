"""
Read observed data and construct observation vector and measurement
matrix that maps spatio-temporal grid to observations

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import csv
import simplejson as json
import numpy as np
import scipy.sparse as spa
from datetime import datetime

'''
Read observed data and construct observation vector and measurement matrix
'''
def ConstructMmentMatrix(data_fn, map_fn, CountyName, dates, CountyInfo=None, region2avoid=[], isSparse=True):
    # @param data_fn: CSV file that stores the observed weekly ILI from different
    #  regions, states and districts
    # @param map_fn: JSON file that stores the counties that are in each
    #  region, state or district listed in the data file data_fn
    # @param CountyName: dictionary defining the order in which each county
    #  appears in the adjacency matrix (spatio-temporal grid):
    #  {'county, state': (order, FIPS)}
    # @param dates: a tuple (earliest, latest) that specifies the earliest
    #  and latest dates of the temporal grid points. Both elements are
    #  datetime objects.
    # @param CountyInfo: county geographic and demographic information
    #  {FIPS: {"Population, 2010": 23000, ...}}
    # @param region2avoid: specify the region (as defined in the header of csv
    #   truth file 'true_data_fn') not to be considered. This is typically used
    #   to avoid conflicting/overlapping regions.
    # @param isSparse: (default: True) whether to return a sparse measurement matrix
    #
    # @param[out] Cm: measurement matrix in numpy array of size
    #   [no. of measurements, no. of spatio-temporal grid points]
    # @param[out] ObsDataFlat: 2-d numpy matrix arranged according to the
    #   order of the spatio-temporal grid
    #   [no. of measurements, 1]

    earliest = dates[0] # earliest date for processing
    latest = dates[1] # latest date for processing

    # number of counties in the spatio-temporal grid
    num_counties = len(CountyName.keys())
    # number of weeks in the spatio-temporal grid
    num_weeks = int((latest - earliest).days / 7) + 1
    # total grid points in the spatio-temporal grid
    num_cell = num_counties*num_weeks

    ## read the ILI data of each region (HHS, state and/or districts)
    ObsData = [] # observed data
    # read observed data in CSV format
    with open(data_fn, 'rb') as fobj:
        reader = csv.reader(fobj)
        header = reader.next()
        # data: a list of dictionaries {column name: cell value}
        for row in reader:
            data = {key:val for (key,val) in zip(header,row)}
            ObsData.append(data)

    ## flatten the ILI data
    DateRegion = [] # DataRegion: [(date,region name),...]
    ObsDataFlat = [] # ObsDataFlat: [ILI rate,]
    region_name = header[3:] # name starts from the 4th column
    for data in ObsData: # each week
        this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
        if (this_week >= earliest) and (this_week <= latest):
            for name in region_name: # each regione
                if (data[name] != 'NaN') and (name not in region2avoid) and (data[name] > 0.00001):
                    # only it's not in the region to avoid and it's not NaN
                    # DateRegion records the time and region names in the
                    # same order as the flatten data ObsDataFlat
                    DateRegion.append((this_week,name))
                    ObsDataFlat.append(float(data[name][:-1])/100.)
                    # the last character is %
    ObsDataFlat = np.array(ObsDataFlat)
    ObsDataFlat = ObsDataFlat[np.newaxis].T # convert to 2D array
    
    ## read the mapping from region to counties
    # mapping: {region name: {FIPS: county name}}
    with open(map_fn, 'rb') as fobj:
        mapping = json.load(fobj)

    ## relate spatio-temporal grid to observations
    #  Cm: [no. of measurements, no. of spatio-temporal grid points]
    if isSparse:
        Cm = spa.lil_matrix((ObsDataFlat.shape[0],num_cell))
    else:
        Cm = np.zeros((ObsDataFlat.shape[0],num_cell))
    # fips_order: {fips: order in the spatial grid}
    fips_order = {fips:order for (order, fips) in CountyName.values()}
    counter = 0
    for (date, region) in DateRegion:
        region_pop = 0. # initialize total population of the region 
        region_fips = mapping[region].keys() # FIPS of all counties in this region
        weeks_since = int((date-earliest).days / 7) # weeks since the earliest date
        for fips in region_fips:
            if CountyInfo is None:
                # equal weighting
                Cm[counter, num_counties*weeks_since +
                    fips_order[fips]] = 1.0/len(region_fips)
            else:
                # weighted by population
                county_pop = CountyInfo[fips]["Population, 2014 estimate"]
                region_pop = region_pop + county_pop
                # weighted by population
                Cm[counter, num_counties*weeks_since + fips_order[fips]] = county_pop
        # normalize by population
        if CountyInfo is not None:
            for fips in region_fips:
                Cm[counter, num_counties*weeks_since + fips_order[fips]] = (
                    Cm[counter, num_counties*weeks_since + fips_order[fips]]/region_pop)
            
        counter = counter + 1 # counter for the element in measurement vector

    return (Cm, ObsDataFlat)


'''
Read observed data and defined a measurement matrix that corresponds to the
missing data (i.e. NaN). It is used to infer the missing data that can be later
compared to the truths.
'''
def ConstructMissingMmentMatrix(data_fn, map_fn, CountyName, dates, CountyInfo=None, region2avoid=[], isSparse=True):
    # @param data_fn: CSV file that stores the observed weekly ILI from different
    #  regions, states and districts
    # @param map_fn: JSON file that stores the counties that are in each
    #  region, state or district listed in the data file data_fn
    # @param CountyName: dictionary defining the order in which each county
    #  appears in the adjacency matrix (spatio-temporal grid):
    #  {'county, state': (order, FIPS)}
    # @param dates: a tuple (earliest, latest) that specifies the earliest
    #  and latest dates of the temporal grid points. Both elements are
    #  datetime objects.
    # @param CountyInfo: county geographic and demographic information
    #  {FIPS: {"Population, 2010": 23000, ...}}
    # @param region2avoid: specify the region (as defined in the header of csv
    #   truth file 'true_data_fn') not to be considered. This is typically used
    #   to avoid conflicting/overlapping regions.
    # @param isSparse: (default: True) whether to return a sparse measurement matrix
    #
    # @param[out] Cm: measurement matrix in numpy array of size
    #   [no. of measurements, no. of spatio-temporal grid points]

    earliest = dates[0] # earliest date for processing
    latest = dates[1] # latest date for processing

    # number of counties in the spatio-temporal grid
    num_counties = len(CountyName.keys())
    # number of weeks in the spatio-temporal grid
    num_weeks = int((latest - earliest).days / 7) + 1
    # total grid points in the spatio-temporal grid
    num_cell = num_counties*num_weeks

    ## read the ILI data of each region (HHS, state and/or districts)
    ObsData = [] # observed data
    # read observed data in CSV format
    with open(data_fn, 'rb') as fobj:
        reader = csv.reader(fobj)
        header = reader.next()
        # data: a list of dictionaries {column name: cell value}
        for row in reader:
            data = {key:val for (key,val) in zip(header,row)}
            ObsData.append(data)

    ## find the missing ILI data (i.e. NaN cells)
    DateRegion = [] # DataRegion: [(date,region name),...]
    region_name = header[3:] # name starts from the 4th column
    for data in ObsData: # each week
        this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
        if (this_week >= earliest) and (this_week <= latest):
            for name in region_name: # each region
                if ((data[name] == 'NaN') or (data[name] < 0.00001)) and (name not in region2avoid):
                    # only it's not in the region to avoid and it's NaN
                    # DateRegion records the time and region names
                    DateRegion.append((this_week,name))

    ## read the mapping from region to counties
    # mapping: {region name: {FIPS: county name}}
    with open(map_fn, 'rb') as fobj:
        mapping = json.load(fobj)

    ## relate spatio-temporal grid to the missing cells
    #  Cm: [no. of measurements, no. of spatio-temporal grid points]
    if isSparse:
        Cm = spa.lil_matrix((len(DateRegion),num_cell))
    else:
        Cm = np.zeros((len(DateRegion),num_cell))
    # fips_order: {fips: order in the spatial grid}
    fips_order = {fips:order for (order, fips) in CountyName.values()}
    counter = 0

    for (date, region) in DateRegion:
        region_pop = 0. # initialize total population of the region 
        region_fips = mapping[region].keys() # FIPS of all counties in this region
        weeks_since = int((date-earliest).days / 7) # weeks since the earliest date
        for fips in region_fips:
            if CountyInfo is None:
                # equal weighting
                Cm[counter, num_counties*weeks_since +
                    fips_order[fips]] = 1.0/len(region_fips)
            else:
                # weighted by population
                county_pop = CountyInfo[fips]["Population, 2014 estimate"]
                region_pop = region_pop + county_pop
                # weighted by population
                Cm[counter, num_counties*weeks_since + fips_order[fips]] = county_pop
        # normalize by population
        if CountyInfo is not None:
            for fips in region_fips:
                Cm[counter, num_counties*weeks_since + fips_order[fips]] = (
                    Cm[counter, num_counties*weeks_since + fips_order[fips]]/region_pop)
                    
        counter = counter + 1 # counter for the element in measurement vector

    return Cm

'''
Extract from the truth file the truth data that corresponds to the missing data
(i.e. NaN) in another file. The truth data is to be used for comparison with the
inferred missing data.
'''
def ExtractTruthData(true_data_fn, test_data_fn, dates, region2avoid=[]):
    # @param true_data_fn: CSV file that stores the observed ture weekly ILI from different
    #  regions, states and districts
    # @param test_data_fn: CSV file that stores the test data that contains missing
    #  ILI cells. Otherwise, it's in the same format and contains exactly the
    #  same values as those in data_fn.
    # @param dates: a tuple (earliest, latest) that specifies the earliest
    #  and latest dates of the temporal grid points. Both elements are
    #  datetime objects.
    # @param region2avoid: specify the region (as defined in the header of csv
    #   truth file 'true_data_fn') not to be considered. This is typically used
    #   to avoid conflicting/overlapping regions.
    #
    # @param[out] TrueMissingData: 2-d numpy matrix arranged according to the
    #   order in which the missing data appears in test_data_fn [no. of missing data, 1]
    # @param[out] DateRegion: dates and region names of the missing data. A list
    #   [(date,region name),...] where each element is the date and region name
    #   of the corresponding missing element.

    earliest = dates[0] # earliest date for processing
    latest = dates[1] # latest date for processing

    ## read the ILI test data of each region (HHS, state and/or districts)
    TestData = [] # observed data
    # read observed data in CSV format
    with open(test_data_fn, 'rb') as fobj:
        reader = csv.reader(fobj)
        header = reader.next()
        # data: a list of dictionaries {column name: cell value}
        for row in reader:
            data = {key:val for (key,val) in zip(header,row)}
            TestData.append(data)

    ## find the dates and regions of the missing ILI data (i.e. NaN cells)
    DateRegion = [] # DataRegion: [(date,region name),...]
    region_name = header[3:] # name starts from the 4th column
    for data in TestData: # each week
        this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
        if (this_week >= earliest) and (this_week <= latest):
            for name in region_name: # each region
                if ((data[name] == 'NaN') or (data[name] < 0.00001)) and (name not in region2avoid):
                    # only it's not in the region to avoid and it's NaN
                    # DateRegion records the time and region names
                    DateRegion.append((this_week,name))

    '''
    find the true ILI data that corresponds to the missing cells
    '''
    ## read true data
    TrueData = [] # observed data
    # read observed data in CSV format
    with open(true_data_fn, 'rb') as fobj:
        reader = csv.reader(fobj)
        header = reader.next()
        # data: a list of dictionaries {column name: cell value}
        for row in reader:
            data = {key:val for (key,val) in zip(header,row)}
            TrueData.append(data)

    ## reformat the true data into a dictionary {(date,region): ILI rate} for easy searching
    TrueDataDict = {} # {(data,region): ILI rate}
    region_name = header[3:] # name starts from the 4th column
    for data in TrueData: # each week
        this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
        if (this_week >= earliest) and (this_week <= latest):
            for name in region_name: # each region
                if name not in region2avoid:
                    if data[name] != 'NaN':
                        # only it's not in the region to avoid and it's not NaN
                        TrueDataDict[(this_week,name)] = float(data[name][:-1])/100.
                        # the last character is %
                    else:
                        TrueDataDict[(this_week,name)] = 'NaN'
    
    ## Extract the truth data
    TrueMissingData = []
    for (this_week,region) in DateRegion:
        TrueMissingData.append(TrueDataDict[(this_week,region)])
    TrueMissingData = np.array(TrueMissingData) # convert to numpy array
    TrueMissingData = TrueMissingData[np.newaxis].T # convert to 2D array
    
    return (TrueMissingData, DateRegion)

'''
Assign the same value in a larger geographical area to all counties inside the area
'''
def AssignSameValue2FinerRes(true_data_fn, map_fn, CountyName, dates,
                             region2avoid=None):
    # @param true_data_fn: CSV file that stores the observed ture weekly ILI from different
    #  regions, states and districts
    # @param map_fn: JSON file that stores the counties that are in each
    #  region, state or district listed in the data file data_fn
    # @param CountyName: dictionary defining the order in which each county
    #  appears in the adjacency matrix (spatio-temporal grid):
    #  {'county, state': (order, FIPS)}
    # @param dates: a tuple (earliest, latest) that specifies the earliest
    #  and latest dates of the temporal grid points. Both elements are
    #  datetime objects.
    # @param region2avoid: specify the region (as defined in the header of csv
    #   truth file 'true_data_fn') not to be considered. This is typically used
    #   to avoid conflicting/overlapping regions.

    earliest = dates[0] # earliest date for processing
    latest = dates[1] # latest date for processing

    # number of counties in the spatio-temporal grid
    num_counties = len(CountyName.keys())
    # number of weeks in the spatio-temporal grid
    num_weeks = int((latest - earliest).days / 7) + 1
    # total grid points in the spatio-temporal grid
    num_cell = num_counties*num_weeks

    ## read the ILI data of each region (HHS, state and/or districts)
    ObsData = [] # observed data
    # read observed data in CSV format
    with open(true_data_fn, 'rb') as fobj:
        reader = csv.reader(fobj)
        header = reader.next()
        # data: a list of dictionaries {column name: cell value}
        for row in reader:
            data = {key:val for (key,val) in zip(header,row)}
            ObsData.append(data)

    ## flatten the ILI data
    DateRegion = [] # DataRegion: [(date,region name),...]
    ObsDataFlat = [] # ObsDataFlat: [ILI rate,]
    region_name = header[3:] # name starts from the 4th column
    for data in ObsData: # each week
        this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
        if (this_week >= earliest) and (this_week <= latest):
            for name in region_name: # each region
                if name not in region2avoid: # only it's not in the region to avoid
                    # DateRegion records the time and region names in the
                    # same order as the flatten data ObsDataFlat
                    DateRegion.append((this_week,name))
                    ObsDataFlat.append(float(data[name][:-1])/100.)
                    # the last character is %
    ObsDataFlat = np.array(ObsDataFlat)
    ObsDataFlat = ObsDataFlat[np.newaxis].T # convert to 2D array

    ## read the mapping from region to counties
    # mapping: {region name: {FIPS: county name}}
    with open(map_fn, 'rb') as fobj:
        mapping = json.load(fobj)
    
    data_FineRes = np.zeros((num_cell,1))
    # fips_order: {fips: order in the spatial grid}
    fips_order = {fips:order for (order, fips) in CountyName.values()}
    counter = 0
    for (date, region) in DateRegion:
        region_fips = mapping[region].keys() # FIPS of all counties in this region
        weeks_since = int((date-earliest).days / 7) # weeks since the earliest date
        for fips in region_fips:
            data_FineRes[num_counties*weeks_since+fips_order[fips], 0] = ObsDataFlat[counter,0]
        counter = counter + 1 # counter for the element in measurement vector

    return data_FineRes