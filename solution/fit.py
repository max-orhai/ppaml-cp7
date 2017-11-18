#! /usr/bin/env python3

from numpy import array
from scipy.optimize import minimize
from argparse import ArgumentParser

from epi import epi_at, sse
from seasons import mean_sd, seasons_for


#              beta         gamma         onset          base
x0 = array([   1.45,        1.13,          1.94,         0.815 ])   # initial value
bounds =   [(0.5, 2.5) , (1.0, 2.5) , (-15.0, 10.0) , (0.0, 2.0)]   # (min, max)
# R0 is the 'basic reproductive ratio', defined as beta / gamma
# x0 was obtained iteratively (3 or 4 steps) from the mean values fitted for USA,
# excluding 2008/2009 outliers


def fit(rates):
    def f(x):  # objective function
        return sse(zip(epi_at(*x), rates))

    result = minimize(f, x0, bounds=bounds, method='TNC',  # truncated Newton
                      options={'maxiter': 500, 'ftol': 0.001, 'stepmx': 1.0})

    if result.success:
        final = list(result.x) + [result.fun]
        return final
    else:
        return str(result.message)


def sir_fits(seasons, omit=[], only=[]):
    target_seasons = [(year, season) for (year, season) in seasons.items()
                      if year not in omit and (only == [] or year in only)]
    fits = {year: fit(rates) for (year, rates) in target_seasons}
    return fits


def red(string):
    return '\033[31m' + string + '\033[0m'


def prettyprint(fitted):
    print('          beta    gamma    onset     base')
    print('min:  ' + ' '.join('{: 8.4f}'.format(p[0]) for p in bounds))
    print('init: ' + ' '.join('{: 8.4f}'.format(p) for p in x0))
    print('max:  ' + ' '.join('{: 8.4f}'.format(p[1]) for p in bounds))
    print('season ' + '-' * 40 + ' SSE')
    for year in sorted(fitted.keys()):
        result = fitted[year]
        if isinstance(result, str):
            print(str(year) + '    ' + red(result))
        else:
            def fmt(idx):
                num = result[idx]
                string = '{: 8.4f}'.format(num)
                return red(string) if num in bounds[idx] else string
            print(str(year) + '  ' + ' '.join(map(fmt, [0, 1, 2, 3])) +
                  '   {: 7.3f}'.format(result[4]))
    stats = []
    for i in range(5):
        stats.append(mean_sd([fitted[k][i] for k in fitted
                              if isinstance(fitted[k], list)]))
    heads = ('mean: ', 'stdv: ')
    print('-' * 52)
    for i in [0, 1]:
        print(heads[i] +
              ' '.join('{: 8.4f}'.format(stat[i]) for stat in stats[:4]) +
              '   {: 7.3f}'.format(stats[4][i]))
    return stats


if __name__ == '__main__':
    ap = ArgumentParser(description='Fit SIR curves to CP7.3 flu data')
    ap.add_argument('file', help='a CP7.3 population data CSV')
    ap.add_argument('column', help='a column in the CSV')
    ps = ap.add_mutually_exclusive_group()
    ps.add_argument('-p', '--plot', metavar='TITLE',
                    help='plot the fitted curves with title')
    ps.add_argument('-s', '--scatter', metavar='TITLE',
                    help='scatter-plot fitted model parameters with title')
    xo = ap.add_mutually_exclusive_group()
    xo.add_argument('-x', '--omit', help='comma-delimited years to omit')
    xo.add_argument('-o', '--only', help='comma-delimited years to select')
    args = ap.parse_args()
    args.only = list(map(int, args.only.split(',')) if args.only else [])
    args.omit = list(map(int, args.omit.split(',')) if args.omit else [])

    # for simplicity, label each season by its start year
    seasons = {int(years[:4]): rates for (years, rates) in
               seasons_for(args.file, args.column)}
    fits = sir_fits(seasons, args.omit, args.only)
    
    stats = prettyprint(fits)
    means = [stats[i][0] for i in [0, 1, 2, 3]]

    if args.plot:
        import matplotlib.pyplot as plt
        plt.xlabel('Weeks from season start')
        plt.ylabel('% ILI')
        i = 0
        for year in sorted(fits.keys()):
            if isinstance(fits[year], list):
                color = 'C' + str(i)
                plt.plot(seasons[year], color=color, marker='.', markersize=10)
                plt.plot(epi_at(*fits[year][:4]), color=color, alpha=0.6, linewidth=3,
                         label='{} (SSE:{: 7.3f})'.format(year, fits[year][-1]))
                i = (i + 1) % 10
        # plt.plot(epi_at(*list(x0)), color='#89fe05', label='initial')
        # plt.plot(epi_at(*means), color='k', label='mean')
        plt.title(args.plot)
        plt.legend(loc='upper left', frameon=False)
        plt.show()

    if args.scatter:
        import matplotlib.pyplot as plt
        plt.xlabel('onset week')
        plt.ylabel('R0 = beta / gamma')

        r0s, onsets, bases, scores = [], [], [], []
        for year, x in sorted(fits.items()):
            if isinstance(x, list):
                r0 = x[0] / x[1]
                r0s.append(r0)
                onsets.append(x[2])
                bases.append(100* x[3])
                scores.append(x[4])
                plt.annotate(year, xy=(x[2], r0), xytext=(0, 0),
                             textcoords='offset points', ha='left', va='bottom')

        plt.scatter(onsets, r0s, s=bases, c=scores, cmap='coolwarm', edgecolor='black')
        plt.colorbar()
        plt.title(args.scatter)
        plt.show()



