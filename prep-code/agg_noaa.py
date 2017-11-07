from os import listdir
from sys import stderr
from collections import defaultdict
import json

import ms_districts as ms
import tn_districts as tn
import nj_counties as nj



def load_num_stations():
    with open('num-stations.json') as fh:
        ns = json.load(fh)
    return ns


# aggregate counts for HHS regions 1-10
def hhs():
    regToStates = {
        1: ['09', '23', '25', '33', '44', '50'],
        2: ['34', '36'],
        3: ['10', '11', '24', '42', '51', '54'],
        4: ['01', '12', '13', '21', '28', '37', '45', '47'],
        5: ['17', '18', '26', '27', '39', '55'],
        6: ['05', '22', '35', '40', '48'],
        7: ['19', '20', '29', '31'],
        8: ['08', '30', '38', '46', '49', '56'],
        9: ['04', '06', '32'],
        10: ['16', '41', '53']
    }

    stateToReg = {}
    for r in regToStates:
        for s in regToStates[r]:
            stateToReg[s] = r

    dirname = 'weather/'
    files = listdir(dirname)
    weights = load_num_stations()

    regToCounts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for filename in files:
        try:
            reg = stateToReg[filename[:2]]
        except KeyError:
            continue
        weight = weights[filename[:5]]
        with open(dirname + filename) as fh:
            for line in fh:
                if line[:2] in ('19', '20'):
                    try:
                        yrwk, tmax, tmin, prcp = line[:-1].split(',')
                        tmax = 0 if tmax in '' else float(tmax) * weight
                        tmin = 0 if tmin == '' else float(tmin) * weight
                        prcp = 0 if prcp == '' else float(prcp) * weight
                    except ValueError:
                        stderr.write(dirname + filename + ': ' + line)
                        raise ValueError
                    for (n, v) in [('weight', weight),
                                   ('tmax', tmax),
                                   ('tmin', tmin),
                                   ('prcp', prcp)]:
                        regToCounts[reg][yrwk][n] += v
                        regToCounts['USA'][yrwk][n] += v

    rows = []
    regs = range(1, 11) + ['USA']
    for wk in sorted(regToCounts['USA'].keys()):
        row = wk
        for reg in regs:
            weight = regToCounts[reg][wk]['weight']
            tmax = regToCounts[reg][wk]['tmax']
            tmin = regToCounts[reg][wk]['tmin']
            prcp = regToCounts[reg][wk]['prcp']
            if weight != 0:
                tmax = tmax / weight
                tmin = tmin / weight
                prcp = prcp / weight
            row += ',{:.02f},{:.02f},{:.02f}'.format(
                tmax, tmin, prcp)
        rows.append(row)

    header = 'Year.Wk,' + ','.join(
        ['R{0:02}.Tmax,R{0:02}.Tmin,R{0:02}.prcp'.format(r) for r in range(1, 11)])
    header += ',USA.Tmax,USA.Tmin,USA.prcp'
    print(header)
    for row in rows:
        print(row)


def flatten(cmap):
    flat = {}
    for k in cmap:
        for co in cmap[k]:
            flat[co[1]] = k
    return flat


# aggregate counts for each state and its subdivisions, if any
def states():
    dirname = 'weather/'
    files = listdir(dirname)
    weights = load_num_stations()
    targets = {
        "MS": ("28", flatten(ms.districtToCounties)),
        "TN": ("47", flatten(tn.districtToCounties)),
        "NJ": ("34", flatten(nj.counties)),
        "NC": ("37", {}),  # state only
        "RI": ("44", {}),  # state only
        "TX": ("48", {}),  # state only
    }
    for state in targets:
        distToCounts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        fips_prefix, districts = targets[state]
        filenames = [dirname + f for f in files if f.startswith(fips_prefix)]
        for fn in filenames:
            fips_suffix = fn[-7:-4]
            dist = districts.get(fips_suffix)
            weight = weights[fips_prefix + fips_suffix]
            with open(fn) as csv:
                for line in csv:
                    if line[:2] in ('19', '20'):
                        yrwk, tmax, tmin, prcp = line[:-1].split(',')
                        tmax = 0 if tmax in '' else float(tmax) * weight
                        tmin = 0 if tmin == '' else float(tmin) * weight
                        prcp = 0 if prcp == '' else float(prcp) * weight
                        for (n, v) in [('weight', weight),
                                       ('tmax', tmax),
                                       ('tmin', tmin),
                                       ('prcp', prcp)]:
                            if dist:
                                distToCounts[dist][yrwk][n] += v
                            distToCounts[state][yrwk][n] += v
        rows = []
        # this works because ints get sorted ahead of strings:
        dists = sorted(distToCounts.keys())
        for wk in sorted(distToCounts[state].keys()):
            row = wk
            for dist in dists:
                weight = distToCounts[dist][wk]['weight']
                tmax = distToCounts[dist][wk]['tmax']
                tmin = distToCounts[dist][wk]['tmin']
                prcp = distToCounts[dist][wk]['prcp']
                if weight != 0:
                    tmax = tmax / weight
                    tmin = tmin / weight
                    prcp = prcp / weight
                row += ',{:.02f},{:.02f},{:.02f}'.format(
                    tmax, tmin, prcp)
            rows.append(row)

        dists.remove(state)
        header = 'Year.Wk,' + ','.join(
            ['D{0:02}.Tmax,D{0:02}.Tmin,D{0:02}.prcp'.format(d) for d in dists])
        if state == 'NJ':
            header = header.replace('D', 'C')
        if dists:
            header += ','
        header += '{0}.Tmax,{0}.Tmin,{0}.prcp'.format(state)
        with open(state + '-weather.csv', 'w') as csv:
            csv.write(header + '\n')
            for row in rows:
                csv.write(row + '\n')


def scrub_geo():
    with open('geography.json') as fh:
        geo = json.load(fh)
    with open('indices.json') as fh:
        ndx = json.load(fh)
    new_geo = {'indices': ndx, 'data': {}}
    for fn in ndx:
        for r in ndx[fn]:
            for fips in ndx[fn][r]:
                new_geo['data'][fips] = geo[fips]
    with open('demographics.json', 'w') as out:
        json.dump(new_geo, out, indent=2, sort_keys=True)


if __name__ == '__main__':
    # hhs()
    # states()
    scrub_geo()
