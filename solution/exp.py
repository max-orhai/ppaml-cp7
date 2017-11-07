#! /usr/bin/python

import argparse
from math import exp


# sum of squared errors over zipped lists
def sse(xys):
    def sqerr(xy):
        x, y = xy
        return (x - y) ** 2
    return sum(map(sqerr, xys))


# exponential model
# TODO: replace narrow_up, narrow_dn with epi start and end
def exp_model(baseline, peak, height, narrow_up, narrow_down):
    def y(x):
        narrow = narrow_up if x < peak else narrow_down
        return baseline + height * exp(0 - (narrow * (x - peak)) ** 2)
    return [y(x) for x in range(52)]


def mean(xs):
    return sum(xs) / len(xs)


def baseline(season):
    return mean(sorted(season)[:20])  # ... is there a better heuristic?


def in_out(v, ys):  # the position in ys of the first and last y > v
    # TODO: {more stable?} in_out(v, ys, k)
    # the positions in ys of the last y < v before index k and
    #                        the first y < v after index k
    def pfa(xs):
        for (i, x) in zip(range(99), xs):
            if x > v:
                return i
    return (pfa(ys), -1 - pfa(reversed(ys)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Score CP7.3 solution forecasts')
    arg = parser.add_argument
    arg('--base', type=float, help='baseline rate')
    arg('--peak', type=float, help='x value of peak')
    arg('--height', type=float, help='y value of peak')
    arg('--narrow_up', type=float, help='narrowness of the up-slope')
    arg('--narrow_dn', type=float, help='narrowness of the down-slope')
    arg('target', type=open, help='a file containing 52 numbers, one per line')
    arg('-q', '--quiet', action='store_true', help="don't plot, just print SSE score")
    args = parser.parse_args()

    target = [float(line) for line in args.target]

    base = args.base or baseline(target)
    peak = args.peak or target.index(max(target))
    height = args.height or max(target) - base

    # TODO: calculate these
    nar_up = args.narrow_up
    nar_dn = args.narrow_dn

    model = exp_model(base, peak, height, nar_up, nar_dn)

    score = sse(zip(target, model))
    result = 'SSE: {:.04f}'.format(score)

    print(result)
    if not args.quiet:
        import matplotlib.pyplot as plt

        # result = '$y = B + He^{-(N (x-O))^2}$ \n'.replace(
        #     'B', '{:.02}'.format(base)).replace(
        #     'O', '{}'.format(peak)).replace(
        #     'H', '{:.02}'.format(height)).replace(
        #     'N', '{:.02}'.format(narrow)) + result
        plt.xlabel('Weeks from season start')
        plt.ylabel('% ILI')
        plt.title(result)
        plt.plot(target, label='target')
        plt.plot(model, label='model', alpha=0.7)
        plt.legend(loc='upper left', frameon=False)
        plt.show()

