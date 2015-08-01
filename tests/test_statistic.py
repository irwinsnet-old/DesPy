
import unittest, statistics

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
        
        r_lens = []; times = []; values = []
 
        reps = 5
        for rep in range(reps):
            time = 0
            r_lens.append(round(dist_num.rvs()))
            for _ in range(r_lens[-1]):
                time += round(dist_time.rvs())
                value = round(dist_v.rvs())
                stat1.append(time, value)
                times.append(time)
                values.append(value)
            if rep < reps - 1:
                stat1.increment_rep()

        print("=====Checking Test Setup Data=====")
        self.assertListEqual(stat1.rep_lengths.tolist(), r_lens)
        self.assertListEqual(times, stat1.times.tolist())
        self.assertListEqual(values, stat1.values.tolist())
        print("Test Values: {}".format(stat1.values))
        print("Replication Lengths: {}".format(r_lens))
        print("Statistic Index: {}".format(stat1.index))

        print()
        print("=====Pre-Finalized=====")
        
        print("total_length: {}".format(stat1.total_length))
        total_length = sum(r_lens)
        self.assertEqual(stat1.total_length, total_length)
        
        print("mean: {}".format(stat1.mean))
        mean = statistics.mean(values)
        self.assertEqual(stat1.mean, mean)

        print("rep_means: {}".format(stat1.rep_means))
        rep_means = []; r_beg = 0
        for length in r_lens:
            r_end = r_beg + length
            r_mean = sum(values[r_beg:r_end]) / length
            rep_means.append(r_mean)
            r_beg += length
        self.assertListEqual(rep_means, stat1.rep_means.tolist())

        print()
        print("=====Post-Finalized=====")
        stat1.finalize()
         
        self.assertListEqual(times, stat1.times.tolist())
        self.assertListEqual(values, stat1.values.tolist())

        print("total_length: {}".format(stat1.total_length))
        self.assertEqual(stat1.total_length, total_length)

        print("mean: {}".format(stat1.mean))
        self.assertEqual(stat1.mean, mean)

        print("rep_means: {}".format(stat1.rep_means))
        self.assertListEqual(stat1.rep_means.tolist(), rep_means)
         

