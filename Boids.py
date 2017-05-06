from math import sqrt
from Types import t_matcher

import numpy as np


def vector_from(agent):
    return lambda neighbour: agent - neighbour


def neighbours_vectors(me, neighbours):
    return map(vector_from(me),
               map(BaseAgent.pos_vector,
                   neighbours))


def sqr_dst(vec):
    return vec[0] * vec[0] + vec[1] * vec[1]


def v_len(vec):
    return sqrt(sqr_dst(vec))


class BaseAgent:
    vision = 2

    def __init__(self, unique_id, space, x, y):
        super().__init__()
        self.unique_id = unique_id
        self.space = space
        self.pos = (x, y)
        self.space.place_agent(self, self.pos)

        self.decision = -1
        self.heading = None
        self.max_speed = None

    def draw(self):
        pass

    def pos_vector(self):
        return np.array(self.pos)


class MarkerAgent(BaseAgent):
    def __init__(self, unique_id, space, x, y):
        super().__init__(unique_id, space, x, y)

    def draw(self):
        return {'Color': 'black', 'r': 1}

    def step(self):
        pass

    def advance(self):
        pass


class GrassAgent(BaseAgent):
    def draw(self):
        return {'Color': 'green', 'r': 3}

    def step(self):
        pass

    def advance(self):
        pass


def norm(new_heading):
    length = v_len(new_heading)
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
        return {'Color': 'blue', 'r': 5, 'rs': BaseAgent.vision}

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
        self.decision = np.random.choice(self.asd)
        return decisions[self.decision]


def cohere(me, neighbours):
    return -norm(sum(neighbours_vectors(me, neighbours),
                     np.array([0, 0])))


def separation_scaling(vector):
    length = v_len(vector)
    return vector * (1.5 - length) / length


def separate(me, neighbours):
    return sum(map(separation_scaling,
                   filter(lambda v: v_len(v) < 1.5,
                          neighbours_vectors(me, neighbours))),
               np.array([0, 0]))


def match(neighbours):
    return np.mean([neighbour.heading for neighbour in neighbours]) if len(neighbours) else np.array([0, 0])


def flocking(me, neighbours):
    neighbours = list(filter(t_matcher(SheepAgent), neighbours))
    return cohere(me, neighbours) + separate(me, neighbours) + match(neighbours)


def eating(me, neighbours):
    neighbours = list(filter(t_matcher(GrassAgent), neighbours))
    if len(neighbours):
        return min(neighbours_vectors(me, neighbours),
                   key=sqr_dst)
    else:
        return np.array([0, 0])


def escaping(me, neighbours):
    return np.array([.0,.0])


decisions = [flocking, eating, escaping]
