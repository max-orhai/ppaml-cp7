from json import load
from os import listdir
from sys import argv
from collections import defaultdict

from epiweek import ew


months = {
    'JAN': 1,
    'FEB': 2,
    'MAR': 3,
    'APR': 4,
    'MAY': 5,
    'JUN': 6,
    'JUL': 7,
    'AUG': 8,
    'SEP': 9,
    'OCT': 10,
    'NOV': 11,
    'DEC': 12
}

def mmwr(d):
    # week 1 is the week defined to start August 1, regardless of its weekday
    # year 2016, week 22 starts 31 DEC
    # year 2016, week 23 starts 07 JAN and thus falls entirely in 2017!
    year = d['year']
    ddmmm = d['week_start']
    day = int(ddmmm[:2])
    month = months[ddmmm[2:]]
    if month < 8:
        year += 1
    week, year = ew(year, month, day)
    if week == 31 and year in (2012, 2013, 2014):
        year += 1
    return '{:.02f}'.format(year + 0.01 * week)



def csvify(dirname='vaccinations'):
    for filename in listdir(dirname):
        with open(dirname + '/' + filename) as fh:
            try:
                data = load(fh)
            except ValueError:
                print(dirname + '/' + filename)
                continue
        weeks = defaultdict(dict)
        for datum in data:
            status = datum['medicare_status'] + '.'
            week = mmwr(datum)
            for k in 'percentage', 'count':
                weeks[week][status + k] = datum[k]

        rows = []
        for week in weeks:
            a_total = str(weeks[week].get('A.count', ''))
            o_total = str(weeks[week].get('O.count', ''))
            a_perct = '{:.02f}'.format(100 * weeks[week].get('A.percentage', 0))
            o_perct = '{:.02f}'.format(100 * weeks[week].get('O.percentage', 0))
            rows.append(','.join([week, a_total, a_perct, o_total, o_perct]))
        rows.sort()

        filename = filename.replace('.json', '.csv')

        with open('../data/weather/' + filename) as tweetfile:
            header = tweetfile.next()

        with open(dirname + '/' + filename, 'w') as csv:
            csv.write(header + '\n')
            csv.write('Year.Wk,All.Total,All.%Vacc,Over64.Total,Over64.%Vacc\n')
            for row in rows:
                csv.write(row + '\n')


def fix(dirname='vaccinations'):
    for filename in listdir(dirname):
        with open(dirname + '/' + filename) as infile:
            with open(dirname + '/' + filename.replace('.xx', ''), 'w') as outfile:
                l1 = l2 = l3 = ''
                for line in infile:
                    l1 = l2
                    l2 = l3
                    l3 = line
                    if l1 + l2 + l3 == '  }\n]\n[\n':
                        outfile.write('  },\n')
                        l2 = l3 = ''
                    else:
                        outfile.write(l1)
                outfile.write(l2 + l3)


if __name__ == '__main__':
    csvify(argv[1])
