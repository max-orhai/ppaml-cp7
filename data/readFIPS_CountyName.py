# Read from a file that contains all of the counties in the US
# Construct a dictionary whose key is the state name abbreviation and
# whose value contains the state name, state FIPS code and a dictionary
# that contains all of the counties in the state. The county
# dictionary has each county's FIPS code as the key and name of the
# county as the value.
#
# Ssu-Hsin Yu
# syu@ssci.com

import os
import csv
import re
from collections import OrderedDict
import us
import simplejson as json

# data directory
root = "/home/syu/Work/ppaml/data/US Census"

# CDC filename to read
filename = "FIPS_CountyName.txt"

# data directory
state_root = ""
# filename to store JSON data
state_info = "StateInfo.json"


data = {}
# the data dictionary has the following content
# {'Name': full state name, 'FIPS': state FIPS code,
#  'Counties': {FIPS Code: county name, ...}}
with open(os.path.join(root,filename), 'rb') as fObj:
    for line in fObj:
        # state FIPS code
        m = re.search("([0-9]+)",line)
        FIPS = m.group(1)
        # check if this line contains either a county or a state
        # That is, for example either "Autauga County, AL" or
        # "ALABAMA" (or "UNITED STATES")
        m = re.search("(?<=, )([A-Z]+)",line)
        if m:
            # county, state abbreviation
            StateAbbrv = m.group(1)
            m = re.search(" ([a-zA-Z \.\-\']+)",line)
            County = m.group(1)
            # initialize a state to store data
            if StateAbbrv not in data:
                data[StateAbbrv] = {}
                data[StateAbbrv]["Counties"] = {}
            # store the county in the corresponding state
            data[StateAbbrv]["Counties"][FIPS] = County
        else:
            # state
            m = re.search(" ([a-zA-Z ]+)",line)
            if m.group(1) != "UNITED STATES":
                State = m.group(1)
                StateAbbrv = us.states.lookup(unicode(State)).abbr
                # initialize a state to store data
                if StateAbbrv not in data:
                    data[StateAbbrv] = {}
                    data[StateAbbrv]["Counties"] = {}
                # store the full state name and state FIPS
                data[StateAbbrv]["Name"] = State
                data[StateAbbrv]["FIPS"] = FIPS

StateInfo = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

# store the data to a JSON-formated file
with open(os.path.join(state_root,state_info), 'wb') as fobj:
    json.dump(StateInfo, fobj, indent=1*' ')
