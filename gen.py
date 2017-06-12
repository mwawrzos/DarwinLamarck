import random

import numpy
from deap import base, tools
from mesa.space import ContinuousSpace

import Boids

X_MAX = 10
Y_MAX = 10

space = ContinuousSpace(X_MAX, Y_MAX,
                        grid_width=10, grid_height=10,
                        torus=True)

GRASS_COUNT = 100
SHEEP_COUNT = 50
WOLFS_COUNT = 10

g_toolbox = base.Toolbox()
s_toolbox = base.Toolbox()
w_toolbox = base.Toolbox()


def creator(agent_type):
    x = random.random() * X_MAX
    y = random.random() * Y_MAX
    return agent_type(space, x, y)


g_toolbox.register('individual', creator, Boids.GrassAgent)
g_toolbox.register('population', tools.initRepeat, list, g_toolbox.individual)

s_toolbox.register('individual', creator, Boids.SheepAgent)
s_toolbox.register('population', tools.initRepeat, list, s_toolbox.individual)

w_toolbox.register('individual', creator, Boids.WolfAgent)
w_toolbox.register('population', tools.initRepeat, list, w_toolbox.individual)

if __name__ == '__main__':
    random.seed(64)

    grass = g_toolbox.population(n=GRASS_COUNT)
    sheep = s_toolbox.population(n=SHEEP_COUNT)
    wolfs = w_toolbox.population(n=WOLFS_COUNT)

    s_hof = tools.HallOfFame(10)
    w_hof = tools.HallOfFame(10)

    s_stats = tools.Statistics(lambda ind: ind.fitness.values)
    s_stats.register('avg', numpy.average)
    s_stats.register('std', numpy.std)
    s_stats.register('min', numpy.min)
    s_stats.register('max', numpy.max)

    logbook = tools.Logbook()
    logbook.header = 'gen', 'evals', 'std', 'min', 'avg', 'max'
