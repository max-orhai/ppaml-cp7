#! /usr/bin/env python

from csv import DictReader
from sys import argv
from os import listdir

# score the forecasts output by combine.py against a single combined reference
assert len(argv) == 3, 'usage: eval2.py [forecast dir] [reference CSV]'


def mse(xys):
    def sqerr((x, y)):
        return (x - y) ** 2
    return sum(map(sqerr, xys)) / len(xys)


def table(filename):
    return {row['Week']: row for row in DictReader(open(filename))}

ref = table(argv[2])


def turn(tbl):
    turned = {}
    for i in range(len(tbl)):
        turned[i] = {}
    for (i, week) in zip(range(len(turned)), sorted(tbl.keys())):
        for pop in tbl[week]:
            if pop != 'Week':
                turned[i][pop] = (float(tbl[week][pop]),
                                  float(ref[week][pop]))
    return turned

targets = {}
for filename in listdir(argv[1]):
    if not filename.startswith('.'):
        pred_week = filename[-11:-4]  # assuming *YYYY.WW.csv
        targets[pred_week] = table(argv[1] + '/' + filename)

fcwd = {}
for t in targets:
    tt = turn(targets[t])
    for i in tt:
        if i not in fcwd:
            fcwd[i] = {}
        for pop in tt[i]:
            p = pop.split('.')[0]
            if pop not in fcwd[i]:
                fcwd[i][p] = []
            fcwd[i][p].append(tt[i][pop])

for i in fcwd:
    for pop in fcwd[i]:
        fcwd[i][pop] = round(mse(fcwd[i][pop]), 3)

ks = sorted(fcwd[0].keys())
print(','.join(['WeeksAhead'] + ks))
for i in fcwd:
    print(','.join([str(i)] + [str(fcwd[i][k]) for k in ks]))
