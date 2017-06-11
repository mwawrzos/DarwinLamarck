from math import sqrt

import numpy as np


def pos_vector(self):
    return np.array(self.pos)


def vector_from(agent):
    return lambda neighbour: agent - neighbour


def norm(new_heading):
    length = v_len(new_heading)
    if length:
        new_heading = new_heading / length
    return new_heading


def sqr_dst(vec):
    return vec[0] * vec[0] + vec[1] * vec[1]


def v_len(vec):
    return sqrt(sqr_dst(vec))


def vector2d(space):
    def vector_2d(from_, to):
        x1, y1 = from_
        x2, y2 = to

        dx = x2 - x1
        dy = y2 - y1

        dx1 = -np.sign(dx) * space.x_max + dx
        dy1 = -np.sign(dy) * space.y_max + dy

        dx = dx if abs(dx / dx1) <= 1 else dx1
        dy = dy if abs(dy / dy1) <= 1 else dy1

        return np.array([dx, dy])

    return vector_2d
