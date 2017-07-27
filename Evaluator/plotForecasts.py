from sys import argv
from csv import DictReader
import matplotlib.pyplot as plt


gt = list(DictReader(open('gt.csv')))
fc = list(DictReader(open(argv[1])))

plt.xlabel('Prediction Week')
plt.ylabel('% ILI')

pop_cs = [
    ('USA.%ILI', 'b'),
    ('R04.%ILI', 'g'),
    ('TN.%ILI', 'y'),
    ('D10.%ILI', 'r'),
]

for (pop, c) in pop_cs:
    plt.plot([float(d[pop]) for d in gt], c=c, lw=1.2, alpha=0.4, label=pop)

pw = fc[0]['Week']
offset = [d['Week'] for d in gt].index(pw)

# plt.ylim(-2, 7)  # for linxtrp, too jumpy otherwise!
plt.vlines(offset, 0, 5, alpha=0.2, linestyles='dotted')

for (pop, c) in pop_cs:
    if pop in fc[0]:
        plt.plot([None] * offset +
                 [float(d[pop]) for d in fc], c=c, lw=2.5, alpha=0.8)

plt.xticks([0, offset, len(gt)],
           [gt[0]['Week'], fc[0]['Week'], gt[-1]['Week']])
plt.legend(loc='upper left', frameon=False)

plt.savefig('pngs/' + argv[1].split('/')[-1][:-4] + '.png', dpi=150)
