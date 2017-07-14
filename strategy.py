from bisect import bisect_left

import numpy as np

from MathUtlis import norm


class Decision(object):
    def __init__(self, value_func, a, b, decision, speed=0.03, cost=1, inertia=0.3) -> None:
        self.value_func = value_func
        self.a = a
        self.b = b
        self.decision = decision
        self.speed = speed
        self.inertia = inertia
        self.cost = cost
        self.target = np.array([0, 0])

    def value(self, *args, **kwargs):
        return self.value_func(*args, **kwargs) * self.a + self.b

    def __call__(self, *args, **kwargs):
        return self.decision(*args, **kwargs)

    def update_heading(self, heading, *args, **kwargs):
        self.target = self.decision(*args, **kwargs)
        return norm(norm(self.target) * self.inertia + heading)

    def update_position(self, pos, heading):
        new_x, new_y = np.array(pos) + heading * self.speed
        return new_x, new_y


class WeighedRandom:
    def __init__(self, decisions):
        self.decisions = decisions
        self.decision = 0

    def __call__(self, *args, **kwargs):
        last_value = 0
        decisions = []
        for decision in self.decisions:
            last_value += decision.value(*args, **kwargs)
            decisions.append(last_value)
        decision = np.random.randint(last_value + 1)

        self.decision = bisect_left(decisions, decision)
        return self.decisions[self.decision]
