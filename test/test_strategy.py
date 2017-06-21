from unittest import TestCase

import mock

from strategy import WeighedRandom, Decision

DECISION1_A = 1
DECISION1_B = 2
DECISION2_A = 3
DECISION2_B = 4

DECISION1_RES = 5
DECISION2_RES = 6

ALLIES = 7
ENEMIES = 8


def couple(neighbours):
    enemies_count = neighbours.count(ENEMIES)
    return neighbours.count(ALLIES) / enemies_count if enemies_count else 0


def fear(neighbours):
    allies_count = neighbours.count(ALLIES)
    return neighbours.count(ENEMIES) / allies_count if allies_count else 0


def first_decision(_):
    return DECISION1_RES


def second_decision(_):
    return DECISION2_RES


decisions_ = [Decision(couple, DECISION1_A, DECISION1_B, first_decision),
              Decision(fear, DECISION2_A, DECISION2_B, second_decision)]
random_strategy = WeighedRandom(decisions_)


class TestStrategy(TestCase):
    @mock.patch('strategy.np.random')
    def test_no_neighbourhood(self, np_random_mock):
        neighbours = []

        np_random_mock.randint.return_value = 0
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION1_RES)
        np_random_mock.randint.return_value = DECISION1_B / 2
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION1_RES)
        np_random_mock.randint.return_value = DECISION1_B
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION1_RES)

        np_random_mock.randint.return_value = DECISION1_B + 0.1
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION2_RES)
        np_random_mock.randint.return_value = DECISION1_B + DECISION2_B / 2
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION2_RES)
        np_random_mock.randint.return_value = DECISION1_B + DECISION2_B
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION2_RES)

    @mock.patch('strategy.np.random')
    def test_more_enemies(self, np_random_mock):
        neighbours = [ENEMIES] * 3 + [ALLIES] * 2

        np_random_mock.randint.return_value = 0
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION1_RES)
        np_random_mock.randint.return_value = DECISION1_A * 2 / 3
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION1_RES)
        np_random_mock.randint.return_value = DECISION1_A * 2 / 3 + DECISION1_B
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION1_RES)

        np_random_mock.randint.return_value = DECISION1_A * 2 / 3 + DECISION1_B + 0.1
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION2_RES)
        np_random_mock.randint.return_value = DECISION1_A * 2 / 3 + DECISION1_B + DECISION2_A * 3 / 2 + DECISION2_B
        self.assertEqual(random_strategy(neighbours)(neighbours), DECISION2_RES)
