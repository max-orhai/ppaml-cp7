"""
Evaluate inferred ILI rates with truth data

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import sys
import os.path as osp
import simplejson as json
from collections import OrderedDict
from datetime import datetime
import csv



def main():

    eval_dir = sys.argv[1]
    input_dir = sys.argv[2]
    output_dir = sys.argv[3]
    log_dir = sys.argv[4]

    #_________________________________________________________________________
    ## Supporting data files that are used in the processing
    #

    # files that stores county demographics in JSON format
    VaccTweets_fn = (osp.join(input_dir, "Flu_Vacc_Tweet_TRAIN.json"),)

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
    earliest=datetime.strptime('09/27/2014','%m/%d/%Y')
    latest=datetime.strptime('05/23/2015','%m/%d/%Y')


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
    region_name = header[3:] # name starts from the 4th column
    for data in ObsData: # each week
        this_week = datetime.strptime(data['Ending'], '%m/%d/%Y')
        if (this_week >= earliest) and (this_week <= latest):
            for name in region_name: # each regione
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
    wgt_ILI = {}
    wgt_Err = {}
    sum_squared_err = 0
    count = 0
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
        count += 1
    mean_squared_err = sum_squared_err / count
    root_mean_squared_err = sqrt(mean_squared_err)

    #_________________________________________________________________________
    ## save the evaluation results
    # metric_str = 'Sum of squared errors: ' + str(sum_squared_err) + '\n'
    metric_str = 'Root mean squared error: ' + str(root_mean_squared_err) + '\n'
    with open(metric_fn, 'wb') as fobj:
        fobj.write(metric_str)
            
    return
        
if __name__ == "__main__":
    main()
    
