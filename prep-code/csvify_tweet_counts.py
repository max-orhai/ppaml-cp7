from datetime import date
from sys import argv
from os import listdir
from collections import defaultdict
import json

from epiweek import epiweek


def ew(ddmmyyyy):
    mm, dd, yyyy = map(int, ddmmyyyy.split('/'))
    wk, yr = epiweek(date(yyyy, mm, dd))
    return '{:.02f}'.format(yr + 0.01 * wk)


def extract(fipsdict):
    for fips in fipsdict:
        nonzero_counts = {}
        for ddmmyyyy in fipsdict[fips]:  # ['No. of Tweets']:
            count = fipsdict[fips][ddmmyyyy]  # ['No. of Tweets'][ddmmyyyy]
            if count > 0:
                nonzero_counts[ew(ddmmyyyy)] = count
        if len(nonzero_counts) > 0:
            with open('../data/weather/' + fips + '.csv') as fh:
                header = fh.next()
            output = sorted(nonzero_counts.items())
            with open('../data/tweets/' + fips + '.csv', 'w') as csv:
                # csv.write('FIPS ' + fips + ': ' + fipsdict[fips]['Name'] + '\n\n')
                csv.write(header + '\n')
                csv.write('Year.Wk,tweets\n')
                for week, count in output:
                    csv.write(week + ',' + str(count) + '\n')


# for CSVs
def daterange():
    first = 9999
    last = 0
    dirname = '../data/tweets/'
    for filename in listdir(dirname):
        with open(dirname + filename) as fh:
            for line in fh:
                if line.startswith('20'):
                    week = float(line.split(',')[0])
                    if week < first:
                        first = week
                    if week > last:
                        last = week
    print('from %s to %s' % (first, last))

# for CSVs
def count_range(first_week, last_week):
    total = 0
    dirname = '../data/tweets/'
    for filename in listdir(dirname):
        with open(dirname + filename) as fh:
            for line in fh:
                if line.startswith('20'):
                    week, count = line[:-1].split(',')
                    if first_week <= float(week) <= last_week:
                        total += int(count)
    print total


def count_tweets_in_json(a_dict):
    total = 0
    for d in a_dict.itervalues():
        if 'No. of Tweets' in d:
            total += sum(d['No. of Tweets'].values())
        else:
            total += sum(d.values())
    print total


def remove_zero_counts(a_dict):
    for fips in a_dict:
        tweets = a_dict[fips]['No. of Tweets'].items()
        for (dt, v) in tweets:
            if v == 0:
                del a_dict[fips]['No. of Tweets'][dt]


def remove_all(a_dict, *keys):
    for fips in a_dict:
        for key in keys:
            if key in a_dict[fips]:
                del a_dict[fips][key]


def accumulate_tweets(*filenames):
    cumulative = defaultdict(dict)
    for filename in filenames:
        with open(filename) as fh:
            data = json.load(fh)
        for (fips, fdict) in data.iteritems():
            cumulative[fips].update(fdict['No. of Tweets'])
    with open('All_Tweets.json', 'w') as outfile:
        json.dump(cumulative, outfile, indent=2, sort_keys=True)


def read_in_pops(a_dict):
    with open('pops.csv') as csv:
        csv.next()  # discard header
        for line in csv:
            fips, pop2000, pop2005, pop2015 = line[:-1].split(',')
            a_dict[fips]['Population, 2000'] = int(pop2000)
            a_dict[fips]['Population, 2005 estimate'] = int(pop2005)
            a_dict[fips]['Population, 2015 estimate'] = int(pop2015)


def read_in_neighbors(a_dict):
    with open('county_adjacency_lower48.json') as adj:
        data = json.load(adj)
    for val in data.itervalues():
        fips = val[1]
        neighbors = sorted(val[2].values())
        a_dict[fips]['Adjacent counties'] = neighbors


if __name__ == '__main__':
    with open(argv[1]) as jsonfile:
        fipsdict = json.load(jsonfile)
    # extract(fipsdict)
    # count_range(*map(float, argv[1:]))
    # daterange()
    # count_tweets_in_json(fipsdict)
    # accumulate_tweets(*argv[1:])
    # remove_zero_counts(fipsdict)
    # remove_all(fipsdict, "No. of Tweets", "Vaccination percentage %")
    # read_in_pops(fipsdict)
    read_in_neighbors(fipsdict)

    with open(argv[1], 'w') as out:
        json.dump(fipsdict, out, indent=2, sort_keys=True)

