#! /usr/bin/env python

from csv import DictReader


def read(filename, colname):
    return [{'Week': d['Week'], 'y': d[colname]}
            for d in DictReader(open(filename))]


def write(filename, colname, data):
    with open(filename, 'w') as file:
        file.write('Week,{}\n'.format(colname))
        for d in data:
            file.write('{},{}\n'.format(d['Week'], d['yhat']))


def next_week(week):
    was_str = False
    if type(week) in (str, unicode):
        was_str = True
        week = float(week)
    yr = int(week)
    wk = (week - yr)
    # only valid for years with 52 epi weeks!
    nw = yr + 1.01 if wk > 0.51 else week + 0.01
    if was_str:
        return '{:.02f}'.format(nw)
    else:
        return nw


def forecast(data, weeks_ahead, extrapolate=False):
    last_y = data[-3]['y']  # don't peek at last two weeks
    fcwks = [data[-1]['Week']]
    for _ in range(weeks_ahead):
        fcwks.append(next_week(fcwks[-1]))
    if not extrapolate:
        return [{'Week': w, 'yhat': last_y} for w in fcwks]
    else:
        last_y = float(last_y)
        last2_y = float(data[-4]['y'])
        last3_y = float(data[-5]['y'])
        mean_incr = ((last_y - last2_y) + (last3_y - last2_y)) / 2.0
        fcyhats = [last_y]
        for _ in range(weeks_ahead):
            fcyhats.append(fcyhats[-1] + mean_incr)
        return [{'Week': w, 'yhat': '{:.03f}'.format(y)} for (w, y) in zip(fcwks, fcyhats)]


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Generate CP7.3 forecasts with simple baseline models')
    parser.add_argument('target', help='a CSV with data to forecast')
    parser.add_argument('column', help='CSV column name')
    parser.add_argument('-w', '--weeks', help='number of forecast weeks', type=int, default=4)
    parser.add_argument('-s', '--start', help='epiweek to begin forecasting')
    parser.add_argument('-x', '--extrapolate', help='use linear extrapolation', action='store_true')
    args = parser.parse_args()

    popn = args.column.split('.')[0]
    hist = read(args.target, args.column)

    if args.start is None:
        args.start = hist[-1]['Week']
    else:
        yr, wk = map(int, args.start.split('.'))
        assert 1996 < yr < 2020
        assert 0 < wk < 54

    while hist[-1]['Week'] >= args.start:
        fcst = forecast(hist, args.weeks, extrapolate=args.extrapolate)
        write('forecast-{}-{}.csv'.format(popn, hist[-1]['Week']),
              args.column, fcst)
        hist = hist[:-1]
