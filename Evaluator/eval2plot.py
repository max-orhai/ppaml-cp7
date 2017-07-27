from sys import argv
from csv import DictReader
import matplotlib.pyplot as plt

data = [d for d in DictReader(open(argv[1]))]
pcs = [k for k in [
       ('USA', 'b'),
       ('R04', 'g'),
       ('TN', 'y'),
       ('D10', 'r'),
       ] if k[0] in data[0]]
name = argv[1].split('/')[-1].split('.')[0]

plt.title('${}$ model forecast error'.format(name))
plt.xlabel('weeks ahead')
plt.ylabel('%ILI mean absolute error')
plt.xticks(range(len(data) + 1))
for (p, c) in pcs:
    plt.plot([d[p] for d in data], ':s', label=p, c=c, alpha=0.6)
plt.legend()
plt.savefig('results/' + name + '.png', dpi=150)
