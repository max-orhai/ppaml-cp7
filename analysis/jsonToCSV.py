#!/usr/bin/env python

import csv
import json
import sys


def main():
    writer = csv.writer(sys.stdout)
    writer.writerow(['fips', 'date', 'ili'])
    for filename in sys.argv[1:]:
        with open(filename) as f:
            try:
                payload = json.load(f)
            except ValueError:
                sys.stderr.write("Can't read JSON from file {}\n".format(
                    filename))
                break

        for fips, fips_dict in sorted(payload.items()):
            ili = fips_dict['ILI percentage %']
            for date, val in sorted(ili.items()):
                writer.writerow([fips, date, val])

if __name__ == '__main__':
    main()
