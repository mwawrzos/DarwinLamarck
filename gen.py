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


def pop_stats(pop, name):
    return [ind.fitness.values for ind in pop[name]]


def alive(pop):
    def has_energy(ind):
        return ind[1] > 0

    return len(list(filter(has_energy, pop[0])))


def specie_params(specie):
    return [ind.get_params() for ind in specie]


def pop_s(pop):
    return pop_stats(pop, 'sheep')


def pop_w(pop):
    return pop_stats(pop, 'wolfs')


class GenState:
    def __init__(self, sheep, wolfs, checkpoint):

        self.cps = []
        self.s_stats = tools.Statistics(pop_s)
        self.w_stats = tools.Statistics(pop_w)
        self.stats = tools.MultiStatistics(sheep=self.s_stats, wolfs=self.w_stats)
        self.stats.register('avg', np.average)
        self.stats.register('std', np.std)
        self.stats.register('min', np.min)
        self.stats.register('median', np.median)
        self.stats.register('max', np.max)
        self.stats.register('alive', alive)

        self.sheep, self.wolfs = sheep, wolfs

        self.s_hof, self.w_hof, self.logbook = (None,) * 3
        if checkpoint:
            self.load_state(checkpoint)
        else:
            self.new_state()

    def new_state(self):
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
        cp = {
            'sheep': self.sheep,
            'wolfs': self.wolfs,
            's_hof': self.s_hof,
            'w_hof': self.w_hof,
            'logbook': self.logbook,
            'random': random.getstate(),
            'np_random': np.random.get_state()
        }
        self.cps.append(cp)

    def log_population(self, gen, v):
        self.s_hof.update(self.sheep)
        self.w_hof.update(self.wolfs)
        self.logbook.record(gen=gen, **self.stats.compile([{'sheep': self.sheep, 'wolfs': self.wolfs}]))
        if v:
            print(self.logbook.stream)


def get_git_sha():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


creator.create('FitnessMax', base.Fitness, weights=(1.0, 0.1))
creator.create('Sheep', list, fitness=creator.FitnessMax)
creator.create('Wolf', list, fitness=creator.FitnessMax)


class Sim:
    def __init__(self, verbose=True):
        self.v = verbose
        self.X_MAX = 10
        self.Y_MAX = 10

        self.MAX_ITER = 500
        self.MAX_GEN = 40

        self.MAX_VALUE = 1000

        self.GRASS_COUNT = 100
        self.SHEEP_COUNT = 50
        self.WOLFS_COUNT = 20

        self.S_CXPB, self.S_MUTPB = 0.25, 0.1
        self.W_CXPB, self.W_MUTPB = 0.25, 0.1
        # self.S_CXPB, self.S_MUTPB = 0, 0
        # self.W_CXPB, self.W_MUTPB = 0, 0

        self.MUT_SIGMA = 10
        self.MUT_PB = 0.1
        self.W_TOUR_SIZE = 3
        self.S_TOUR_SIZE = 3

        # self.SHEEP_LAMARCK = Lamarck(0.1, 0.1, self.S_MUTPB)
        # self.WOLFS_LAMARCK = Lamarck(0.1, 0.1, self.W_MUTPB)
        self.SHEEP_LAMARCK = None
        self.WOLFS_LAMARCK = None

        self.common_tbx = base.Toolbox()
        self.s_toolbox = base.Toolbox()
        self.w_toolbox = base.Toolbox()

        self.common_tbx.register('random', random.randint, a=0, b=self.MAX_VALUE)
        self.common_tbx.register('evaluate', self.eval_populations)
        self.common_tbx.register('mate', tools.cxTwoPoint)
        self.common_tbx.register('mutate', tools.mutGaussian, mu=0, sigma=self.MUT_SIGMA, indpb=self.MUT_PB)

        self.s_toolbox.register('individual', tools.initRepeat, creator.Sheep, self.common_tbx.random, n=7)
        self.s_toolbox.register('population', tools.initRepeat, list, self.s_toolbox.individual)
        self.s_toolbox.register('select', tools.selTournament, tournsize=self.S_TOUR_SIZE)

        self.w_toolbox.register('individual', tools.initRepeat, creator.Wolf, self.common_tbx.random, n=5)
        self.w_toolbox.register('population', tools.initRepeat, list, self.w_toolbox.individual)
        self.w_toolbox.register('select', tools.selTournament, tournsize=self.W_TOUR_SIZE)

    def eval_populations(self, *species):
        sheep_par, wolf_par = species
        species = [(Boids.SheepAgent, self.SHEEP_LAMARCK, sheep_par),
                   (Boids.WolfAgent, self.WOLFS_LAMARCK, wolf_par),
                   (Boids.GrassAgent, False, [()] * self.GRASS_COUNT)]
        model = SimulationModel(self.X_MAX, self.Y_MAX, species, self.MAX_ITER)
        model.run_model()
        return model.results(), (specie_params(model.species[0]), specie_params(model.species[1]))

    def main(self, checkpoint=None):
        state = GenState(checkpoint=checkpoint,
                         sheep=self.s_toolbox.population(n=self.SHEEP_COUNT),
                         wolfs=self.w_toolbox.population(n=self.WOLFS_COUNT))

        self.evaluate_population(state.sheep, state.wolfs)
        state.log_population(0, self.v)
        state.checkpoint(0)

        for g in range(1, self.MAX_GEN):
            state.sheep = self.s_toolbox.select(state.sheep, len(state.sheep))
            state.wolfs = self.w_toolbox.select(state.wolfs, len(state.wolfs))

            state.sheep = algorithms.varAnd(state.sheep,
                                            self.common_tbx, self.S_CXPB, 0 if self.SHEEP_LAMARCK else self.S_MUTPB)
            state.wolfs = algorithms.varAnd(state.wolfs,
                                            self.common_tbx, self.W_CXPB, 0 if self.WOLFS_LAMARCK else self.W_MUTPB)

            self.evaluate_population(state.sheep, state.wolfs)

            state.log_population(g, self.v)
            state.checkpoint(g)

        if self.v:
            print(state.s_hof)
            print(state.w_hof)

        return state

    def write_summary(self, state, directory):
        with open(os.path.join(directory, 'summary.txt'), 'a') as summary:
            summary.write(str(state.logbook))
            summary.write('\nPolulacje:   wilki[%d] owce[%d]\n' % (len(set(((v for v in w) for w in state.wolfs))),
                                                                   len(set(((v for v in s) for s in state.sheep)))))
            summary.write('\nPlansza:       %dx%d' % (self.X_MAX, self.Y_MAX))
            summary.write('\nSymulacja:     %dx%d' % (self.MAX_GEN, self.MAX_ITER))
            summary.write(
                '\nPolulacja:     %d trawy, %d owiec, %d wilków' % (
                    self.GRASS_COUNT, self.SHEEP_COUNT, self.WOLFS_COUNT))
            summary.write('\nEwolucja o:    %s' % ('Lamarck' if self.SHEEP_LAMARCK else 'Darwin'))
            summary.write('\nEwolucja w:    %s' % ('Lamarck' if self.WOLFS_LAMARCK else 'Darwin'))
            summary.write('\nEwolucja o:    cx(%f), mut(%f)' % (self.S_CXPB, self.S_MUTPB))
            summary.write('\nEwolucja w:    cx(%f), mut(%f)' % (self.W_CXPB, self.W_MUTPB))
            summary.write('\nMutacja:       sigma=%d, p(%f)' % (self.MUT_SIGMA, self.MUT_PB))
            summary.write('\nKrzyżowanie o: turniej=%d' % self.S_TOUR_SIZE)
            summary.write('\nKrzyżowanie w: turniej=%d' % self.W_TOUR_SIZE)
            summary.write('\nLimit rand:    %d' % self.MAX_VALUE)
            summary.write('\nWersja:        %s' % get_git_sha())

    def evaluate_population(self, sheep, wolfs):
        results, (sp, wp) = self.common_tbx.evaluate(sheep, wolfs)
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


def save_results(directory, res):
    for gen, cp in enumerate(res):
        path = os.path.join(directory, '%03i.pkl' % gen)
        with open(path, mode='wb') as cp_file:
            pickle.dump(cp, cp_file)

if __name__ == '__main__':
    s = Sim()

    _res = s.main()

    _directory = os.path.join('cp', str(datetime.now().strftime('%y%b%d%H%M%S')))
    os.makedirs(_directory)
    save_results(_directory, _res.cps)
    s.write_summary(_res, _directory)

# path = os.path.join('cp', '17Jul30072615')
# for case in os.listdir(path)[:1]:
#     case_dir = os.path.join(path, case)
#     for x in os.listdir(case_dir)[:1]:
#         x_dir = os.path.join(case_dir, x)
#         for gen in [gen for gen
#                     in os.listdir(x_dir)
#                     if fnmatch.fnmatch(gen, '*.pkl')][:1]:
#             gen_dir = os.path.join(x_dir, gen)
#             s = GenState([], [], gen_dir)
