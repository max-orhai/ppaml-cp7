"""
Extract relevant meta data from the Tweets

(1) Load Twitter data in Gnip's Activity Streams format
(2) Divide the data according to the time frame of interest
(3) Save relevant data in Python Pickle format

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import csv
import simplejson as json
from datetime import datetime
import cPickle as pickle

## Twitter generated JSON file
root = "/home/syu/Work/ppaml/data/Twitter/"
#root = ""
fn_tweets = root + "twitter.json"

## Set the time frame of interest for tweets
earliest = datetime.strptime('09/29/2013','%m/%d/%Y')
#latest = datetime.strptime('08/1/2015','%m/%d/%Y')
latest = datetime.strptime('10/06/2013','%m/%d/%Y')

## Pickle file to store the resultant meta data
fn_meta = 'tmp.pkl'

count = 0
## Dictionary storing Tweet meta data
# {'tag:search.twitter.com,2005:362738615844995074':
#  {'lang': {'value': 'en'},
#  'location': {'address': {'country': 'United States',
#    'countryCode': 'US',
#    'locality': 'Maui Meadows',
#    'region': 'Hawaii'},
#   'displayName': 'Maui Meadows, Hawaii, United States',
#   'geo': {'coordinates': [-156.42664, 20.69871], 'type': 'point'},
#   'objectType': 'place'},
#  'time': {'date': 1,
#   'month': 8,
#   'str': '2013-08-01T00:56:40.000Z',
#   'year': 2013}}
tweet_db = {}
with open(fn_tweets, 'rb') as line_generator:
    for line in line_generator: # each line may contain a JSON object
        if line not in ['\n', '\r\n']: # ignore empty lines
            #ftxt.write(line)
            jobj = json.loads(line) # parse the JSON object
            ## only store data where location and time info is available
            if ('gnip' in jobj) & ('object' in jobj):
                if (('profileLocations' in jobj['gnip']) and
                    ('postedTime' in jobj['object'])):
                    # find time of the tweet
                    date_obj = datetime.strptime(
                        jobj['object']['postedTime'][0:19],
                        '%Y-%m-%dT%H:%M:%S')
                    ## only save data within the specified time frame
                    if (date_obj >= earliest) and (date_obj < latest):
                        key = jobj['id'] # primary key
                        # tweet location
                        tweet_db[key] = {}
                        tweet_db[key]['location'] = jobj['gnip']['profileLocations'][0]
                        # time of tweet
                        tweet_db[key]['time'] = {}
                        tweet_db[key]['time']['str'] = jobj['object']['postedTime']
                        tweet_db[key]['time']['year'] = date_obj.year
                        tweet_db[key]['time']['month'] = date_obj.month
                        tweet_db[key]['time']['date'] = date_obj.day
                        ## availability of language is optional
                        if 'language' in jobj['gnip']:
                            tweet_db[key]['lang'] = jobj['gnip']['language']
                        else:
                            tweet_db[key]['lang'] = 'NA'
                        '''
                        count = count + 1
                        if count >= 50:
                            break
                        '''

with open(fn_meta, 'wb') as fobj:
    pickle.dump(tweet_db, fobj, 2)

'''
with open('tmp.json', 'wb') as ftxt:
    json.dump(tweet_db, ftxt, indent=2*' ')
'''
