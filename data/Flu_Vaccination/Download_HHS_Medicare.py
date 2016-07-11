# -*- coding: utf-8 -*-
"""
Download file from HHS Flu Vaccinations of Medicare Beneficiaries
http://www.hhs.gov/nvpo/flu-vaccination-map/

"""

import urllib, json
import csv

# specify whether we need data on the state level or the county level
ResLevel = 'state'

# HHS url
#url = "http://flu-vaccination-map.hhs.gov/api/v1/states.json?year=xxxx"
#url = "http://flu-vaccination-map.hhs.gov/api/v1/counties.json?year=xxxx"
url = "http://flu-vaccination-map.hhs.gov/api/v1/counties.json?year=xxxx&sf="

# url depends on the level of resolution desired
if ResLevel.lower()=='state':
    url = "http://flu-vaccination-map.hhs.gov/api/v1/states.json?year=xxxx"
elif ResLevel.lower()=='county':
    url = "http://flu-vaccination-map.hhs.gov/api/v1/counties.json?year=xxxx&sf="
else:
    raise IOError('wrong resolution specified')

# data is only available from 2012 or later
#all_year = ('2010', '2011', '2012', '2013', '2014', '2015')
all_year = ('2015',)
state_fips_id = ()

all_data = []
all_metadata = []


# read data for all the years specified and aggregated in a list
for year in all_year:
    url_cur = url.replace("xxxx", year)
    print url_cur
    if ResLevel.lower()=='state':
        response = urllib.urlopen(url_cur)
        data = json.loads(response.read())
        all_data.extend(data['results'])
        all_metadata.extend(data['metadata'])
    elif ResLevel.lower()=='county':
        # loop over all states; otherwise the county data is too big for HHS to handle
        # Each state has a FIPS number that is between 1 and 57 excluding Puerto Rico (72)
        for state_fips in range(1,57):
            print url_cur+str(state_fips)
            response = urllib.urlopen(url_cur+str(state_fips))
            data = json.loads(response.read())
            all_data.extend(data['results'])
            all_metadata.extend(data['metadata'])

# save the data (type dictionary) in the csv format
with open('medicare_flu_vac.csv', 'wb') as csvfile:
    fieldnames = all_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_data)
