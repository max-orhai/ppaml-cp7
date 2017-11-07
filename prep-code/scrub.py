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


def make_example(dirname):
    for filename in listdir(dirname):
        if filename[0].isupper():
            with open(dirname + filename) as infile:
                print('>> ' + filename)
                for line in infile:
                    if line[:7] in ('2014.41', '2014.42'):
                        print(line[:-1])
                print('')


if __name__ == '__main__':
    # trim()
    # rm_empty(argv[1])
    make_example(argv[1])
