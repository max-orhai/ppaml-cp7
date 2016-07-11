
import GIS_Utilities
import numpy as np
import scipy.sparse as spa

import matplotlib.pyplot as plt
import networkx as nx

import simplejson as json
from collections import OrderedDict

# file to save county adjacency info in JSON
fn = 'county_adjacency_lower48.json'

# data directory
root = "C:/Users/syu/project/1614/data/GIS"
#root = "/home/syu/Work/ppaml/data/GIS"

# construct county adjacency matrix
#filename = "county_adjacency.txt"
#filename = "county_adjacency_MA.txt"
filename = "county_adjacency_lower48.txt"
(AdjMatrix, CountyName, CountyAdjDict)=GIS_Utilities.ConstructCountyAdjMatrix(filename,root)

Dw = np.squeeze(np.asarray(AdjMatrix.sum(axis=1)))
StrucMat = spa.spdiags(Dw,0,AdjMatrix.shape[0],AdjMatrix.shape[0]) - AdjMatrix

import StrucMat as sm
num_weeks = 20
sz = 0.5*np.ones([AdjMatrix.shape[0]*(num_weeks-1),])
#cov = sm.StrucMatR_FromRDf_Inhomo(num_weeks, StrucMat, sz, isSparse = True)
cov = sm.StrucMatR_FromRDf(num_weeks, StrucMat, isSparse = True)

# check
row=1
cov[row,cov[row].nonzero()[1]].todense()

# load county coordinates
filename = "countyGPS.txt"
county_info = GIS_Utilities.ReadCountyLatLon(filename,root)
county_gps = county_info.values()
plt.figure(1)
plt.clf()
plt.scatter([lon for lat,lon in county_gps], [lat for lat,lon in county_gps])


# plot adjacency matrix graph using GPS coordinates
plt.figure(2)
plt.clf()
pos = {}
for name in CountyName.keys():
    fips = CountyName[name][1]
    idx_adjMatrix = CountyName[name][0]
    pos[idx_adjMatrix] = county_info[fips][::-1] # [lon,lat]

G=nx.from_scipy_sparse_matrix(AdjMatrix)
nx.draw_networkx(G,pos,with_labels=False,node_size=6)

# sorted by FIPS code of each county
AdjJson = OrderedDict(sorted(CountyAdjDict.items(), key=lambda t: t[1][1]))
# save the county adjacency data in JSON
with open(fn, 'wb') as fobj:
    json.dump(AdjJson, fobj, indent=2*' ')
