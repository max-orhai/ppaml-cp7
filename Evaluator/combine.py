#! /usr/bin/env python

from sys import argv

# make a single forecast CSV with a column for each population
lines = [l[:-1] for l in open(argv[1])]  # strip newlines
pops = []
this_pop_weeks = []
for l in lines:
    if l.startswith('>>'):
        this_pop_weeks = []
    elif l == '':
        pops.append(this_pop_weeks)
    else:
        this_pop_weeks.append(l)
pops.append(this_pop_weeks)

first = pops[0]
for pop in pops[1:]:
    for (l, i) in zip(pop, range(52)):
        row = l.split(',')
        twk = first[i].split(',', 1)[0]
        assert row[0] == twk, (row[0], twk)  # weeks must match
        first[i] += ',' + ','.join(row[1:])

for l in first:
    print(l)
