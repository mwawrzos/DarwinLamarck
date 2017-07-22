from bisect import bisect_left

import numpy as np

from MathUtlis import norm


def limited(val):
    return max(0, min(1000, val))


class Decision(object):
    def __init__(self, value_func, a, b, decision, speed_weight=0, inertia=0.3) -> None:
        self.value_func = value_func
        self.a = a
        self.b = b
        self.decision = decision
        self.target = np.array([0, 0])
        self.inertia = inertia
        self.speed_weight = speed_weight
        self.speed, self.cost = 0.03, 1
        self.update_speed()

    def update_speed(self):
        self.speed = 0.03 + self.speed_weight / 1000 * 0.03
        self.cost = 1 + self.speed_weight / 1000 * 3

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

    def lamarck_mutation(self, value):
        last = 3 if self.speed_weight else 2
        i = np.random.randint(last)
        if i == 0:
            self.a = limited(self.a + value)
        elif i == 1:
            self.b = limited(self.b + value)
        else:
            self.speed_weight = limited(self.speed_weight + value)
            self.update_speed()


class WeighedRandom:
    def __init__(self, lamarck, decisions):
        self.lamarck = lamarck
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

        if self.lamarck:
            self.lamarck.mut(self.decisions, self.decision)

        return self.decisions[self.decision]
