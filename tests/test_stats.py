
import unittest

import despy.stats.random as dsr

class testRandom(unittest.TestCase):
    
    def test_seed(self):
        self.assertRaises(TypeError, dsr.seed, "seed")
        dsr.seed(None)
        dsr.seed(731)
        
    def test_Emperical(self):
        dsr.seed(731)
        values = [1, 2, 3, 4]
        probabilities = [0.25, 0.40, 0.20, 0.15]
        dpf =  dsr.get_empirical_pmf(values, probabilities)
        rv_result = [2, 4, 1, 2, 2, 2, 2, 2, 2, 3]
        self.assertListEqual(list(dpf.rvs(size=10)), rv_result)      
        
    def test_Poisson(self):
        print()
        print("===== Poisson Test=====")
        # Get a single Poisson random number
        poisson_pmf = dsr.get_poisson_pmf(28)
        self.assertIsInstance(poisson_pmf.rvs(), int)