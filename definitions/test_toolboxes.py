import unittest
import random

from . import toolboxes

class TestToolbox(unittest.TestCase):
    MAX = 100
    
    def the_same_with_fixed_seed(self, constructor, *args):
        random.seed(42)
        a = constructor(*args)
        random.seed(42)
        b = constructor(*args)
        self.assertEqual(a, b)

        
class TestCommonToolbox(TestToolbox):
    def setUp(self):
        self.common_tbx = toolboxes.create_common_toolbox(self.MAX)
        
    def test_random_in_bounds(self):
        rnd = self.common_tbx.random()
        self.assertGreater(rnd, 0)
        self.assertLess(rnd, self.MAX)
        
    def test_random_the_same_with_fixed_seed(self):
        self.the_same_with_fixed_seed(self.common_tbx.random)
        

class TestSheepToolbox(TestToolbox):
    N = 3
    def setUp(self):
        self.common_tbx = toolboxes.create_common_toolbox(self.MAX)
        self.s_toolbox = toolboxes.create_sheep_toolbox(self.common_tbx)
        
    def test_individual_the_same_with_fixed_seed(self):
        self.the_same_with_fixed_seed(self.s_toolbox.individual)
        
    def test_population_the_same_with_fixed_seed(self):
        self.the_same_with_fixed_seed(self.s_toolbox.population, self.N)

class TestWolvesToolbox(TestToolbox):
    N = 2
    def setUp(self):
        self.common_tbx = toolboxes.create_common_toolbox(self.MAX)
        self.w_toolbox = toolboxes.create_wolves_toolbox(self.common_tbx)

    def test_individual_the_same_with_fixed_seed(self):
        self.the_same_with_fixed_seed(self.w_toolbox.individual)

    def test_population_the_same_with_fixed_seed(self):
        self.the_same_with_fixed_seed(self.w_toolbox.population, self.N)
