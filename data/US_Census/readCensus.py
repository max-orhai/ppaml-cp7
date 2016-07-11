
import os
import csv

# data directory
#root = "/home/syu/Work/ppaml/data/US Census"
root = "C:/Users/syu/project/1614/data/US Census"

# CDC filename to read
filename = "CensusData_partial.csv"

CensusData = {}
with open(os.path.join(root,filename), 'rb') as Obj:
    reader = csv.reader(Obj)
    header = reader.next() # header
    for row in reader:
        conv_row = [float(row[ic]) if '.' in row[ic] else int(row[ic])
                    for ic in range(1,len(row))]
        data = {header[ic]:conv_row[ic-1] for ic in range(1,len(row))}
        data['Name'] = row[0]
        CensusData[row[1]] = data
