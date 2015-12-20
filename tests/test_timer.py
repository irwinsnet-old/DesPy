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


class TimerCallback(dp.AbstractCallback):
    def call(self, **args):
        pass

class testTimer(unittest.TestCase):
    def test_timer(self):
        #Test a basic timer
        print()
        print("=====Testing RandomTimer with immediate = False=======")
        model1 = dp.Component("Timer Test Model-A")
        session = dp.Session.new()
        session.model = model1   
        session.sim = sim = dp.Simulation()
        sim.seed = 731                  
        dist1 = stats.poisson(10)
        model1.add_component("timer",
                   dp.RandomTimer("TimerA", dist1, TimerCallback()))
        self.assertEqual(len(model1.components), 1)
        
        results = sim.irunf(100)
         
        trace1 = results.trace
        self.assertEqual(trace1[0]['time'], 7)
        self.assertEqual(trace1[1]['time'], 15)
        self.assertEqual(trace1[2]['time'], 23)
         
        #Test timer with immediate = True
        print()
        print("=====Testing RandomTimer with immediate = True======")
        model2 = dp.Component("Timer Test Model-B")
        dist2 = stats.poisson(150)
        model2.add_component("Timer",
                   dp.RandomTimer("Timer-B", dist2, TimerCallback()))
        session.model = model2
        session.sim = sim = dp.Simulation()
        sim.seed = 704
        results = sim.irunf(1000)
        trace2 = results.trace
        self.assertEqual(trace2[0]['time'], 142)
        self.assertEqual(trace2[1]['time'], 285)
        self.assertEqual(len(trace2), 3)
         
        #Test timer with Priority.LATE
        print()
        print("=====Testing Priority Attribute =======================")
        model3 = dp.Component("Timer Test Model-C")
 
        dist3 = drand.get_empirical_pmf([5, 10], [0.3, 0.7])
        model3.add_component("timer", 
                   dp.RandomTimer("Timer-C", dist3, TimerCallback(),
                                priority = dp.Priority.LATE))
        session.model = model3
        session.sim = sim = dp.Simulation()
        model3.sim.seed = 731        
        results = sim.irunf(100)
        trace3 = results.trace
        self.assertEqual(trace3[0]['priority'], 1)
        self.assertEqual(trace3[1]['priority'], 1)
        self.assertEqual(trace3[2]['interval'], 10)
        self.assertEqual(trace3[4]['interval'], 10)
        self.assertEqual(trace3[10]['interval'], 10)
        
if __name__ == '__main__':
    unittest.main()
        
    