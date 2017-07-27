from sys import argv
from csv import DictReader
import matplotlib.pyplot as plt

data = [d for d in DictReader(open(argv[1]))]
keyorder = [k for k in (
                'constant',
                'linxtrp',
                'fbprophet',
                'per',
                'se',
                'crosscatts',
                'dsm',
             ) if k in data[0]]
name = argv[1].split('/')[-1].split('.')[0]

plt.title('Mean squared error of forecast in population {}'.format(name))
plt.xlabel('Weeks ahead')
plt.xticks(range(len(data) + 1))
for k in keyorder:
    plt.plot([d[k] if float(d[k]) < 5 else None for d in data], ':s', label=k)
plt.legend()
plt.show()
