
import unittest, statistics

import scipy.stats as stats

import despy.stats.random as dsr
from despy.output.statistic import DiscreteStatistic
from despy.output.statistic import TimeWeightedStatistic

class testStatistic(unittest.TestCase):
    
    def test_stat(self):
        print()
        print("======Statistic First Test=====")
        stat1 = DiscreteStatistic('stat1', 'i4')
        dsr.seed(731)
                
        dist_v = stats.expon(100)
        dist_num = stats.expon(3)
        dist_time = stats.expon(10)
        
        r_lens = []; times = []; values = []
 
        reps = 5
        for _ in range(reps):
            time = 0
            r_lens.append(round(dist_num.rvs()))
            stat1.start_rep()
            for _ in range(r_lens[-1]):
                time += round(dist_time.rvs())
                value = round(dist_v.rvs())
                stat1.append(time, value)
                times.append(time)
                values.append(value)
            stat1.end_rep()

        print("=====Checking Test Setup Data=====")
        self.assertListEqual(stat1.rep_lengths.tolist(), r_lens)
        self.assertListEqual(times, stat1.times.tolist())
        self.assertListEqual(values, stat1.values.tolist())
        print("Test Values: {}".format(stat1.values))
        print("Replication Lengths: {}".format(r_lens))
#         print("Statistic Index: {}".format(stat1.index))

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

    def test_time_weighted_mean(self):
        print()
        print("============================")
        print("=====Time-Weighted-Mean=====")
        stat2 = TimeWeightedStatistic('time_weighted_stat', 'i4')
        dsr.seed(731)
                 
        dist_v = stats.expon(50)
        dist_num = stats.expon(7)
        dist_time = stats.expon(17)
        dist_rep_end = stats.expon(2)
         
        r_lens = []; times = []; values = []; spans = []
  
        reps = 3
        for _ in range(reps):
            time = 0
            r_lens.append(round(dist_num.rvs()))
            stat2.start_rep()
            stat2.append(0, 0)
            times.append(0)
            values.append(0)
            for _ in range(r_lens[-1]):
                span = round(dist_time.rvs())
                spans.append(span)
                time += round(span)
                value = round(dist_v.rvs())
                stat2.append(time, value)
                times.append(time)
                values.append(value)
            end_span = 1 + round(dist_rep_end.rvs())
            rep_end = time + end_span
            spans.append(end_span + 1)
            r_lens[-1] += 1
            stat2.end_rep(rep_end)
            
        print("=====Checking Test Setup Data=====")
        self.assertListEqual(stat2.rep_lengths.tolist(), r_lens)
        self.assertListEqual(times, stat2.times.tolist())
        self.assertListEqual(values, stat2.values.tolist())
        print("Test Values: {}".format(stat2.values))
        print("Replication Lengths: {}".format(r_lens))
        print("Statistic Index: {}".format(stat2._index))
        print()
        print("Test Times: {}".format(stat2.times))        
        print("Time Spans: {}".format(stat2._spans))
        self.assertListEqual(stat2._spans, spans)
#         
#         print("mean: {}".format(stat2.mean))
#         
# #         sum = 0
# #         for idx in range(len(times)):
# #             sum += times[idx] * spans[idx]
# #         time_mean = sum
# #         self.assertEqual(stat2.mean, stats.average(self.times, ))
#         
        

