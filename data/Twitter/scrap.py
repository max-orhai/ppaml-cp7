'''
import cPickle as pickle
import matplotlib.pyplot as plt

with open('rev_tmp.pkl', 'rb') as fobj:
    reverseGeo = pickle.load(fobj)

a=reverseGeo.keys()

with open('tweets_20130801_20140731.pkl', 'rb') as fobj:
    tweets = pickle.load(fobj)

lonlat = [tweets[key]['location']['geo']['coordinates']
          for key in reverseGeo.keys()]
x=[lon[0] for lon in lonlat]
y=[lon[1] for lon in lonlat]
plt.plot(x,y,'.')
'''

import simplejson as json
from collections import OrderedDict
from datetime import datetime
import csv
import plotCountyData

## map file
#root='/home/syu/software/MakeMap/'
root = 'C:/Users/syu/project/1614/data/Misc/'
map_file = root + 'USA_Counties_with_FIPS_and_names.svg'

## JSON file storing aggregated county data
root='C:/Users/syu/project/1614/data/Ch7_Data/'
fn_vaccTweets = root + 'Flu_Vacc_Tweet_TRAIN.json'

# read the county data
with open(fn_vaccTweets, 'rb') as fobj:
    CntData = json.load(fobj, object_pairs_hook=OrderedDict)

first_fips = '01001' # a valid FIPS

# age weighting
wgt_under18 = 0
wgt_btwn18and65 = ((37+25+12)/3.)/100.
wgt_over65 = 10/100.

# find the data to plot
#wks = range(0,52,10)
#data_to_plot = 'Vaccination percentage %'
data_to_plot = 'No. of Tweets'
wks = sorted(CntData[first_fips][data_to_plot].keys(),
             key=lambda t: datetime.strptime(t, '%m/%d/%Y')) # sorted weeks in keys
wks_to_plot = wks[::5]
for wk in wks_to_plot:
    data = {}
    tmp_state_data = {}
    pop_state = {}
    state_data = {}
    outmap_fn = data_to_plot + wk.replace('/','') + '.svg'
    for fips in CntData:
        try:
            # age weighted population
            frac_under18 = CntData[fips]['Persons under 18 years, percent, 2013']/100
            frac_over65 = CntData[fips]['Persons 65 years and over, percent, 2013']/100
            frac_btwn18and65 = 1 - frac_under18 - frac_over65
            pop = CntData[fips]['Population, 2014 estimate']
            if data_to_plot is 'No. of Tweets':
                weighting = (frac_under18*wgt_under18 + frac_btwn18and65*wgt_btwn18and65 + frac_over65*wgt_over65)
                pop_weighted = pop*weighting
                #pop_weighted = float(pop)
                #pop_weighted = 1.
                data[fips] = CntData[fips][data_to_plot][wk]/pop_weighted # county data
                # aggregate county data to each state
                if fips[:2] not in tmp_state_data:
                    tmp_state_data[fips[:2]] = CntData[fips][data_to_plot][wk]
                    pop_state[fips[:2]] = pop
                else:
                    tmp_state_data[fips[:2]] = tmp_state_data[fips[:2]] + CntData[fips][data_to_plot][wk]
                    pop_state[fips[:2]] = pop_state[fips[:2]] + pop
            else:
                pop_weighted = 1.
                data[fips] = CntData[fips][data_to_plot][wk]/pop_weighted
        except:
            continue
        
    for fips in data:
        # all counties in a state share the same state value
        state_data[fips] = 1e5*(float(tmp_state_data[fips[:2]]) / pop_state[fips[:2]])

    if data_to_plot is 'No. of Tweets':
        #plotCountyData.plotCountyData(data, map_file, outmap_fn, max_val=0.002)
        plotCountyData.plotCountyData(state_data, map_file, outmap_fn, max_val=5)
    elif data_to_plot is 'Vaccination percentage %':
        plotCountyData.plotCountyData(data, map_file, outmap_fn, min_val=0, max_val=85.0)

'''
root='/home/syu/software/MakeMap/'
map_file = root + 'USA_Counties_with_FIPS_and_names.svg'
#data_file = root + 'unemployment09.csv'

data = {}
with open(data_file, 'rb') as fobj:
    reader = csv.reader(fobj, delimiter=",")
    for row in reader:
        try:
            full_fips = row[1] + row[2]
            rate = float( row[8].strip() )
            data[full_fips] = rate
        except:
            pass

plotCountyData.plotCountyData(data, map_file)
'''
