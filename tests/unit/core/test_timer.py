#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
********************
unit/core/test_timer
********************
"""

import unittest

import despy.core as dp
import despy.stats.random as drand
import scipy.stats as stats


def timer_callback(evt):
    pass

class testTimer(unittest.TestCase):
    def test_timer(self):
        #Test a basic timer.
        print()
        print("=====Testing RandomTimer with immediate = False========")
        model1 = dp.Model("Timer Test Model-A")
        dist1 = stats.poisson(10)
        model1["timer"] = dp.RandomTimer(model1, "Timer-A", dist1, timer_callback)
        sim = dp.Simulation(model = model1)
        model1.sim.seed = 731
        self.assertEqual(len(model1.components), 1)
        sim.run(100)
        
        trace1 = model1.sim.gen.trace
        self.assertEqual(trace1[0]['time'], 7)
        self.assertEqual(trace1[1]['time'], 15)
        self.assertEqual(trace1[2]['time'], 23)
        
        #Test timer with immediate = True
        print()
        print("=====Testing RandomTimer with immediate = True=========")
        model2 = dp.Model("Timer Test Model-B")
        dist2 = stats.poisson(150)
        model2["Timer"] = dp.RandomTimer(model2, "Timer-B", dist2,
                                         timer_callback)
        sim = dp.Simulation(model = model2)
        sim.seed = 704
        sim.run(1000)
        trace2 = model2.sim.gen.trace
        self.assertEqual(trace2[0]['time'], 142)
        self.assertEqual(trace2[1]['time'], 285)
        self.assertEqual(len(trace2), 3)
        
        #Test timer with Priority.LATE
        print()
        print("=====Testing Priority Attribute =======================")
        model3 = dp.Model("Timer Test Model-C")

        dist3 = drand.get_empirical_pmf([5, 10], [0.3, 0.7])
        model3["timer"] = dp.RandomTimer(model3, "Timer-C", dist3,
                                timer_callback,
                                priority = dp.Priority.LATE)
        sim = dp.Simulation(model = model3)
        model3.sim.seed = 731        
        sim.run(100)
        trace3 = model3.sim.gen.trace
        self.assertEqual(trace3[0]['priority'], 1)
        self.assertEqual(trace3[1]['priority'], 1)
        self.assertEqual(trace3[2]['interval'], 5)
        self.assertEqual(trace3[4]['interval'], 5)
        self.assertEqual(trace3[10]['interval'], 5)
        
        
        
        
    