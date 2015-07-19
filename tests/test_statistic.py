
import unittest

import scipy.stats as stats
import numpy as np

import despy.stats.random as dsr
from despy.output.statistic import Statistic, StatisticNotFinalizedError



class testRandom(unittest.TestCase):
    
    def test_stat(self):
        print()
        print("======Statistic First Test=====")
        stat1 = Statistic('stat1', 'i4')
        
        dsr.seed(731)
        exp_values = [101, 103, 100, 101, 100, 101, 100, 100, 100, 101]
                
        dist = stats.expon(100)
                
        for i in range(10):
            stat1.append(1, 1, i, round(dist.rvs()))
        

        
        self.assertEqual(len(stat1), 10)
        self.assertListEqual(exp_values, stat1.obs)
        
        print("=====Values before Finalization=====")
        for i in range(10):
            print(stat1[i])
            
        self.assertEqual(stat1.mean, np.mean(np.array(exp_values)))
            
        stat1.finalize()
            
        print ("=====Values after Finalization=====")
        for i in range(10):
            print(stat1[i])
        
        self.assertIsInstance(stat1.obs, np.ndarray)
        self.assertListEqual(exp_values, stat1.obs.tolist())
        with self.assertRaises(StatisticNotFinalizedError):
            stat1.append(2, 2, 2, 2)
            
        print("=====Estimates=====")
        print("Mean: {}".format(stat1.mean))
        self.assertEqual(stat1.mean, np.mean(np.array(exp_values)))
