
import unittest

import scipy.stats as stats
import numpy as np

import despy.stats.random as dsr
from despy.output.statistic import Statistic, StatisticNotFinalizedError



class testStatistic(unittest.TestCase):
    
    def test_stat(self):
        print()
        print("======Statistic First Test=====")
        stat1 = Statistic('stat1', 'i4', 5)
        dsr.seed(731)
                
        dist_v = stats.expon(100)
        dist_num = stats.expon(3)
        dist_time = stats.expon(10)

        for i in range(5):
            time = 0
            for _ in range(round(dist_num.rvs())):
                time += round(dist_time.rvs())
                value = round(dist_v.rvs())
                stat1.append(i, time, value)
                
        times = [[13, 24, 35, 45],
                     [10, 21, 35, 47],
                     [11, 21, 32, 49, 60],
                     [10, 23, 33],
                     [11, 22, 34, 45]]
        
        vals = [[100, 100, 100, 100],
                   [103, 102, 102, 102],
                   [101, 101, 102, 101, 101],
                   [101, 101, 101],
                   [100, 101, 104, 100]]
         
        self.assertListEqual(times, stat1.times.tolist())
        self.assertListEqual(vals, stat1.values.tolist())
        print(stat1.values)
        
        print("=====Pre-Finalized=====")
        print("rep_means: {}".format(stat1.rep_means))
        res_means = [sum(vals[i])/len(vals[i]) \
                    for i in range(len(vals))]
        self.assertListEqual(res_means, stat1.rep_means.tolist())
        
        print("total_length: {}".format(stat1.total_length))
        length = sum([len(times[i]) for i in range(len(times))])
        self.assertEqual(stat1.total_length, length)
        
        print("mean: {}".format(stat1.mean))
        total_sum = sum([sum(vals[i]) for i in range(len(vals))])
        mean = total_sum / length
        self.assertEqual(stat1.mean, mean)
        
        stat1.finalize()
        
        self.assertListEqual(times, stat1.times.tolist())
        self.assertListEqual(vals, stat1.values.tolist())
        
        print()
        print("=====Post-Finalized=====")
        print("rep_means: {}".format(stat1.rep_means))
        self.assertListEqual(res_means, stat1.rep_means.tolist())
        
        print("total_length: {}".format(stat1.total_length))
        self.assertEqual(stat1.total_length, length)
        
        print("mean: {}".format(stat1.mean))
        self.assertEqual(stat1.mean, mean)
