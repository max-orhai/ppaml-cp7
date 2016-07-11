"""
Augment county information including weekly vaccination data with tweet counts

(1) Load tweet meta data and corresponding counties
(2) Load county information
(3) Count weekly number of tweets in each county
(4) Augment the weekly vaccination data with the tweet counts
(5) Save the augmented data

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import cPickle as pickle
from datetime import datetime, timedelta
import simplejson as json
from collections import OrderedDict

#fn_cnty = 'rev_tmp.pkl'
#fn_tweet = 'tweets_20130801_20140731.pkl'

## pickle file storing tweet meta data
#root = '/home/syu/Work/ppaml/data/Twitter/'
#root = 'C:/Users/syu/project/1614/data/Twitter/'
root = '/projects/1614/data/Twitter/'
#fn_tweet = 'tweets_test_20130801.pkl'
#fn_tweet = root + 'tweets_20130801_20140731.pkl'
fn_tweet = root + 'tweets_20140801_20150731.pkl'
## pickle file storing county association of the corresponding tweet
#root = '/home/syu/Work/ppaml/data/Twitter/'
#root = 'C:/Users/syu/project/1614/data/Twitter/'
root = '/projects/1614/data/Twitter/'
#fn_cnty = 'geo_test_20130801.pkl'
#fn_cnty = root + 'tweetsGeo_20130801_20140731.pkl'
fn_cnty = root + 'tweetsGeo_20140801_20150731.pkl'
## JSON file storing county data covariates
#root = '/home/syu/Work/ppaml/data/Ch7_Data/'
#root = 'C:/Users/syu/project/1614/data/Ch7_Data/'
root = '/projects/1614/data/Ch7_Data/'
fn_vacc = root + 'Flu_Vacc_TEST.json'
## JSON file to store aggregated county data
root = ''
fn_vaccTweets = root + 'Flu_Vacc_Tweet_TEST.json'

# county association
with open(fn_cnty, 'rb') as fobj:
    reverseGeo = pickle.load(fobj)
# tweet meta data
with open(fn_tweet, 'rb') as fobj:
    tweets = pickle.load(fobj)

# End of week (Sat) before the earliest week for aggregation
# That is, the first week starts the day after the following date
earliest = datetime.strptime('08/03/2013', '%m/%d/%Y')

## count number of tweets by county by week
# {'51059': {('07/20/2013': 1), ('07/27/2013': 5)},
#  '51058': {('07/20/2013': 3), ('07/27/2013': 2)}}
TweetData = {}
for key in reverseGeo: # for every tweet (key of a tweet)
    # time of the tweet
    date_str = (str(tweets[key]['time']['month']) + '/' +
                str(tweets[key]['time']['date']) + '/' +
                str(tweets[key]['time']['year']))
    date_obj = datetime.strptime(date_str, '%m/%d/%Y')
    # county (FIPS) of the tweet
    fips = reverseGeo[key]['County']['FIPS']
    # weeks since the earliest date
    wk_since = 1 + int((date_obj-earliest-timedelta(days=1)).days / 7)
    # find the week in which the tweet occurs
    w_end = earliest + timedelta(days=7*wk_since)
    if fips in TweetData: # FIPS already occurred at least once before
        if w_end.strftime('%m/%d/%Y') in TweetData[fips]:
            # aggregate to the corresponding week and county
            TweetData[fips][w_end.strftime('%m/%d/%Y')] = (
                TweetData[fips][w_end.strftime('%m/%d/%Y')] + 1)
        else:
            TweetData[fips][w_end.strftime('%m/%d/%Y')] = 1
    else:
        TweetData[fips] = {}
        TweetData[fips][w_end.strftime('%m/%d/%Y')] = 1

## combine aggregated tweet counts with other county information

# read the county data
with open(fn_vacc, 'rb') as fobj:
    CntData = json.load(fobj, object_pairs_hook=OrderedDict)

## initialize the tweet field
#first_fips = '01001'
#wks = CntData[first_fips]['Vaccination percentage %'].keys()
#for fips in CntData:
#    CntData[fips]['No. of Tweets'] = {}
#    for wk_end in wks:
#        CntData[fips]['No. of Tweets'][wk_end] = 0
#
## combine the data
#for fips in CntData:
#    for wk_end in wks:
#        if fips in TweetData:
#            if wk_end in TweetData[fips]:
#                CntData[fips]['No. of Tweets'][wk_end] = TweetData[fips][wk_end]

# initialize the tweet field
first_fips = '01001'
wks = CntData[first_fips]['Vaccination percentage %'].keys()
tmpData = {}
for fips in CntData:
    tmpData[fips] = {}
    for wk_end in wks:
        tmpData[fips][wk_end] = 0

# combine the data
for fips in CntData:
    for wk_end in wks:
        if fips in TweetData:
            if wk_end in TweetData[fips]:
                tmpData[fips][wk_end] = TweetData[fips][wk_end]

for fips in CntData:
    CntData[fips]['No. of Tweets'] = OrderedDict(
        sorted(tmpData[fips].items(),
               key=lambda t: datetime.strptime(t[0], '%m/%d/%Y')))



# save the aggregated data
with open(fn_vaccTweets, 'wb') as fobj:
    json.dump(CntData, fobj, indent=1*' ')
