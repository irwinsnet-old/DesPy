
import unittest

import scipy.stats as stats

import despy.stats.random as dsr
from despy.output.statistic import Statistic



class testRandom(unittest.TestCase):
    
    def test_stat(self):
        print()
        print("======Statistic First Test=====")
        stat1 = Statistic('stat1', 'i4')
        
        dsr.seed(731)
        dist = stats.expon(100)
        
        for i in range(10):
            stat1.append(1, 1, i, round(dist.rvs()))
        
        self.assertEqual(len(stat1), 10)
        
        print("=====Values before Finalization=====")
        for i in range(10):
            print(stat1[i])
            
        stat1.finalize()
            
        print ("=====Values after Finalization=====")
        for i in range(10):
            print(stat1[i])
