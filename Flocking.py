import numpy as np

from Types import t_matcher
from MathUtlis import norm, neighbours_vectors, v_len


def cohere(me, neighbours):
    return -norm(sum(neighbours_vectors(me, neighbours),
                     np.array([0, 0])))


def match(neighbours):
    return np.mean([neighbour.heading for neighbour in neighbours]) if len(neighbours) else np.array([0, 0])


class Flocking:
    def __init__(self, agent_type, separation):
        self.agent_type = agent_type
        self.separation = separation

    def separation_scaling(self, vector):
        length = v_len(vector)
        return vector * (self.separation - length) / length

    def separate(self, me, neighbours):
        return sum(map(self.separation_scaling,
                       filter(lambda v: v_len(v) < self.separation,
                              neighbours_vectors(me, neighbours))),
                   np.array([0, 0]))

    def __call__(self, me, neighbours):
        neighbours = list(filter(t_matcher(self.agent_type), neighbours))
        return cohere(me, neighbours) + self.separate(me, neighbours) + match(neighbours)
