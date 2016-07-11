# Combine data from US_Census and Flu_Vaccination into a dictionary
# and store in a JSON-formated file

import os
import sys
import simplejson as json
from collections import OrderedDict
import matplotlib.pyplot as plt


#sys.path.append('/home/syu/Work/ppaml/software/data/US_Census')
#sys.path.append('/home/syu/Work/ppaml/software/data/Flu_Vaccination')
sys.path.append('C:/Users/syu/project/1614/software/code_repo/data/US_Census')
sys.path.append('C:/Users/syu/project/1614/software/code_repo/data/Flu_Vaccination')


# data directory
root = ""
# filename to store JSON data
#filename = "Flu_Vacc.json"
#filename = "Flu_Vacc_Syn.json"
#filename = "Flu_Vacc_TEST.json"
filename = "Flu_Vacc_TRAIN.json"

import readCensus as rc
import readFluVacc as rf

# attach cumulative vaccination percentage to the census data
for key in rc.CensusData.keys():
    if key in rf.VaccPerc:
        rc.CensusData[key]['Vaccination percentage %'] = (
        rf.CountyCumVacPerc[key])

# sort the data in FIPS
CountyInfo = OrderedDict(sorted(rc.CensusData.items(), key=lambda t:t[0]))

# store the data to a JSON-formated file
with open(os.path.join(root,filename), 'wb') as fobj:
    #json.dump(CountyInfo, fobj, sort_keys=True, indent=1*' ')
    json.dump(CountyInfo, fobj, indent=1*' ')

# read the data from a JSON-formated file
with open(os.path.join(root,filename), 'rb') as fobj:
    cdata = json.load(fobj, object_pairs_hook=OrderedDict)


#for fips in cdata.keys():
#    plt.clf()
#    if 'Vaccination percentage %' in cdata[fips]:
#        plt.plot(cdata[fips]['Vaccination percentage %'].values())
#        plt.title(fips + cdata[fips]['Name'])
#        plt.pause(0.01)
#    else:
#        plt.title(fips + cdata[fips]['Name'])
#        plt.pause(0.01)
