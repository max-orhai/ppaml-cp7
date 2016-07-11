"""
Given latitude and longitude, find the corresponding county

(1) read the meta data of tweets stored in a dictionary
(2) query FCC site to convert lat/lon to county
(3) save the data in a dictionary (same key as the tweet
    meta data) in Python Pickle format

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import urllib, json
import simplejson as json
import cPickle as pickle

# URL query
url = ("http://data.fcc.gov/api/block/2010/find?" +
       "format=json&latitude=LATITUDE&longitude=LONGITUDE")

## File storing Tweet meta data
#fn = 'tweets_20130801_20140731.pkl'
fn = 'tweets_test_20130801.pkl'

## file to store corresponding county info
fn_cnty = 'geo_test_20130801.pkl'

count = 0
## Dictionary storing the county information of the corresponding lat/lon
# {Tweet key: {{'Block': {'FIPS': '150090303031012'},
#  'County': {'FIPS': '15009', 'name': 'Maui'},
#  'State': {'FIPS': '15', 'code': 'HI', 'name': 'Hawaii'},
#  'executionTime': '105',
#  'status': 'OK'}
reverseGeo = {}
with open(fn, 'rb') as fobj:
    db = pickle.load(fobj)
    num_tw = len(db)
    for key in db: # each tweet meta data
        longitude = str(db[key]['location']['geo']['coordinates'][0])
        latitude = str(db[key]['location']['geo']['coordinates'][1])
        url_cur = url
        url_cur = url_cur.replace("LONGITUDE", longitude)
        url_cur = url_cur.replace("LATITUDE", latitude)
        response = urllib.urlopen(url_cur) # query FCC URL
        data = json.loads(response.read())
        reverseGeo[key] = data

        count = count + 1
        if (count % 100) == 0: # update progress
            print str(count)+'/'+str(num_tw)

        if (count % 5000) == 0: # periodic save
            with open('rev_tmp.pkl', 'wb') as fobj:
                pickle.dump(reverseGeo, fobj, 2)
        '''
        if count >= 10:
            break
        '''

with open(fn_cnty, 'wb') as fobj:
    pickle.dump(reverseGeo, fobj, 2)

'''
url_cur = url
url_cur = url_cur.replace("LONGITUDE", str(db[a[0]]['location']['geo']['coordinates'][0]))
url_cur = url_cur.replace("LATITUDE", str(db[a[0]]['location']['geo']['coordinates'][1]))

response = urllib.urlopen(url_cur)
data = json.loads(response.read())
'''
