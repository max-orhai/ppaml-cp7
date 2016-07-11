'''
Read data from HHS's Medicare flu vaccination claims file Extract and
convert the relevant information to a dictionary.
The dictionary's keys are the county FIPS codes and values are
dictionaries containing cumulative flu vaccination percentages over time
of the corresponding counties. The vaccination dictionary's keys are the
dates (m/d/yr) of consecutive Saturdays and the values are the cumulative
vaccination percentages up to the dates.

Ssu-Hsin Yu
syu@ssci.com
'''

import os
import csv
from datetime import datetime, date, timedelta
import time
from collections import OrderedDict

# data directory
#root = "/home/syu/Work/ppaml/data/Flu_Vaccination"
root = "C:/Users/syu/project/1614/data/Flu_Vaccination/"

# CDC filename to read
filename = "medicare_flu_vac_county_2012-2015.csv"
#filename = "medicare_flu_vac_county_2013.csv"

# define the earlies date to extract data ('%m/%d/%Y') or empty if using earliest data available
#START_DATE = "10/1/2013" # it doesn't have to be a date with data
START_DATE = "08/04/2013"
#START_DATE = "08/04/2014"
# define the latest date to extract data or empty if using latest data available
#END_DATE = "10/20/2013" # it doesn't have to be a date with data
END_DATE = "08/03/2014"
#END_DATE = "07/30/2015"



FluVaccData = {}

# Define columns of interest with appropirate types conversion
# Note: week_start (Sat) is actually week_end
# Note: percentage in the data is actually fraction [0-1]
col_heading = {'count':int, 'week':int, 'name':str, 'year':int,
               'state':str,
               'fips_id':(lambda fips: fips.zfill(5)),
               'week_start':str,
               'percentage':(lambda perc: float(perc)*100)}

# Read data row by row and store only columns of interest
with open(os.path.join(root,filename), 'rb') as Obj:
    reader = csv.reader(Obj)
    header = reader.next() # header
    # indices of columns of interest
    col_idx = [header.index(col) for col in col_heading.keys()]
    for row in reader:
        # extract data of interest and do respective type conversion
        data = {header[col]:col_heading[header[col]](row[col])
                for col in col_idx}
        # convert year and week_start column to m/d/yr
        year = data['year']
        month = time.strptime(data['week_start'][-3:],'%b').tm_mon        
        if '-' in data['week_start']:
            date_month = int(data['week_start'][:-4])
        else:
            date_month = int(data['week_start'][:-3])
        # convert from government fiscal year to calendar year
        d = date(year, month, date_month)
        if (d  < date(year,9,1)) and (data['week']>20):
            # after Sep 1st, if there are already more than 20 weeks
            # then must be the next year.
            d = date(year+1, month, date_month)
        
        week_end = d.strftime('%m/%d/%Y')
        # key (fips, m/d/yr); val is a dict defined in col_heading
        FluVaccData[(data['fips_id'], week_end)] = data

# Rearrange data; key is FIPS and value is a dictionary whose
# key is date and value is percentage:
# {FIPS: {date: percentage}}
VaccPerc = {}
for key in FluVaccData.keys():
    # check if this week falls in the time of interest
    cur_week = datetime.strptime(key[1], '%m/%d/%Y')
    KEEP = True
    if START_DATE:
        if cur_week < datetime.strptime(START_DATE,'%m/%d/%Y'):
            KEEP = False
    if END_DATE:
        if cur_week > datetime.strptime(END_DATE,'%m/%d/%Y'):
            KEEP = False
    # store the vaccination data
    if KEEP:
        if key[0] in VaccPerc:
            VaccPerc[key[0]][key[1]] = FluVaccData[key]['percentage']
        else:
            VaccPerc[key[0]] = {}
            VaccPerc[key[0]][key[1]] = FluVaccData[key]['percentage']

# find ealiest and latest dates
dates = []
for fips in VaccPerc.keys():
    dates.extend([datetime.strptime(d, '%m/%d/%Y')
             for d in VaccPerc[fips].keys()])
earliest = min(dates)
latest = max(dates)

# filling in missing weeks, if any
for fips in VaccPerc.keys():
    w_end = earliest
    while w_end <= latest:
        if not (w_end.strftime('%m/%d/%Y') in VaccPerc[fips]):
            VaccPerc[fips][w_end.strftime('%m/%d/%Y')] = 'NaN'
        w_end = w_end + timedelta(days=7)

# use ordered dictionary to store data useful for analysis and storage in JSON
CountyCumVacPerc = {}
for fips in VaccPerc.keys():
    CountyCumVacPerc[fips] = OrderedDict(
        sorted(VaccPerc[fips].items(),
               key=lambda t: datetime.strptime(t[0], '%m/%d/%Y')))
