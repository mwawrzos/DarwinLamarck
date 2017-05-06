import numpy as np

from MathUtlis import norm, neighbours_vectors, v_len
from Types import t_matcher


def cohere(me, neighbours):
    return -norm(sum(neighbours_vectors(me, neighbours),
                     np.array([0, 0])))


def match(neighbours):
    return np.mean([neighbour.heading for neighbour in neighbours]) if len(neighbours) else np.array([0, 0])


class Flock:
    def __init__(self, flock_mem_type, coherence_w=1, separate_w=1, match_w=1, separation=1.5):
        self.coherence_w = coherence_w
        self.separate_w = separate_w
        self.match_w = match_w
        self.flock_mem_type = flock_mem_type
        self.separation = separation

    def separation_scaling(self, vector):
        length = v_len(vector)
        return vector * (self.separation - length) / length

    def separate(self, me, neighbours):
        # noinspection PyTypeChecker
        return sum(map(self.separation_scaling,
                       filter(lambda v: v_len(v) < self.separation,
                              neighbours_vectors(me, neighbours))),
                   np.array([0, 0]))

    def __call__(self, me, neighbours):
        neighbours = list(filter(t_matcher(self.flock_mem_type), neighbours))
        coherence = cohere(me, neighbours) * self.coherence_w
        separation = self.separate(me, neighbours) * self.separate_w
        matching = match(neighbours) * self.match_w
        return coherence + separation + matching
