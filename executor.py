import itertools
import os
from datetime import datetime
from multiprocessing.pool import Pool

from gen import Sim, save_results
from lamarck import Lamarck

VERBOSE = True
START = 0
END = 50
DATE = None


def DUMMY_PARAMS():
    return {
        'X_MAX': 10,
        'Y_MAX': 10,
        'MAX_ITER': 500,
        'MAX_GEN': 40,
        'GRASS_COUNT': 100,
        'SHEEP_COUNT': 50,
        'WOLFS_COUNT': 10,
        'S_CXPB': 0.25,
        'W_CXPB': 0.25,
        'S_MUTPB': 0.1,
        'W_MUTPB': 0.1,
        'S_TOUR_SIZE': 3,
        'W_TOUR_SIZE': 3,
        'SHEEP_LAMARCK': Lamarck(0.1, 0.1, 0.1),
        'WOLFS_LAMARCK': Lamarck(0.1, 0.1, 0.1)
    }


def w_nothing(ret=DUMMY_PARAMS()):
    ret['WOLFS_LAMARCK'] = None
    ret['W_CXPB'] = 0
    ret['W_MUTPB'] = 0
    ret['W_TOUR_SIZE'] = 1
    return ret


def s_nothing(ret=DUMMY_PARAMS()):
    ret['SHEEP_LAMARCK'] = None
    ret['S_CXPB'] = 0
    ret['S_MUTPB'] = 0
    ret['S_TOUR_SIZE'] = 1
    return ret


def no_mutation(ret=DUMMY_PARAMS()):
    ret['SHEEP_LAMARCK'] = None
    ret['WOLFS_LAMARCK'] = None
    ret['S_CXPB'] = 0
    ret['W_CXPB'] = 0
    ret['S_MUTPB'] = 0
    ret['W_MUTPB'] = 0
    return ret


def no_mutation_no_selection(ret=DUMMY_PARAMS()):
    ret = no_mutation(ret)
    ret['S_TOUR_SIZE'] = 1
    ret['W_TOUR_SIZE'] = 1
    return ret


def w_no_mutation_no_selection():
    ret = DUMMY_PARAMS()
    ret['WOLFS_LAMARCK'] = None
    ret['W_CXPB'] = 0
    ret['W_MUTPB'] = 0
    return ret


def lamarck():
    ret = DUMMY_PARAMS()
    return ret


def s_darwin(ret=DUMMY_PARAMS()):
    ret['SHEEP_LAMARCK'] = None
    return ret


def w_darwin(ret=DUMMY_PARAMS()):
    ret['WOLFS_LAMARCK'] = None
    return ret


def wymysl(param):
    if param['SHEEP_LAMARCK'] is None:
        if param['S_MUTPB'] == 0:
            if param['S_TOUR_SIZE'] == 1:
                sheep = 'TWO__NO'
            else:
                sheep = 'ONE__NO'
        else:
            sheep = 'kDarwin'
    else:
        sheep = 'lamarck'
    if param['WOLFS_LAMARCK'] is None:
        if param['W_MUTPB'] == 0:
            if param['W_TOUR_SIZE'] == 1:
                wolfs = 'TWO__NO'
            else:
                wolfs = 'ONE__NO'
        else:
            wolfs = 'kDarwin'
    else:
        wolfs = 'lamarck'
    return 's_%s-w_%s' % (sheep, wolfs)


def start_sim(args):
    params, i, date = args
    name = '%s' % (wymysl(params))
    directory = os.path.join('cp', date, name, str(i))

    sim = Sim(VERBOSE)
    for p in params:
        sim.__setattr__(p, params[p])
    print('start > %s' % name)
    res = sim.main()
    print('end   > %s' % name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_results(directory, res.cps)
    sim.write_summary(res, directory)


simulations = [
    no_mutation_no_selection(),
    no_mutation(),
    lamarck(),
    w_darwin(s_darwin()),
    s_darwin(lamarck()),
    w_darwin(lamarck()),
    s_nothing(lamarck()),
    w_nothing(lamarck()),
    s_nothing(w_darwin()),
    w_nothing(s_darwin())
]

if __name__ == '__main__':
    _date = DATE if DATE else str(datetime.now().strftime('%y%b%d%H%M%S'))
    _date = itertools.repeat(_date)

    _simulations = simulations * (END - START)

    _input = ((simulation, i, date)
              for ((i, simulation), date)
              in zip(enumerate(_simulations, START), _date))

    with Pool(3) as _p:
        _p.map(start_sim, _input)
