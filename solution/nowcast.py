#! /usr/bin/env python3

from argparse import ArgumentParser
import matplotlib.pyplot as plt

from epi import epi_at, sse
from fit import fit
from seasons import seasons_for



if __name__ == '__main__':
    ap = ArgumentParser(description='Predict CP7.3 flu data using SIR curves')
    ap.add_argument('file', help='a CP7.3 population data CSV')
    ap.add_argument('column', help='a column in the CSV')
    args = ap.parse_args()

    # throw a ValueError if more than one season in file
    [(target_season, truth)] = seasons_for(args.file, args.column)
    
    # mask out end of season for each week
    nows = [(wk, truth[:wk] + [None] * (52 - wk)) for wk in range(1, 53)]
    
    fits = [(wk, fit(rs)) for (wk, rs) in nows]
    epis = [(wk, epi_at(*fit[:4]), fit[4]) for (wk, fit) in fits]

    plt.xlabel('Weeks from season start')
    plt.ylabel('% ILI')
    orange = plt.get_cmap('Oranges')
    print('obs. SSE, season SSE')
    for (wk, curve, score) in epis:
        plt.plot(curve, color=orange(wk / 52.0), alpha=0.6, linewidth=3)
        print('{: 7.3f}, {: 7.3f}'.format(score, sse(zip(curve, truth))))
    plt.plot(truth, color='blue', marker='.', markersize=10)
    plt.title('Predicted {}, over {} season'.format(
        args.column, target_season))
    plt.show()
