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

    dirname = 'vaccinations/'
    files = listdir(dirname)

    regToCounts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for filename in files:
        try:
            reg = stateToReg[filename[:2]]
        except KeyError:
            continue
        with open(dirname + filename) as fh:
            for line in fh:
                if line.startswith('20'):
                    yrwk, all_tot, all_pct, old_tot, old_pct = line.split(',')
                    # weight each percent by the total
                    all_tot = float(all_tot)
                    all_pct = float(all_pct) * all_tot
                    old_tot = float(old_tot)
                    old_pct = float(old_pct) * old_tot

                    for (n, v) in [('old_tot', old_tot),
                                   ('old_pct', old_pct),
                                   ('all_tot', all_tot),
                                   ('all_pct', all_pct)]:
                        regToCounts[reg][yrwk][n] += v
                        regToCounts['USA'][yrwk][n] += v

    rows = []
    regs = range(1, 11) + ['USA']
    for wk in sorted(regToCounts['USA'].keys()):
        row = wk
        for reg in regs:
            all_tot = int(regToCounts[reg][wk]['all_tot'])
            old_tot = int(regToCounts[reg][wk]['old_tot'])
            all_pct = regToCounts[reg][wk]['all_pct']
            old_pct = regToCounts[reg][wk]['old_pct']
            if all_tot != 0:
                all_pct = all_pct / all_tot
            if old_tot != 0:
                old_pct = old_pct / old_tot
            row += ',{},{:.02f},{},{:.02f}'.format(
                all_tot, all_pct, old_tot, old_pct)
        rows.append(row)

    header = 'Year.Wk,' + ','.join(
        ['R{0:02}.all,R{0:02}.allV%,R{0:02}.65+,R{0:02}.65+V%'.format(r) for r in range(1, 11)])
    header += ',USA.all,USA.allV%,USA.65+,USA.65+V%'
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
    dirname = 'vaccinations/'
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
        distToCounts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        fips_prefix, districts = targets[state]
        filenames = [dirname + f for f in files if f.startswith(fips_prefix)]
        for fn in filenames:
            fips_suffix = fn[-7:-4]
            dist = districts.get(fips_suffix)
            with open(fn) as csv:
                for line in csv:
                    if line.startswith('20'):
                        yrwk, all_tot, all_pct, old_tot, old_pct = line.split(',')
                        # weight each percent by the total
                        all_tot = float(all_tot)
                        all_pct = float(all_pct) * all_tot
                        old_tot = float(old_tot)
                        old_pct = float(old_pct) * old_tot

                        for (n, v) in [('old_tot', old_tot),
                                       ('old_pct', old_pct),
                                       ('all_tot', all_tot),
                                       ('all_pct', all_pct)]:
                            if dist:
                                distToCounts[dist][yrwk][n] += v
                            distToCounts[state][yrwk][n] += v
        rows = []
        # this works because ints get sorted ahead of strings:
        dists = sorted(distToCounts.keys())
        for wk in sorted(distToCounts[state].keys()):
            row = wk
            for dist in dists:
                all_tot = int(distToCounts[dist][wk]['all_tot'])
                old_tot = int(distToCounts[dist][wk]['old_tot'])
                all_pct = distToCounts[dist][wk]['all_pct']
                old_pct = distToCounts[dist][wk]['old_pct']
                if all_tot != 0:
                    all_pct = all_pct / all_tot
                if old_tot != 0:
                    old_pct = old_pct / old_tot
                row += ',{},{:.02f},{},{:.02f}'.format(
                    all_tot, all_pct, old_tot, old_pct)
            rows.append(row)

        dists.remove(state)
        header = 'Year.Wk,' + ','.join(
            ['D{0:02}.all,D{0:02}.allV%,D{0:02}.65+,D{0:02}.65+V%'.format(d) for d in dists])
        if dists:
            header += ','
        header += '{0}.all,{0}.allV%,{0}.65+,{0}.65+V%'.format(state)
        with open(state + '-vaccinations.csv', 'w') as csv:
            csv.write(header + '\n')
            for row in rows:
                csv.write(row + '\n')


if __name__ == '__main__':
    # hhs()
    states()
