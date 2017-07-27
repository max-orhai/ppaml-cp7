from sys import argv
from csv import DictReader
import matplotlib.pyplot as plt

data = [d for d in DictReader(open(argv[1]))]
pop_cs = [pc for pc in [
            ('constant', 'r'),
            ('linxtrp', 'orange'),
            ('fbprophet', 'y'),
            ('per', 'g'),
            ('se', 'c'),
            ('crosscatts', 'b'),
            ('dsm', 'm'),
            ] if pc[0] in data[0]]
name = argv[1].split('/')[-1].split('.')[0]

plt.title('forecast error in population {}'.format(name))
plt.xlabel('weeks ahead')
plt.ylabel('%ILI mean absolute error')
plt.xticks(range(len(data) + 1))
for pop, c in pop_cs:
    plt.plot([d[pop] if float(d[pop]) < 5 else None for d in data], ':s', label=pop, c=c)
plt.legend()
plt.savefig('results/' + name + '.png', dpi=150)
