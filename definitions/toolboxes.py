import random
from deap import base, tools, creator

def create_common_toolbox(max_rand_value):
    common_tbx = base.Toolbox()
    common_tbx.register('random',
                        random.randint,
                        a=0,
                        b=max_rand_value)
    return common_tbx

def create_sheep_toolbox(common_tbx):
    s_toolbox = base.Toolbox()
    s_toolbox.register('individual',
                       tools.initRepeat,
                       creator.Sheep,
                       common_tbx.random,
                       n=7)
    s_toolbox.register('population',
                       tools.initRepeat,
                       list,
                       s_toolbox.individual)
    return s_toolbox

def create_wolves_toolbox(common_tbx):
    s_toolbox = base.Toolbox()
    s_toolbox.register('individual',
                       tools.initRepeat,
                       creator.Wolf,
                       common_tbx.random,
                       n=5)
    s_toolbox.register('population',
                       tools.initRepeat,
                       list,
                       s_toolbox.individual)
    return s_toolbox