
import os
import csv
import numpy as np


# data directory
root = "/home/syu/Work/ppaml/data/ILI_CDC"

# CDC filename to read
filename = "ILINet.csv"

# file to store re-arranged CDC data
wfname = "ILINet_Rearranged.csv"

# data dictionary
dataDict = {}
# read CDC ILI data
with open(os.path.join(root,filename), 'rb') as Obj:
    reader = csv.reader(Obj)
    reader.next() # skip the first line
    header = reader.next() # header
    for row in reader:
        dataDict[(row[1], row[2], row[3])] = row[8]
        # (region, year, week): %unweighted ILI

# For each region, arrange the ILI rates chronologically
region = ["Region "+str(num) for num in range(1,11)]
year = range(2010,2016)
week = range(1,54)

regionILI = {}
row_name = [] # (yr, wk) of each element of regionILI
for rg in region:
    regionILI[rg] = []
    for yr in year:
        for wk in week:
            key = (str(rg), str(yr), str(wk))
            if key in dataDict:
                if rg == "Region 1":
                    # key exists (week 53 may not exist for some years)
                    row_name.append((int(yr), int(wk)))
                try:
                    # is a floating number ILI rate
                    regionILI[rg].append(float(dataDict[key]))
                except:
                    regionILI[rg].append('NA')

# save the re-arranged data
with open(os.path.join(root,wfname), 'wb') as Obj:
    writer = csv.writer(Obj)
    d=2*['']
    d.extend(region)
    writer.writerow(d) # header
    for row_idx in range(len(row_name)):
        row = list(row_name[row_idx]) # [yr, wk]
        for rg in region:
            row.append(regionILI[rg][row_idx]) # ILI for each region
        writer.writerow(row)

