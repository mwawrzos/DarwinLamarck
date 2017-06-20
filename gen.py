import random

import numpy
from deap import base, tools, creator, algorithms

import Boids
from gen_model import SimulationModel

X_MAX = 10
Y_MAX = 10

MAX_ITER = 500
MAX_GEN = 100

MAX_VALUE = 1000

GRASS_COUNT = 100
SHEEP_COUNT = 50
WOLFS_COUNT = 10

S_CXPB, S_MUTPB = 0.5, 0.1
MUT_SIGMA = 0.1
MUT_PB = 0.1
TOUR_SIZE = 5

common_tbx = base.Toolbox()
s_toolbox = base.Toolbox()
w_toolbox = base.Toolbox()


def foo(pop, name):
    return list(map(lambda ind: ind.fitness.values, pop[name]))


def eval_populations(*species):
    sheep_par, wolf_par = species
    species = [(Boids.SheepAgent, sheep_par),
               (Boids.WolfAgent, wolf_par),
               (Boids.GrassAgent, [()] * GRASS_COUNT)]
    model = SimulationModel(X_MAX, Y_MAX, species, MAX_ITER)
    model.run_model()
    return model.results()


creator.create('FitnessMax', base.Fitness, weights=(1.0,))
creator.create('Sheep', list, fitness=creator.FitnessMax)
creator.create('Wolf', list, fitness=creator.FitnessMax)

common_tbx.register('random', random.randint, a=0, b=MAX_VALUE)
common_tbx.register('evaluate', eval_populations)
common_tbx.register('select', tools.selTournament, tournsize=7)
common_tbx.register('mate', tools.cxTwoPoint)
common_tbx.register('mutate', tools.mutGaussian, mu=0, sigma=MUT_SIGMA, indpb=MUT_PB)
common_tbx.register('select', tools.selTournament, tournsize=TOUR_SIZE)

s_toolbox.register('individual', tools.initRepeat, creator.Sheep, common_tbx.random, n=2)
s_toolbox.register('population', tools.initRepeat, list, s_toolbox.individual)

w_toolbox.register('individual', tools.initRepeat, creator.Wolf, common_tbx.random, n=2)
w_toolbox.register('population', tools.initRepeat, list, w_toolbox.individual)

s_hof = tools.HallOfFame(10)
w_hof = tools.HallOfFame(10)

s_stats = tools.Statistics(lambda pop: foo(pop, 'sheep'))
w_stats = tools.Statistics(lambda pop: foo(pop, 'wolfs'))
stats = tools.MultiStatistics(sheep=s_stats, wolfs=w_stats)
stats.register('avg', numpy.average)
stats.register('std', numpy.std)
stats.register('min', numpy.min)
stats.register('max', numpy.max)

logbook = tools.Logbook()
logbook.header = 'gen', 'sheep', 'wolfs'
logbook.chapters['sheep'].header = 'std', 'min', 'avg', 'max'
logbook.chapters['wolfs'].header = 'std', 'min', 'avg', 'max'


def main():
    random.seed(64)

    sheep = s_toolbox.population(n=SHEEP_COUNT)
    wolfs = w_toolbox.population(n=WOLFS_COUNT)

    evaluate_population(sheep, wolfs)

    log_population(0, sheep, wolfs)

    for g in range(1, MAX_GEN):
        sheep = common_tbx.select(sheep, len(sheep))
        wolfs = common_tbx.select(wolfs, len(wolfs))

        sheep = algorithms.varAnd(sheep, common_tbx, S_CXPB, S_MUTPB)
        wolfs = algorithms.varAnd(wolfs, common_tbx, S_CXPB, S_MUTPB)

        evaluate_population(sheep, wolfs)

        log_population(g, sheep, wolfs)


def log_population(gen, sheep, wolfs):
    s_hof.update(sheep)
    w_hof.update(wolfs)
    logbook.record(gen=gen, **stats.compile([{'sheep': sheep, 'wolfs': wolfs}]))
    print(logbook.stream)


def evaluate_population(sheep, wolfs):
    results = list(common_tbx.evaluate(sheep, wolfs))
    for s, res in zip(sheep, results[0]):
        s.fitness.values = res
    for wolf, res in zip(wolfs, results[1]):
        wolf.fitness.values = res


if __name__ == '__main__':
    main()
