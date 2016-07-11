# -*- coding: utf-8 -*-
"""

Extract percentages of ILI cases for each region, week and year from
text files converted from PDF files acquired from Tennessee.

It is assumed that the region names and ILI data are in the same
patterns in the text files so that the extraction can be done
automatically. Some files may not work.


@author: syu
"""

import os
import re
import operator
import matplotlib.pyplot as plt
from collections import defaultdict
import csv

RegionName = ['State', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# store % ILI for each region, week and year (default value None)
# keys are (year, week, region name) and values are ILI percentages
RegionILI = defaultdict(lambda: None)
#RegionILI = {}
for root, dirs, filenames in os.walk("."):
    for filename in filenames:
        # find all text files
        if filename.endswith('.txt'):
            print(os.path.join(root,filename))
            weekChecked = False
            lineCnt = -1
            # read the weekly % ILI for each district
            with open(os.path.join(root,filename), 'rb') as txtFileObj:
                for line in txtFileObj:
                    # read the week number
                    if (re.match("Week [0-9]*",line) and not(weekChecked)):
                        week = int(re.match("Week ([0-9]*)",line).group(1))
                        weekChecked = True
                    # check if the line begins with a floating point number
                    fnum = re.match("\A[0-9]*\.([0-9]*)", line)
                    if fnum:
                        # make sure the number doesn't end with %
                        fnum_noperc = re.match("\A[0-9]*\.([0-9]*)(?!\%)", line)
                        if fnum_noperc.group(0)==fnum.group(0):
                            lineCnt = lineCnt+1
                            # skip the first 10 (prior week) and store the next 10
                            if (lineCnt>=10 and lineCnt<20):
                                if week < 30:
                                    # prior year
                                    year = int(root[7:])
                                else:
                                    # current year
                                    year = int(root[2:6])                            
                                district = lineCnt - 10
                                RegionILI[year,week,RegionName[district]] = \
                                  float(fnum_noperc.group(0))

#ILI_Dict = {key: RegionILI[key] for key in RegionILI.keys() \
#            if (key[2]=="State of Tennessee")}
#sorted_dict = sorted(ILI_Dict.items(), key=operator.itemgetter(0))
#sorted_val=[sorted_dict[k][1] for k in range(0,len(sorted_dict))]
#plt.clf()
#plt.plot(sorted_val)
#

# years and weeks in the dataset
yr_wk = [(2011,wk) for wk in range(40,53)] + \
  [(yr,wk) for yr in (2012,2013) for wk in range(1,53)] + \
  [(2014,wk) for wk in range(1,54)] + \
  [(2015,wk) for wk in range(1,53)]

# Create a dictionary whose keys are region names and whose values are their
# corresponding weekly ILI percentages. If data is missing, fill in with
# none.
RegionWklyILI = {}
for region in RegionName:
    RegionWklyILI[region] = [RegionILI[wk_cnt+(region,)] for wk_cnt in yr_wk]
    
with open('Mississippi.csv','wb') as fp:
    datawriter = csv.writer(fp, delimiter=',')
    datawriter.writerow((None, None)+tuple(RegionName))
    for cnt in range(0,len(yr_wk)):        
        row = yr_wk[cnt]+ \
          tuple([RegionWklyILI[region][cnt] for region in RegionName])
        datawriter.writerow(row)
