"""
Create a JSON file that list all of counties belonging to each HHS
region, to each selected state and to each district in selected states.

It reads two files
1. a CSV file ("GeoAssociation.csv") that contains the mapping
from HHS regions and districts to respectively states and counties.
The file also contains the states, specified in 2-letter state
abbreviations, whose state-to-county mappings are to be included in
the output file.
2. a JSON file ("StateInfo.json") that contains the mapping
from states to their corresponding counties.

It saves the mapping results to a JSON file "Region2CountyMap.json"

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import os
import csv
import simplejson as json
from collections import OrderedDict

# file containing mapping from regions and districts
#root = "/home/syu/Work/ppaml/data/Aggregated_Data/"
root = "C:/Users/syu/project/1614/data/Ch7_Data/Aggregated_Data/"
fn_region = root + "GeoAssociation.csv"

# file containing state to counties mapping
root = "C:/Users/syu/project/1614/data/"
fn_state = root + "StateInfo.json"

# file to store regions/districts to counties mapping
root = ""
fn_map = root + "Region2CountyMap.json"


## read the mapping from HHS regions to states and from
# districts in selected states to counties
# The mapping is stored in a dictionary
# {region/disctrict name: [states or county names]}
# For example, {"HHS Region 1": ["CT", "ME", "MA", "NH", "RI", "VT"],
#               "MS District 1": ["Coahoma", ...],...}
RegionAsso = {}
with open(fn_region, 'rb') as fobj:
    reader = csv.reader(fobj, skipinitialspace=True)
    for row in reader:
        RegionAsso[row[0]] = [row[i] for i in range(1,len(row))]

## read the mapping from state to counties
# StateCntAsso: {State Abbrv: {"FIPS": fips, "Name": full state name,
#                      "Counties": {"FIPS": county name}}}
with open(fn_state, 'rb') as fobj:
    StateCntyAsso = json.load(fobj)


## Dictionary storing mapping from HHS region/district to counties
# {"HHS Region 1": {'55129': 'Washburn County', ....},
#  "MS District 1": {'...': '.....', ....}, ...}
RegCntyAsso = {}
# re-formulate mapping from HHS regions or districts to counties
for premap in RegionAsso.items():
    RegCntyAsso[premap[0]] = {}
    if "HHS Region" in premap[0]: # it's a HHS region
        for state in premap[1]:
            if state not in ['AK', 'PR', 'HI', 'VI']:
                # append the counties from each state
                RegCntyAsso[premap[0]].update(
                    StateCntyAsso[state]["Counties"])
    elif len(premap[0])==2: # 2-letter state name
        # append the counties from each state
        RegCntyAsso[premap[0]].update(
            StateCntyAsso[premap[0]]["Counties"])        
    else: # it's a district in a state
        for county in premap[1]:
            # the first 2 letters in the district name are state abbrv
            for ct in StateCntyAsso[premap[0][:2]]["Counties"].items():
                if ct[1] == county + ' County':
                    RegCntyAsso[premap[0]].update({ct[0]: ct[1]})
                    break

RegCntyAsso = OrderedDict(sorted(RegCntyAsso.items(), key=lambda t: t[0]))

# store the data to a JSON-formated file
with open(fn_map, 'wb') as fobj:
    json.dump(RegCntyAsso, fobj, indent=1*' ')
