#! /usr/bin/python

import argparse


# sum of squared errors over zipped lists
def sse(xys):
    def sqerr(xy):
        x, y = xy
        try:
            return (x - y) ** 2
        except TypeError:  # allow for missing values
            return 0
    return sum(map(sqerr, xys))


def iterate(f, v):
    while True:
        v = f(v)
        yield v


def take(n, gen):
    return [next(gen) for _ in range(n)]


# the SIR model as an iterator
def epi(beta, gamma, initI, base):
    def nextSRI(sri):
        s, r, i = sri  # unpack tuple
        dS = 0 - beta * s * i
        dR = gamma * i
        dI = 0 - (dS + dR)
        return (s + dS, r + dR, i + dI)
    return (base + i * 100 for (_, _, i) in
            iterate(nextSRI, (1, 0, initI / 100)))


def offset(xs, i, pad):
    i = int(i)
    if i < 0:
        return xs[-i:] + [pad] * -i
    elif i > 0:
        return [pad] * i + xs[:-i]
    else:
        return xs


def interpolate(ys, dx, pad):
    assert -1 < dx < 1
    if dx > 0:
        return [l + dx * (r - l) for (l, r) in zip(ys, [pad] + ys)]
    elif dx < 0:
        return [l + (dx + 1) * (r - l) for (l, r) in zip(ys[1:] + [pad], ys)]
    else:
        return ys


# Translate a sequence of numbers an arbitrary amount left or right,
# using linear interpolation between successive values, and padding
# as needed. We need this to preserve continuity of the 'onset' param
# in its effect on the SSE when finding minima.
def shift(ys, dx, pad):
    dx_whole = int(dx)
    dx_fract = dx - dx_whole
    return offset(interpolate(ys, dx_fract, pad), dx_whole, pad)


def epi_at(beta, gamma, onset, base):
    raw = take(70, epi(beta, gamma, initI=0.01, base=base))  # longer tail
    return shift(raw, onset, base)[:52]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Score CP7.3 solution forecasts')
    parser.add_argument('beta', type=float, help='infection rate, per week')
    parser.add_argument('gamma', type=float, help='recovery rate, per week')
    parser.add_argument('onset', type=float, help='initial percentage infected')
    parser.add_argument('base', type=float, help='baseline infection rate')
    parser.add_argument('-t', '--target', help='a file containing 52 numbers, one per line')
    parser.add_argument('-q', '--quiet', action='store_true', help="don't plot, just print SSE score")
    args = parser.parse_args()

    if args.target:
        with open(args.target) as target_file:
            target = [float(line) for line in target_file]

    model = epi_at(args.beta, args.gamma, args.onset, args.base)
    title = 'beta = {}, gamma = {}, onset = {}, base = {}'.format(
        args.beta, args.gamma, args.onset, args.base)
    if args.target:
        score = sse(zip(target, model))
        result = 'SSE = {:.03f}'.format(score)
        print(result)
        title += '\n' + result

    if not args.quiet:
        import matplotlib.pyplot as plt
        plt.xlabel('Weeks from season start')
        plt.ylabel('% ILI')
        plt.title(title)
        plt.plot(model, color='orange', label='model')
        if args.target:
            plt.plot(target, color='blue', label='target', alpha=0.6)
            plt.legend(loc='upper left', frameon=False)
        plt.show()
