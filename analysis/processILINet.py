import csv
from collections import defaultdict

# read input:
# REGION,   YEAR, WEEK, % WEIGHTED ILI, %UNWEIGHTED ILI, ILITOTAL, TOTAL PATIENTS, NUM. OF PROVIDERS
# Region 1, 1997, 40,   0.498535,       0.623848,        44,       7053,           32
# ...


def compact(filename):

    weeks = defaultdict(list)
    with open(filename, 'rb') as file:
        data = csv.reader(file)
        data.next()  # throw away header row
        for raw_vals in data:
            (region, year, week, _, _, ili, total, _) = tuple(raw_vals)
            weeks[(int(year), int(week))].append((region, ili, total))

    rows = []
    for ((year, week), vals) in sorted(weeks.items()):
        row = [float('{}.{:02.0f}'.format(year, week))]
        total_patient_count = 0
        ili_patient_count = 0
        try:
            for (region, ili, total) in sorted(vals):
                ili, total = float(ili), float(total)
                row.append(ili / total)
                total_patient_count += total
                ili_patient_count += ili
        except ValueError:
            continue  # skip any weeks with 'X' (missing) values
        row.append(ili_patient_count / total_patient_count)
        rows.append(tuple(row))

    return rows


if __name__ == '__main__':
    rows = compact('ILINet-by-region.csv')
    print('Year.Wk,R.01%,R.02%,R.03%,R.04%,R.05%,R.06%,R.07%,R.08%,R.09%,R.10%,USA%')
    for row in rows:
        row = [row[0]] + map(lambda x: 100 * x, row[1:])
        print(','.join(map('{:05.2f}'.format, row)))
