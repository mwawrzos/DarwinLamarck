from unittest import TestCase

import numpy as np
from mesa.space import ContinuousSpace

from MathUtlis import vector2d

SIZE = 10
ZERO = np.array([0, 0])
ONE = np.array([1, 1])

maker = vector2d(ContinuousSpace(10, 10, True))


class TestVector2d(TestCase):
    def test_vector2d(self):
        np.testing.assert_equal(maker(ZERO, ONE), ONE)
        np.testing.assert_equal(maker(ONE, ZERO), -ONE)
        np.testing.assert_equal(maker(ONE, ONE), -ZERO)
