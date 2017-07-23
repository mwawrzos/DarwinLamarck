import itertools

import numpy as np

from MathUtlis import norm, v_len, vector2d
from Types import t_matcher


def match(neighbours):
    return np.mean([neighbour.heading for neighbour in neighbours]) if len(neighbours) else np.array([0, 0])


class Flock:
    def __init__(self, agent, space, coherence_w=1, separate_w=1, match_w=1, separation=1.5):
        self.agent = agent
        self.space = space
        self.coherence_w = coherence_w
        self.separate_w = separate_w
        self.match_w = match_w
        self.separate = Separate(agent, space, separation)

    def __call__(self, neighbours):
        neighbours = list(filter(t_matcher(type(self.agent)), neighbours))
        coherence = cohere(self.agent, self.space, neighbours) * self.coherence_w
        separation = self.separate(neighbours) * self.separate_w
        matching = match(neighbours) * self.match_w
        return coherence + separation + matching


def cohere(agent, space, neighbours):
    i = map(vector2d(space), itertools.repeat(agent.pos), [n.pos for n in neighbours])
    neighbours_vector = sum(i, np.array([0, 0]))
    return norm(neighbours_vector)


class Separate:
    def __init__(self, agent, space, separation=1.5):
        self.agent = agent
        self.separation = separation
        self.space = space

    def __call__(self, neighbours):
        close_neighbours = filter(self.close_enough, [n.pos for n in neighbours])
        neighbours_vectors = map(vector2d(self.space),
                                 close_neighbours,
                                 itertools.repeat(self.agent.pos))
        neighbours_separation = map(self.separation_vector, neighbours_vectors)
        # noinspection PyTypeChecker
        return sum(neighbours_separation, np.array([0, 0]))

    def close_enough(self, neighbour):
        return self.space.get_distance(self.agent.pos, neighbour) < self.separation

    def separation_vector(self, neighbour_vector):
        length = v_len(neighbour_vector)
        return neighbour_vector * (self.separation - length) / length
