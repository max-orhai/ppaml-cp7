# -*- coding: utf-8 -*-
"""

Extract percentages of ILI cases for each region, week and year from
text files converted from PDF files acquired from Tennessee.

It is assumed that the region names and ILI data are in the same
patterns in the text files so that the extraction can be done
automatically. Some files may not work.

Created on Thu Oct 15 13:27:40 2015

@author: syu
"""

import os
import re
import operator
import matplotlib.pyplot as plt
from collections import defaultdict
import csv

# store % ILI for each region, week and year (default value None)
# keys are (year, week, region name) and values are ILI percentages
RegionILI = defaultdict(lambda: None)
for root, dirs, filenames in os.walk("."):
    for filename in sorted(filenames):
        # find all text files that starts with 'week'
        if (filename.endswith('.txt') and filename.startswith('week')):
            print(os.path.join(root,filename))
            lineCnt = -1;
            percCnt = -1
            RegionName = []
            # read the region names and correponding their % ILI 
            with open(os.path.join(root,filename), 'rb') as txtFileObj:
                # find week and year from the file name
                fnsplit = re.match("([a-zA-Z]*)([0-9]*)([a-zA-Z_]*)([0-9]*)",filename)
                week = int(fnsplit.group(2))
                year = int(fnsplit.group(4))
                for line in txtFileObj:
                    if re.match("Summary for",line):
                        # start counting lines for region name block
                        lineCnt = 0
                    if (lineCnt>=0 and lineCnt<15):
                        lineCnt = lineCnt + 1
                        # region names between the 2nd and the 15th lines
                        if (lineCnt>1):
                            name = re.match("(.*)",line)
                            RegionName.append(name.group(0))
                    if re.match("% ILI",line):
                        # start counting lines for ILI percentage block
                        percCnt = 0
                    if (percCnt>=0 and percCnt<19):
                        percCnt = percCnt + 1
                        # % ILI between the 6th and the 19th lines
                        if percCnt>5:
                            perc = re.match("(.*)%",line)
                            if perc is None:
                                perc = re.match("n/a",line)
                                RegionILI[year,week,RegionName[percCnt-6]]=None
                            else:
                                RegionILI[year,week,RegionName[percCnt-6]]=\
                                  float(perc.group(1))
                

#ILI_Dict = {key: RegionILI[key] for key in RegionILI.keys() \
#            if (key[2]=="State of Tennessee")}
#sorted_dict = sorted(ILI_Dict.items(), key=operator.itemgetter(0))
#sorted_val=[sorted_dict[k][1] for k in range(0,len(sorted_dict))]
#plt.clf()
#plt.plot(sorted_val)
#

# years and weeks in the dataset
yr_wk = [(2009,wk) for wk in range(32,53)] + \
  [(yr,wk) for yr in (2010,2011,2012,2013) for wk in range(1,53)] + \
  [(2014,wk) for wk in range(1,54)] + \
  [(2015,wk) for wk in range(1,53)]

# Create a dictionary whose keys are region names and whose values are their
# corresponding weekly ILI percentages. If data is missing, fill in with
# none.
RegionWklyILI = {}
for region in RegionName:
    RegionWklyILI[region] = [RegionILI[wk_cnt+(region,)] for wk_cnt in yr_wk]
    
with open('TennesseeILI.csv','wb') as fp:
    datawriter = csv.writer(fp, delimiter=',')
    datawriter.writerow((None, None)+tuple(RegionName))
    for cnt in range(0,len(yr_wk)):        
        row = yr_wk[cnt]+ \
          tuple([RegionWklyILI[region][cnt] for region in RegionName])
        datawriter.writerow(row)
