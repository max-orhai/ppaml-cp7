#! /usr/bin/python

"""
Extract a time-series from the given CP7 data CSV file and column name,
and print new CSV with a row for each 52-week season (week 29 through 30).
By default, the output CSV will not have any column or row headers.

Usage:
$ ./seasons.py <file.csv> <column name>
"""

from argparse import ArgumentParser
from sys import stdout
from csv import DictReader, DictWriter


week_seq = ['{:02}'.format(wk) for wk in list(range(30, 54)) + list(range(1, 30))]


def new_season():
    return {'{:02}'.format(wk): None for wk in range(1, 54)}


def in_season(wk, yr, yrs):
    lo, hi = yrs
    return (
        (yr == lo and '29' < wk < '54') or
        (yr == hi and '00' < wk < '30'))


def succ(year_str):
    return str(int(year_str) + 1)


def to_seasons(filename, col_name):
    data = DictReader(open(filename))
    weekly = [(row['Week'], row[col_name]) for row in data]
    start_year = weekly[0][0].split('.')[0]
    seasons = []
    these_years = (start_year, succ(start_year))
    this_season = new_season()
    for (yr_wk, ili) in weekly:
        yr, wk = yr_wk.split('.')
        if not in_season(wk, yr, these_years):
            this_season['years'] = '{}-{}'.format(*these_years)
            seasons.append(this_season)
            this_season = new_season()
            these_years = tuple(map(succ, these_years))
        this_season[wk] = ili
    this_season['years'] = '{}-{}'.format(*these_years)
    seasons.append(this_season)
    return seasons


def tidy(season):
    # make each season have exactly 52 weeks, and no gaps
    # omit week 30 rather than week 53 for long seasons
    return [season[wk] or '' for wk in week_seq
            if not (wk == '53' and season[wk] is None)][:52]


def years_tidy(season):
    return (season['years'], tidy(season))


def spew(seasons):
    for season in seasons:
        print(','.join(season))


def mean_sd(numbers):
    assert len(numbers) > 0
    mean = sum(numbers) / len(numbers)
    variance = sum([(x - mean) ** 2 for x in numbers]) / len(numbers)
    return (mean, variance ** 0.5)


def stats(season):
    values = []
    missing_count = 0
    for x in season:
        try:
            values.append(float(x))
        except ValueError:
            missing_count += 1
    peak = max(season)
    peak_index = season.index(peak)
    base_mean, base_sd = mean_sd(sorted(values)[:20])
    return {
        'height': float(peak),
        'offset': peak_index,
        'base_mean': base_mean,
        'base_sd': base_sd,
        'missing_count': missing_count,
    }


def output_season_stats(seasons):
    seasons = map(stats, seasons)
    writer = DictWriter(stdout, fieldnames=sorted(seasons[0].keys()))
    writer.writeheader()
    writer.writerows(seasons)


def meta(key, stats_seq):
    return '{}, {}, {}'.format(
        key, *mean_sd([d[key] for d in stats_seq]))


def output_meta_stats(seasons):
    season_stats = map(stats, seasons)
    print('var, mean, std_dev')
    for k in season_stats[0].keys():
        print(meta(k, season_stats))


# export-grade interface
def seasons_for(filename, col_name):
    def float_or_none(string):
        try:
            return float(string)
        except ValueError:
            return None
    raw = map(years_tidy, to_seasons(filename, col_name))
    return [(years, list(map(float_or_none, season))) for (years, season) in raw]


if __name__ == '__main__':
    parser = ArgumentParser(description='Collate and analyze CP7.3 data')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--stats', action='store_true', help='output stats for each season')
    group.add_argument('-m', '--meta', action='store_true', help='output stats for season stats')
    parser.add_argument('-y', '--years', action='store_true', help='prepend years to output rows')
    parser.add_argument('file', help='a CP7.3 population data CSV')
    parser.add_argument('column', help='a column in the CSV')
    args = parser.parse_args()

    seasons = map(years_tidy if args.years else tidy,
                  to_seasons(args.file, args.column))

    if args.stats:
        output_season_stats(seasons)
    elif args.meta:
        output_meta_stats(seasons)
    else:
        spew([[yrs] + sn for (yrs, sn) in seasons] if args.years else seasons)
