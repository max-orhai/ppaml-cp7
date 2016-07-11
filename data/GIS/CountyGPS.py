"""

@author: syu
"""

import os
import csv
import matplotlib.pyplot as plt

root = ""
filename = "countyGPS.txt"

county_info = {}
with open(os.path.join(root,filename), 'rb') as gpsf:
    reader = csv.DictReader(gpsf, delimiter='\t')
    for row in reader:
        county_info[row["FIPS"]] = \
          [float(row["Latitude"]), float(row["Longitude"])]

