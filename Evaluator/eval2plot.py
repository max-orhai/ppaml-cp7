from sys import argv
from csv import DictReader
import matplotlib.pyplot as plt

data = [d for d in DictReader(open(argv[1]))]
keyorder = [k for k in ('USA', 'R04', 'TN', 'D10') if k in data[0]]
name = argv[1].split('/')[-1].split('.')[0]

plt.title('Mean squared error of "${}$" model forecasts'.format(name))
plt.xlabel('Weeks ahead')
plt.xticks(range(len(data) + 1))
for k in keyorder:
    plt.plot([d[k] for d in data], ':s', label=k)
plt.legend()
plt.show()
