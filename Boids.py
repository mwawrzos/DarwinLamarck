from math import sqrt

from numpy import random, mean

import numpy as np


class BaseAgent:
    vision = 5

    def __init__(self, unique_id, space, x, y):
        super().__init__()
        self.unique_id = unique_id
        self.space = space
        self.pos = (x, y)
        self.space.place_agent(self, self.pos)

        self.decision = -1

    def draw(self):
        return self.draw()


class GrassAgent(BaseAgent):
    def draw(self):
        return {'Color': 'green', 'r': 3}

    def step(self):
        pass

    def advance(self):
        pass


def norm(new_heading):
    length = np.linalg.norm(new_heading)
    if length:
        new_heading = new_heading / length
    return new_heading


class SheepAgent(BaseAgent):
    def __init__(self, unique_id, space, x, y, max_speed=0.03, heading=None):
        super().__init__(unique_id, space, x, y)
        self.max_speed = max_speed
        self.heading = heading if heading else np.random.random(2)
        self.asd = [i for (i, c) in enumerate([33, 22, 3]) for _ in range(c)]

        self.new_pos = None

    def draw(self):
        return {'Color': 'blue', 'r': 5}

    def step(self):
        self.update_heading(self.space.get_neighbors(self.pos, BaseAgent.vision, False))
        new_pos = np.array(self.pos) + self.heading * self.max_speed
        (new_x, new_y) = new_pos
        self.new_pos = new_x, new_y

    def advance(self):
        self.space.move_agent(self, self.new_pos)

    def update_heading(self, neighbours):
        new_heading = self.distributed_decision()(np.array(self.pos), neighbours)
        self.heading += norm(new_heading) * 0.3
        self.heading = norm(self.heading)

    def distributed_decision(self):
        self.decision = random.choice(self.asd)
        return decisions[self.decision]


def sqr_dst(vec):
    return vec[0]*vec[0] + vec[1]*vec[1]


def cohere(neighbours):
    return norm(sum([np.array(neighbour.pos) for neighbour in neighbours]))


def separation_vector(dist_vector):
    return np.array([0, 0]) if sqrt(sqr_dst(dist_vector)) > 5 else -dist_vector


def separate(me, neighbours):
    return norm(sum([separation_vector(me - np.array(neighbour.pos))
                     for neighbour in neighbours]))


def match(neighbours):
    return mean([neighbour.pos for neighbour in neighbours])


def flocking(me, neighbours):
    neighbours = [neighbour
                  for neighbour in neighbours
                  if type(neighbour) is SheepAgent]
    return cohere(neighbours) + separate(me, neighbours) + match(neighbours)


def eating(me, neighbours):
    closest = min([me - np.array(neighbour.pos)
                   for neighbour in neighbours
                   if type(neighbour) is GrassAgent],
                  key=sqr_dst)
    return -closest


def escaping(me, neighbours):
    return np.array([.0,.0])


decisions = [flocking, eating, escaping]
