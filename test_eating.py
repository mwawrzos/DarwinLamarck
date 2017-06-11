from unittest import TestCase
from unittest.mock import Mock

import numpy as np
from mesa.space import ContinuousSpace

from Boids import eating


class Food:
    pass


class NotFood:
    pass


MY_POS = np.array([1, 2])
ME = Mock(pos=MY_POS)
CLOSE_FOOD_VECTOR = np.array([-2, -3])
FAR_FOOD_VECTOR = np.array([4, -3])
NULL_VECTOR = np.array([0, 0])

SIZE = 10

space_mock = ContinuousSpace(SIZE, SIZE, True)

food_mock = Mock(spec=Food,
                 pos=MY_POS + CLOSE_FOOD_VECTOR)
far_food_mock = Mock(spec=Food,
                     pos=MY_POS + FAR_FOOD_VECTOR)
not_food_mock = Mock(spec=NotFood)

decision = eating(ME, Food, space_mock)


class TestEating(TestCase):
    def test_can_find_food(self):
        neighbours = [food_mock]
        np.testing.assert_equal(decision(neighbours), CLOSE_FOOD_VECTOR)

    def test_doesnt_eat_uneatable(self):
        neighbors = [not_food_mock]
        np.testing.assert_equal(decision(neighbors), NULL_VECTOR)

    def test_finds_food_between_uneatable(self):
        neighbors = [food_mock, not_food_mock]
        np.testing.assert_equal(decision(neighbors), CLOSE_FOOD_VECTOR)

    def test_finds_nearest_food(self):
        neighbors = [food_mock, far_food_mock]
        np.testing.assert_equal(decision(neighbors), CLOSE_FOOD_VECTOR)
