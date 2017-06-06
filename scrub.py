from os import listdir, remove
from sys import argv


last_week = 2015.29
sourcedirname = '../data/all-vaccinations/'
targetdirname = '../data/vaccinations/'


def trim():
    for filename in listdir(sourcedirname):
        with open(sourcedirname + filename) as infile:
            with open(targetdirname + filename, 'w') as outfile:
                for line in infile:
                    if line.startswith('20'):
                        if float(line[:7]) <= last_week:
                            outfile.write(line)
                    else:
                        outfile.write(line)


def rm_empty(dirname):
    for filename in listdir(dirname):
        with open(dirname + filename) as infile:
            data_lines = len(filter(lambda l: l.startswith('20'), infile))
        if data_lines == 0:
            remove(dirname + filename)
            print(dirname + filename)


# $ python scrub.py ~/git/ppaml/ppaml-eval-results/2017-06/cp7-phase3/evaluation-data/ > week-2014.42.txt
def make_example(dirname):
    for filename in listdir(dirname):
        if filename[0].isupper():
            end_wk = '2014.40' if filename.endswith('-flu.csv') else '2014.42'
            with open(dirname + filename) as infile:
                print('>> ' + filename)
                for line in infile:
                    if '2014.20' < line[:7] <= end_wk:
                        print(line[:-1])
                print('')


def check_for_dupes(dirname):
    for filename in listdir(dirname):
        if filename[0].isupper():
            weeks = set()
            with open(dirname + filename) as file:
                for line in file:
                    week = line.split(',', 1)[0]
                    if week in weeks:
                        print(filename + ": " + week)
                    else:
                        weeks.add(week)


if __name__ == '__main__':
    # trim()
    # rm_empty(argv[1])
    # make_example(argv[1])
    check_for_dupes(argv[1])
