#! /usr/bin/python

import argparse
import csv


def sse(xys):
    def sqerr(xy):
        x, y = xy
        return (x - y) ** 2
    return sum(map(sqerr, xys))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Score CP7.3 solution forecasts')
    parser.add_argument('target', help='a CSV with data to evaluate')
    parser.add_argument('reference', help='a CSV with ground-truth data')
    parser.add_argument('-c', '--column', default=1, help='CSV column name or index')
    parser.add_argument('-p', '--plot', help='show a plot', action='store_true')
    args = parser.parse_args()

    reader = csv.reader
    week_col = 0
    try:
        column = int(args.column)
    except ValueError:
        column = args.column
        week_col = 'Week'
        reader = csv.DictReader

    with open(args.target) as target_file:
        if week_col == 0:
            target_file.next()  # throw away header
        target = [row for row in reader(target_file)]
    with open(args.reference) as reference_file:
        if week_col == 0:
            reference_file.next()
        reference = [row for row in reader(reference_file)]

    target_data = [(row[week_col], row[column]) for row in target]
    reference_data = [(row[week_col], row[column]) for row in reference]
    err_msg = '{} != {}'.format(len(target_data), len(reference_data))
    assert len(target_data) == len(reference_data), err_msg

    data = zip(target_data, reference_data)
    line_count = 0
    for ((target_week, _), (reference_week, _)) in data:
        line_count += 1
        err_msg = 'data lines {}: {} != {}'.format(
            line_count, target_week, reference_week)
        assert target_week == reference_week, err_msg

    score = sse([(float(t), float(r)) for ((_, t), (_, r)) in data])
    result = 'Sum of squared errors: {} over {} weeks'.format(score, len(data))

    if args.plot:
        import matplotlib.pyplot as plt
        weeks = [w for ((w, _), _) in data]
        ref_vals = [r for (_, (_, r)) in data]
        target_vals = [t for ((_, t), _) in data]
        plt.xlabel('Weeks')
        plt.ylabel('% ILI')
        plt.title(result)
        plt.plot(ref_vals, label=args.reference)
        plt.plot(target_vals, label=args.target, alpha=0.6)
        plt.xticks([0, len(weeks) - 1], [weeks[0], weeks[-1]])
        plt.legend(loc='upper left', frameon=False)
        plt.show()
    else:
        print(result)
