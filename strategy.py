from bisect import bisect_left

import numpy as np


class Decision(object):
    def __init__(self, value_func, a, b, decision) -> None:
        self.value_func = value_func
        self.a = a
        self.b = b
        self.decision = decision

    def value(self, *args, **kwargs):
        return self.value_func(*args, **kwargs) * self.a + self.b

    def __call__(self, *args, **kwargs):
        return self.decision(*args, *kwargs)


class WeighedRandom(list):
    def __call__(self, *args, **kwargs):
        last_value = 0
        decisions = []
        for decision in self:
            last_value += decision.value(*args, **kwargs)
            decisions.append(last_value)
        decision = np.random.randint(last_value + 1)

        self.decision = bisect_left(decisions, decision)
        return self[self.decision]
