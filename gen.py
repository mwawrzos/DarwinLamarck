import random

import numpy
from deap import base, tools, creator

import Boids
from gen_model import SimulationModel

X_MAX = 10
Y_MAX = 10

MAX_ITER = 1000

MAX_VALUE = 1000

GRASS_COUNT = 100
SHEEP_COUNT = 50
WOLFS_COUNT = 10


# noinspection PyUnresolvedReferences
def main():
    common_tbx = base.Toolbox()
    s_toolbox = base.Toolbox()
    w_toolbox = base.Toolbox()

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

    s_toolbox.register('individual', tools.initRepeat, creator.Sheep, common_tbx.random, n=0)
    s_toolbox.register('population', tools.initRepeat, list, s_toolbox.individual)

    w_toolbox.register('individual', tools.initRepeat, creator.Wolf, common_tbx.random, n=0)
    w_toolbox.register('population', tools.initRepeat, list, w_toolbox.individual)

    s_toolbox.register('evaluate', eval_populations)

    if __name__ == '__main__':
        random.seed(64)

        sheep = s_toolbox.population(n=SHEEP_COUNT)
        wolfs = w_toolbox.population(n=WOLFS_COUNT)

        s_hof = tools.HallOfFame(10)
        w_hof = tools.HallOfFame(10)

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register('avg', numpy.average)
        stats.register('std', numpy.std)
        stats.register('min', numpy.min)
        stats.register('max', numpy.max)

        s_logbook = tools.Logbook()
        s_logbook.header = 'gen', 'evals', 'std', 'min', 'avg', 'max'

        w_logbook = tools.Logbook()
        w_logbook.header = 'gen', 'evals', 'std', 'min', 'avg', 'max'

        results = list(s_toolbox.evaluate(sheep, wolfs))
        for s, res in zip(sheep, results[0]):
            s.fitness.values = res
        for wolf, res in zip(wolfs, results[1]):
            wolf.fitness.values = res
        # for sheep_, wolf, res in zip(sheep, wolfs, zip(results[0], results[1])):
        #     sheep_.fitness.values, wolf.fitness.values = res

        s_hof.update(sheep)
        w_hof.update(wolfs)
        s_logbook.record(gen=0, evals=len(sheep), **stats.compile(sheep))
        print(s_logbook.stream)
        w_logbook.record(gen=0, evals=len(wolfs), **stats.compile(wolfs))
        print(w_logbook.stream)


if __name__ == '__main__':
    main()
