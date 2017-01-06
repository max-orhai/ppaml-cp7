import csv
import json
import sys

from constants import dateToWeek

{
  "01001": {
    "ILI percentage %": {
      "01/03/2015": 0.016282420314801916,
      "01/04/2014": 0.2966518348098047,
      "01/10/2015": 0.010809779258632864,
      # ...
    }
  }
  # ...
}


def loadjson(filename):
    with open(filename) as fh:
        fp = json.load(fh)
    return fp


def weekly(rates, pops, regions):
    weeks = {}
    for (fips, d) in rates.items():
        region = regions[fips]
        pop = pops[fips]
        for (date, pct) in d["ILI percentage %"].items():
            if date not in weeks:
                weeks[date] = [0] * 11
            weeks[date][region] += (pct * 100) * pop
    return weeks


# to sum Flu_ILI.csv regional rates:
def weightedSums(filenameIn, filenameOut):
    pops = loadjson("avgpops.json")
    regions = loadjson("fipsToRegion.json")
    regionPops = [0] * 11
    for (fips, region) in regions.items():
        regionPops[region] += pops[fips]
    regionPops.append(sum(regionPops))  # US total pop

    def weightedPercent(regions):
        count = 0
        for (r, p) in zip(regions, regionPops)[1:-1]:
            count += (float(r) / 100) * p
        return '{:05.2f}'.format(100 * (count / regionPops[-1]))

    rows = []
    with open(filenameIn, 'rb') as fh:
        data = csv.reader(fh)
        rows.append(data.next())  # header row
        for row in data:
            rows.append(row + [weightedPercent(row)])

    with open(filenameOut, 'wb') as fh:
        writer = csv.writer(fh)
        for r in rows:
            writer.writerow(r)

# to process model output json:
if __name__ == '__main__':
    pops = loadjson("avgpops.json")
    regions = loadjson("fipsToRegion.json")
    rates = loadjson(sys.argv[1])

    regionPops = [0] * 11
    for (fips, region) in regions.items():
        regionPops[region] += pops[fips]
    regionPops.append(sum(regionPops))  # US total pop

    weeklyBins = weekly(rates, pops, regions)
    weeklyBins = sorted([
        [dateToWeek(date)] + counts[1:] + [sum(counts)]
        for (date, counts) in weeklyBins.items()])

    # convert counts back to percentage rates
    for wb in weeklyBins:
        for i in range(1, 12):
            wb[i] /= regionPops[i] * 100

    print('Year.Wk,R.01%,R.02%,R.03%,R.04%,R.05%,R.06%,R.07%,R.08%,R.09%,R.10%,USA%')
    for row in weeklyBins:
        print(','.join(map('{:05.2f}'.format, row)))
