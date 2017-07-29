import os
import pickle
import random
import subprocess
from datetime import datetime

import numpy as np
from deap import base, tools, creator, algorithms

import Boids
from gen_model import SimulationModel
from lamarck import Lamarck

X_MAX = 20
Y_MAX = 20

MAX_ITER = 700
MAX_GEN = 80

MAX_VALUE = 1000

GRASS_COUNT = 400
SHEEP_COUNT = 200
WOLFS_COUNT = 40

# S_CXPB, S_MUTPB = 0.5, 0.1
W_CXPB, W_MUTPB = 0.5, 0.1
S_CXPB, S_MUTPB = 0, 0
# W_CXPB, W_MUTPB = 0, 0

MUT_SIGMA = 10
MUT_PB = 0.1
W_TOUR_SIZE = 3
S_TOUR_SIZE = 3

SHEEP_LAMARCK = Lamarck(0.1, 0.1, S_MUTPB)
WOLFS_LAMARCK = Lamarck(0.1, 0.1, W_MUTPB)
# SHEEP_LAMARCK = None
# WOLFS_LAMARCK = None

common_tbx = base.Toolbox()
s_toolbox = base.Toolbox()
w_toolbox = base.Toolbox()


def foo(pop, name):
    return list(map(lambda ind: ind.fitness.values, pop[name]))


def alive(pop):
    def has_energy(ind):
        return ind[1] > 0

    return len(list(filter(has_energy, pop[0])))


def asd(specie):
    return [ind.get_params() for ind in specie]


def eval_populations(*species):
    sheep_par, wolf_par = species
    species = [(Boids.SheepAgent, SHEEP_LAMARCK, sheep_par),
               (Boids.WolfAgent, WOLFS_LAMARCK, wolf_par),
               (Boids.GrassAgent, False, [()] * GRASS_COUNT)]
    model = SimulationModel(X_MAX, Y_MAX, species, MAX_ITER)
    model.run_model()
    return model.results(), (asd(model.species[0]), asd(model.species[1]))


creator.create('FitnessMax', base.Fitness, weights=(1.0, 0.1))
creator.create('Sheep', list, fitness=creator.FitnessMax)
creator.create('Wolf', list, fitness=creator.FitnessMax)

common_tbx.register('random', random.randint, a=0, b=MAX_VALUE)
common_tbx.register('evaluate', eval_populations)
common_tbx.register('mate', tools.cxTwoPoint)
common_tbx.register('mutate', tools.mutGaussian, mu=0, sigma=MUT_SIGMA, indpb=MUT_PB)

s_toolbox.register('individual', tools.initRepeat, creator.Sheep, common_tbx.random, n=7)
s_toolbox.register('population', tools.initRepeat, list, s_toolbox.individual)
s_toolbox.register('select', tools.selTournament, tournsize=S_TOUR_SIZE)

w_toolbox.register('individual', tools.initRepeat, creator.Wolf, common_tbx.random, n=5)
w_toolbox.register('population', tools.initRepeat, list, w_toolbox.individual)
w_toolbox.register('select', tools.selTournament, tournsize=W_TOUR_SIZE)

s_stats = tools.Statistics(lambda pop: foo(pop, 'sheep'))
w_stats = tools.Statistics(lambda pop: foo(pop, 'wolfs'))
stats = tools.MultiStatistics(sheep=s_stats, wolfs=w_stats)
stats.register('avg', np.average)
stats.register('std', np.std)
stats.register('min', np.min)
stats.register('median', np.median)
stats.register('max', np.max)
stats.register('alive', alive)


class GenState:
    def __init__(self, checkpoint, directory=None):
        self.directory = directory if directory else os.path.join('cp', str(datetime.now().strftime('%y%b%d%H%M%S')))
        os.makedirs(self.directory)
        self.sheep, self.wolfs, self.s_hof, self.w_hof, self.logbook = (None,) * 5
        if checkpoint:
            self.load_state(checkpoint)
        else:
            self.new_state()

    def new_state(self):
        self.sheep = s_toolbox.population(n=SHEEP_COUNT)
        self.wolfs = w_toolbox.population(n=WOLFS_COUNT)
        self.s_hof = tools.HallOfFame(10)
        self.w_hof = tools.HallOfFame(10)
        self.logbook = tools.Logbook()
        self.logbook.header = 'gen', 'sheep', 'wolfs'
        self.logbook.chapters['sheep'].header = 'std', 'min', 'median', 'avg', 'max', 'alive'
        self.logbook.chapters['wolfs'].header = 'std', 'min', 'median', 'avg', 'max', 'alive'
        self.logbook.columns_len = [4, 28, 28]

    def load_state(self, checkpoint):
        with open(checkpoint, 'rb') as cp_file:
            cp = pickle.load(cp_file)
        self.sheep = cp['sheep']
        self.wolfs = cp['wolfs']
        self.s_hof = cp['s_hof']
        self.w_hof = cp['w_hof']
        self.logbook = cp['logbook']
        random.setstate(cp['random'])
        np.random.set_state(cp['np_random'])

    def checkpoint(self, gen):
        path = os.path.join(self.directory, '%03i.pkl' % gen)
        cp = {
            'sheep': self.sheep,
            'wolfs': self.wolfs,
            's_hof': self.s_hof,
            'w_hof': self.w_hof,
            'logbook': self.logbook,
            'random': random.getstate(),
            'np_random': np.random.get_state()
        }
        with open(path, mode='wb') as cp_file:
            pickle.dump(cp, cp_file)

    def log_population(self, gen):
        self.s_hof.update(self.sheep)
        self.w_hof.update(self.wolfs)
        self.logbook.record(gen=gen, **stats.compile([{'sheep': self.sheep, 'wolfs': self.wolfs}]))
        print(self.logbook.stream)


def main(checkpoint=None, directory=None):
    state = GenState(checkpoint, directory)
    with open(os.path.join(state.directory, 'summary.txt'), 'w') as summary:
        summary.write('Polulacje:   wilki[%d] owce[%d]\n' % (len(set(((v for v in w) for w in state.wolfs))),
                                                             len(set(((v for v in s) for s in state.sheep)))))

    evaluate_population(state.sheep, state.wolfs)
    state.log_population(0)
    state.checkpoint(0)

    for g in range(1, MAX_GEN):
        state.sheep = common_tbx.select(state.sheep, len(state.sheep))
        state.wolfs = common_tbx.select(state.wolfs, len(state.wolfs))

        state.sheep = algorithms.varAnd(state.sheep, common_tbx, S_CXPB, 0 if SHEEP_LAMARCK else S_MUTPB)
        state.wolfs = algorithms.varAnd(state.wolfs, common_tbx, W_CXPB, 0 if WOLFS_LAMARCK else W_MUTPB)

        evaluate_population(state.sheep, state.wolfs)

        state.log_population(g)
        state.checkpoint(g)

    with open(os.path.join(state.directory, 'summary.txt'), 'a') as summary:
        summary.write(str(state.logbook))
        summary.write('\nPolulacje:   wilki[%d] owce[%d]\n' % (len(set(((v for v in w) for w in state.wolfs))),
                                                               len(set(((v for v in s) for s in state.sheep)))))
        summary.write('\nPlansza:       %dx%d' % (X_MAX, Y_MAX))
        summary.write('\nSymulacja:     %dx%d' % (MAX_GEN, MAX_ITER))
        summary.write('\nPolulacja:     %d trawy, %d owiec, %d wilków' % (GRASS_COUNT, SHEEP_COUNT, WOLFS_COUNT))
        summary.write('\nEwolucja o:    %s' % ('Lamarck' if SHEEP_LAMARCK else 'Darwin'))
        summary.write('\nEwolucja w:    %s' % ('Lamarck' if WOLFS_LAMARCK else 'Darwin'))
        summary.write('\nEwolucja o:    cx(%f), mut(%f)' % (S_CXPB, S_MUTPB))
        summary.write('\nEwolucja w:    cx(%f), mut(%f)' % (W_CXPB, W_MUTPB))
        summary.write('\nMutacja:       sigma=%d, p(%f)' % (MUT_SIGMA, MUT_PB))
        summary.write('\nKrzyżowanie o: turniej=%d' % S_TOUR_SIZE)
        summary.write('\nKrzyżowanie w: turniej=%d' % W_TOUR_SIZE)
        summary.write('\nLimit rand:    %d' % MAX_VALUE)
        summary.write('\nWersja:        %s' % get_git_sha())
    print(state.s_hof)
    print(state.w_hof)


def get_git_sha():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


def evaluate_population(sheep, wolfs):
    results, (sp, wp) = common_tbx.evaluate(sheep, wolfs)
    results = list(results)
    for s, res in zip(sheep, results[0]):
        s.fitness.values = res
    for wolf, res in zip(wolfs, results[1]):
        wolf.fitness.values = res
    for i in range(len(sheep)):
        for j in range(len(sheep[i])):
            sheep[i][j] = sp[i][j]
    for i in range(len(wolfs)):
        for j in range(len(wolfs[i])):
            wolfs[i][j] = wp[i][j]


if __name__ == '__main__':
    main()
