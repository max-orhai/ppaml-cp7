from os import listdir
from collections import defaultdict

import ms_districts as ms
import tn_districts as tn
import nj_counties as nj


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

    dirname = 'tweets/'
    files = listdir(dirname)

    regToCounts = {k: defaultdict(int) for k in range(1, 11)}
    regToCounts['US'] = defaultdict(int)
    for filename in files:
        try:
            reg = stateToReg[filename[:2]]
        except KeyError:
            continue
        with open(dirname + filename) as fh:
            for line in fh:
                if line.startswith('20'):
                    yrwk, count = line.split(',')
                    count = int(count)
                    regToCounts[reg][yrwk] += count
                    regToCounts['US'][yrwk] += count

    rows = []
    cols = range(1, 11) + ['US']
    for wk in sorted(regToCounts['US'].keys()):
        row = wk
        for col in cols:
            row += (',' + str(regToCounts[col][wk]))
        rows.append(row)

    print('Year.Wk,R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,USA')
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
    dirname = 'tweets/'
    files = listdir(dirname)
    targets = {
        "MS": ("28", flatten(ms.districtToCounties)),
        "TN": ("47", flatten(tn.districtToCounties)),
        "NJ": ("34", flatten(nj.counties)),
        "NC": ("37", {}),  # state only
        "RI": ("44", {}),  # state only
        "TX": ("48", {}),  # state only
    }
    for state in targets:
        distToCounts = defaultdict(lambda: defaultdict(int))
        fips_prefix, districts = targets[state]
        filenames = [dirname + f for f in files if f.startswith(fips_prefix)]
        for fn in filenames:
            fips_suffix = fn[-7:-4]
            dist = districts.get(fips_suffix)
            with open(fn) as csv:
                for line in csv:
                    if line.startswith('20'):
                        yrwk, count = line.split(',')
                        count = int(count)
                        if dist:
                            if dist < 10:
                                dist = '0' + str(dist)
                            distToCounts['D' + str(dist)][yrwk] += count
                        distToCounts[state][yrwk] += count
        rows = []
        cols = sorted(distToCounts.keys())
        for wk in sorted(distToCounts[state]):
            row = wk
            for col in cols:
                row += (',' + str(distToCounts[col][wk]))
            rows.append(row)
            with open(state + '-tweets.csv', 'w') as csv:
                csv.write(','.join(['Year.Wk'] + cols) + '\n')
                for row in rows:
                    csv.write(row + '\n')


if __name__ == '__main__':
    # hhs()
    # states()

