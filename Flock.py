import itertools

import numpy as np

from MathUtlis import norm, pos_vector, v_len, vector2d
from Types import t_matcher


def match(neighbours):
    return np.mean([neighbour.heading for neighbour in neighbours]) if len(neighbours) else np.array([0, 0])


class Flock:
    def __init__(self, me, space, coherence_w=1, separate_w=1, match_w=1, separation=1.5):
        self.me = me
        self.space = space
        self.coherence_w = coherence_w
        self.separate_w = separate_w
        self.match_w = match_w
        self.separation = separation

    def separation_scaling(self, vector):
        length = v_len(vector)
        return vector * (self.separation - length) / length

    def separation_vector(self, neighbour_vector):
        length = v_len(neighbour_vector)
        return neighbour_vector * (self.separation - length) / length

    def separate(self, neighbours):
        def close_enough(neighbour):
            return self.space.get_distance(self.me.pos, neighbour) < self.separation

        close_neighbours = filter(close_enough, map(pos_vector, neighbours))
        neighbours_vectors = map(vector2d(self.space),
                                 close_neighbours,
                                 itertools.repeat(self.me.pos))
        neighbours_separation = map(self.separation_vector, neighbours_vectors)
        return sum(neighbours_separation)

    def __call__(self, neighbours):
        neighbours = list(filter(t_matcher(type(self.me)), neighbours))
        coherence = self.cohere(neighbours) * self.coherence_w
        separation = self.separate(neighbours) * self.separate_w
        matching = match(neighbours) * self.match_w
        return coherence + separation + matching

    def cohere(self, neighbours):
        i = map(vector2d(self.space), itertools.repeat(self.me.pos), map(pos_vector, neighbours))
        neighbours_vector = sum(i, np.array([0, 0]))
        return norm(neighbours_vector)
