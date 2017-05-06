import numpy as np

from math import sqrt


def pos_vector(self):
    return np.array(self.pos)


def vector_from(agent):
    return lambda neighbour: agent - neighbour


def neighbours_vectors(me, neighbours):
    return map(vector_from(me),
               map(pos_vector,
                   neighbours))


def norm(new_heading):
    length = v_len(new_heading)
    if length:
        new_heading = new_heading / length
    return new_heading


def sqr_dst(vec):
    return vec[0] * vec[0] + vec[1] * vec[1]


def v_len(vec):
    return sqrt(sqr_dst(vec))
