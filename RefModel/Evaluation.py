"""
Evaluate inferred ILI rates with truth data

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import sys
import os.path as osp
import simplejson as json
from collections import OrderedDict
from datetime import datetime, date, timedelta
import csv
import numpy as np
import matplotlib.pyplot as plt

"""
eval_dir = '/projects/1614/software/sandbox/ppaml-cp7-datasets/Small/eval'
input_dir = '/projects/1614/software/sandbox/ppaml-cp7-datasets/Small/input'
output_dir = '/projects/1614/software/sandbox/ppaml-cp7-datasets'
log_dir = ''
"""

eval_dir = 'C:/Users/syu/project/1614/data/Ch7_Data/ppaml-cp7-datasets/Middle/eval'
input_dir = 'C:/Users/syu/project/1614/data/Ch7_Data/ppaml-cp7-datasets/Middle/input'
#eval_dir = 'C:/Users/syu/project/1614/data/Ch7_Data/ppaml-cp7-datasets/Small/eval'
#input_dir = 'C:/Users/syu/project/1614/data/Ch7_Data/ppaml-cp7-datasets/Small/input'
output_dir = ''
log_dir = ''

PLOT = 1
def main():

    eval_dir = sys.argv[1]
    input_dir = sys.argv[2]
    output_dir = sys.argv[3]
    log_dir = sys.argv[4]

    return
    
if __name__ == "__main__":
    main()

#_________________________________________________________________________
## Supporting data files that are used in the processing
#

# files that stores county demographics in JSON format
VaccTweets_fn = (osp.join(input_dir, "Flu_Vacc_Tweet_TRAIN.json"),)
print VaccTweets_fn

# file that stores the mapping from regions/states/districs to counties
map_fn = osp.join(input_dir, 'Region2CountyMap.json')


#_________________________________________________________________________
## ILI truth data file
#
#

data_fn = osp.join(eval_dir, 'Flu_ILI_TRUTH.csv')

#_________________________________________________________________________
## JSON file that stores the results
#
#

result_fn = osp.join(output_dir, "result.json")


#_________________________________________________________________________
## Evalution results
#
#

metric_fn = osp.join(log_dir, 'eval_metric.csv')


#_________________________________________________________________________
## Specify the earlies and latest dates for performance evaluation
#
earliest=datetime.strptime('09/28/2013','%m/%d/%Y')
latest=datetime.strptime('05/23/2015','%m/%d/%Y')
#earliest = datetime.strptime('09/28/2013', '%m/%d/%Y')
#latest = datetime.strptime('04/19/2014', '%m/%d/%Y')


#_________________________________________________________________________
## Specify the region (as defined in the header of csv truth file) not to be
# considered. This is typically used to avoid conflicting/overlapping regions.
Region2Avoid = []
#Region2Avoid = ['HHS Region 4', 'NC']


#_________________________________________________________________________
## read the county demographics
with open(VaccTweets_fn[0], 'rb') as fobj:
    # the first file
    CntData = json.load(fobj, object_pairs_hook=OrderedDict)

# total number of weeks
num_weeks = int((latest - earliest).days / 7) + 1


#_________________________________________________________________________
## read the ILI truth data of each HHS region/state/district
ObsData = [] # observed data
# read observed data in CSV format
with open(data_fn, 'rb') as fobj:
    reader = csv.reader(fobj)
    header = reader.next()
    # data: a list of dictionaries {column name: cell value}
    for row in reader:
        data = {key:val for (key,val) in zip(header,row)}
        ObsData.append(data)

# Retain the ILI truth data of interest and store data in a dictionary variable
# ObsDataFlat: {(region name, week): ILI rate}
ObsDataFlat = {}
region_name_hd = header[3:] # name starts from the 4th column
for data in ObsData: # each week
    this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
    if (this_week >= earliest) and (this_week <= latest):
        for name in region_name_hd: # each regione
            if (data[name] != 'NaN') and (name not in Region2Avoid):
                # only it's not in the region to avoid and it's not NaN
                ObsDataFlat[(name,this_week.strftime('%m/%d/%Y'))] = float(data[name][:-1])/100.
                # the last character is %


#_________________________________________________________________________
## read the mapping from region/state/district to counties
# mapping: {region name: {FIPS: county name}}
with open(map_fn, 'rb') as fobj:
    mapping = json.load(fobj)


#_________________________________________________________________________
## read the inferred ILI data and store in a dictionary
# InfData: {FIPS: {"Name": name,
#               "ILI percentage %": {"mm/dd/yyyy": ILI %}}}
with open(result_fn, 'rb') as fobj:
    InfData = json.load(fobj)


#_________________________________________________________________________
## compare inferred data with truth
'''
wgt_ILI = {}
wgt_Err = {}
sum_squared_err = 0
for (region_name, week) in ObsDataFlat:
    tmp_wgt_ILI = 0
    wgt = 0
    for fips in mapping[region_name]:
        wgt_factor = CntData[fips]["Population, 2014 estimate"] # weighted by county population
        wgt = wgt + wgt_factor
        # inferred data
        tmp_wgt_ILI = tmp_wgt_ILI + wgt_factor*InfData[fips]["ILI percentage %"][week]/100.
    wgt_ILI[(region_name, week)] = tmp_wgt_ILI / wgt # weighted average
    # difference between true and inferred data
    wgt_Err[(region_name, week)] = ObsDataFlat[(region_name, week)] - wgt_ILI[(region_name, week)]
    # sum of squared errors of all regions and weeks
    sum_squared_err = sum_squared_err + wgt_Err[(region_name, week)]**2
'''

#_________________________________________________________________________
## region population
region_pop = {}
for name in region_name_hd:
    region_pop[name] = 0
    for fips in mapping[name]:
        region_pop[name] = region_pop[name] + CntData[fips]["Population, 2014 estimate"]
        

#_________________________________________________________________________
## compare inferred data with truth
wgt_ILI = {}
wgt_Err = {}
sum_squared_err = 0
for (region_name, week) in ObsDataFlat:
    region_ILI_case = 0
    for fips in mapping[region_name]:
        county_pop = CntData[fips]["Population, 2014 estimate"] # weighted by county population
        # inferred ILI cases for each region
        region_ILI_case = region_ILI_case + county_pop*InfData[fips]["ILI percentage %"][week]/100.
    wgt_ILI[(region_name, week)] = region_ILI_case / region_pop[region_name] # weighted average
    # difference between true and inferred data
    wgt_Err[(region_name, week)] = ObsDataFlat[(region_name, week)] - wgt_ILI[(region_name, week)]
    # sum of squared errors of all regions and weeks
    sum_squared_err = sum_squared_err + wgt_Err[(region_name, week)]**2
    

#_________________________________________________________________________
## re-arrange data for plotting (weekly ILI cases for each region)
WeeklyILI_Inf = {}
WeeklyILI_True = {}
Week = []
for name in region_name_hd:
    WeeklyILI_Inf[name] = np.full(num_weeks,np.nan)
    WeeklyILI_True[name] = np.full(num_weeks,np.nan)
    w_end = earliest
    wk = 0    
    while w_end <= latest:
        if (name, w_end.strftime('%m/%d/%Y')) in wgt_ILI.keys():
            WeeklyILI_Inf[name][wk] = wgt_ILI[(name, w_end.strftime('%m/%d/%Y'))]
            WeeklyILI_True[name][wk] = ObsDataFlat[(name, w_end.strftime('%m/%d/%Y'))]
        wk = wk + 1 # counter
        w_end = w_end + timedelta(days=7) # date

w_end = earliest
wk = 0    
while w_end <= latest:
    Week.append(w_end.strftime('%m/%d/%Y'))
    w_end = w_end + timedelta(days=7) # date


#_________________________________________________________________________
## plot the inferred vs. true ILI rates for each region
plt.figure(1)
plt.clf()
plt.plot(WeeklyILI_Inf[region_name_hd[0]],'r')
plt.plot(WeeklyILI_True[region_name_hd[0]],'b')
plt.title(region_name_hd[0])

'''
if PLOT:
    fig = plt.figure(figsize=(8, 6))
    ax = plt.subplot(111, xlabel='week', ylabel='wgt. ILI rate', title='Wgh. ILI Rate in ')
    ax.plot(ObsDataFlat[(region_name_hd[0], week)], 'b', alpha=.05)
'''

#_________________________________________________________________________
## save the evaluation results
metric_str = 'Sum of squared errors: ' + str(sum_squared_err) + '\n'
with open(metric_fn, 'wb') as fobj:
    fobj.write(metric_str)
    

