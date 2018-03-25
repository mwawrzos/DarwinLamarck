# encoding utf-8

import fnmatch
import os
import matplotlib.pyplot as plt
import numpy as np
from gen import GenState
from scipy import polyfit, polyval

data = dict()

path = os.path.join('cp', '17Sep14012108')
for case in os.listdir(path):
    print(case)
    case_dir = os.path.join(path, case)
    xs = []
    for x in os.listdir(case_dir):
        x_dir = os.path.join(case_dir, x)
        gens = []
        for gen in [gen for gen
                    in os.listdir(x_dir)
                    if fnmatch.fnmatch(gen, '*.pkl')]:
            gen_dir = os.path.join(x_dir, gen)
            s = GenState([], [], gen_dir)
            gens.append(s)
        xs.append(gens)
    data[case] = xs


def map_case(cases, operator, getter):
    values = [[operator(list(map(getter, a.sheep))) for a in olo]
              for olo in cases]
    return operator(values, 0)


def alive(state):
    return state.fitness.getValues()[1] > 0


def calc_fitness(fitness):
    return sum(v * w for (v, w) in zip(fitness.values, fitness.weights))


def draw(_case, specie, foo, color, label):
    stats = gen_stats(foo, _case, specie)
    x = range(len(stats))
    y = polyfit(x, stats, 4)
    y_pred = polyval(y, x)
    plt.plot(stats, '%s--' % color, label=label)
    plt.plot(y_pred, '%s-' % color, label='_nolegend_')


def gen_stats(foo, _case, specie):
    return foo(axis=0,
               a=[[foo([calc_fitness(wolf.fitness)
                        for wolf in getattr(day, specie)])
                   for day in rep]
                  for rep in data[_case]])
# christopher chawaker

l = 'lamarck'
d = 'kDarwin'
n = 'TWO__NO'
m = np.max, 'maksimum'
a = np.mean, 'średniej'
s = 'sheep', 'Owce', 'wilkami'
w = 'wolfs', 'Wilki', 'owcami'

funkcja = a
gatunek = s
# _specie = s[0]
s1, w1 = 'ONE__NO', 'ONE__NO'
s2, w2 = n, n

_foo = funkcja[0]
_specie = gatunek[0]

draw('s_%s-w_%s' % (s1, w1), _specie, _foo, 'C0', '%s wg t. 1no' % gatunek[1])
draw('s_%s-w_%s' % (s2, w2), _specie, _foo, 'C1', '%s wg t. 2no' % gatunek[1])

# draw('s_%s-w_%s' % (l, l), _specie, _foo, 'C0', '%s wg t. Lamarcka' % gatunek[1])
# draw('s_%s-w_%s' % (d, d), _specie, _foo, 'C1', '%s wg t. Darwina' % gatunek[1])
# draw('s_%s-w_%s' % ('TWO__NO', 'TWO__NO'), _specie, _foo, 'C2', '%s bez mutacji' % gatunek[1])
# draw('s_%s-w_%s' % (l, d), _specie, _foo, 'C3', '%s wg t. Lamarcka' % gatunek[1])
# draw('s_%s-w_%s' % (d, l), _specie, _foo, 'C4', '%s wg t. Darwina' % gatunek[1])
# draw('s_%s-w_%s' % (l, n), _specie, _foo, 'C5', '%s wg t. Lamarcka' % gatunek[1])
# draw('s_%s-w_%s' % (d, n), _specie, _foo, 'C6', '%s wg t. Darwina' % gatunek[1])

plt.legend()
plt.title('Zestawienie różnych środowisk z %s — wykres %s' % (gatunek[2], funkcja[1]))
plt.xlabel('Pokolenie')
plt.ylabel('Dostosowanie')
