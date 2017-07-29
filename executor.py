import os
from datetime import datetime
from multiprocessing.pool import Pool

from gen import Sim, save_results
from lamarck import Lamarck


def DUMMY_PARAMS():
    return {
        'X_MAX': 20,
        'Y_MAX': 20,
        'MAX_ITER': 5,
        'MAX_GEN': 5,
        'GRASS_COUNT': 100,
        'SHEEP_COUNT': 50,
        'WOLFS_COUNT': 10,
        'S_CXPB': 0.5,
        'W_CXPB': 0.5,
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

    sim = Sim(False)
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
    _date = str(datetime.now().strftime('%y%b%d%H%M%S'))
    with Pool(3) as _p:
        for _i in range(3):
            len1 = len(simulations)
            fs = _p.map(start_sim, zip(simulations, [_i] * len1, [_date] * len1))
