import unittest
from deap import creator, base

from . import creators

class TestFitnessMax(unittest.TestCase):
    def test_enables_creation(self):
        self.assertIsInstance(creator.FitnessMax((1,)),
                         base.Fitness)

class TestSheep(unittest.TestCase):
    def test_enables_creation(self):
        self.assertEqual(creator.Sheep((1,)),
                         [1])

class TestWolf(unittest.TestCase):
    def test_enables_creation(self):
        self.assertEqual(creator.Wolf((1,)),
                         [1])
