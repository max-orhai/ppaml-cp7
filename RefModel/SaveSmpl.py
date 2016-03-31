"""
Store county flu percentage in JSON file

@author: Ssu-Hsin Yu
"""

import simplejson as json
from collections import OrderedDict
from datetime import datetime, timedelta

## Save data in JSON format
#
# @param Data: data to store whose order is determined by CountyName and
#  state_date and end_date
# @param CountyName: dictionary defining the order in which each county
#  appear in the adjacency matrix:
#  {(county, state): (order, FIPS)}
# @param start_date: the earlies date (a date object) of the HHS week of which
#   data is generated
# @param end_date: the latest date (a date object) of the HHS week of which
#   data is generated
# @param[out] cty_ILI_info: returned ILI percentages of each county
#   {FIPS: {"Name": county name; "ILI Percentage %":
#                                  {m/d/yr: percentage; ...}}}
def SaveSmpl(Data, filename, CountyName, start_date, end_date):

    cty_ILI_info = {} # ordered dictionary of ILI percentages
    cty_data = {} # dictionary of ILI percentages
    
    num_counties = len(CountyName.keys())
    for name in CountyName.keys():
        fips = CountyName[name][1] # county FIPS code
        cty_data[fips] = {}
        cty_data[fips]["Name"] = name.decode("ISO-8859-1").encode('utf-8') # county name, state abbrv
        ILI_data = {}
        wk = 0
        w_end = start_date # starting date of the ILI week
        # extract the ILI data of the county and week
        while w_end <= end_date:
            ILI_data[w_end.strftime('%m/%d/%Y')] = float(
                Data[num_counties*wk+CountyName[name][0],])
            wk = wk + 1 # counter
            w_end = w_end + timedelta(days=7) # date

        # sort by date and then store in a dictionary
        cty_data[fips]["ILI percentage %"] = OrderedDict(
            sorted(ILI_data.items(),
                   key=lambda t: datetime.strptime(t[0],'%m/%d/%Y')))

    # sort by FIPS and then store in a dictionary
    cty_ILI_info = OrderedDict(
        sorted(cty_data.items(), key=lambda t: t[0]))


    # store the data to a JSON-formated file
    with open(filename, 'wb') as fobj:
        json.dump(cty_ILI_info, fobj, indent=1*' ')

    return cty_ILI_info

