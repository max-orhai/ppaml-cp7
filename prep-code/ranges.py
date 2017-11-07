
stop_date = '2015.29'

def get_start(pop):
    with open(pop + '-flu.csv') as fh:
        for line in fh:
            if line[0].isdigit():
                return line[:7]

for pop in ('MS', 'NC', 'NJ', 'RI', 'TN', 'TX', 'USA'):
    start_date = get_start(pop)
    for var in ('flu', 'tweets', 'vaccinations', 'weather'):
        filename = pop + '-' + var + '.csv'
        with open(filename) as infile:
            with open('new/' + filename, 'w') as outfile:
                for line in infile:
                    if not line[0].isdigit() or start_date <= line[:7] <= stop_date:
                        outfile.write(line)
