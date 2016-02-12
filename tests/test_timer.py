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

import despy.dp as dp
import despy.stats.random as drand
import scipy.stats as stats


class TimerCallback():
    def call(self):
        pass
    
def timerCB_function(self):
    pass

class testTimer(unittest.TestCase):
    def test_timer(self):
        #Test a basic timer
        print()
        print("=====Testing RandomTimer with immediate = False=======")
        dp.Session.new()
        sim = dp.Simulation()            
        model1 = dp.model.Component("Timer_Test_Model_A")
        sim.model = model1   

        sim.config.seed = 731                  
        dist1 = stats.poisson(10)
        cb_class = TimerCallback()
        model1.add_component(dp.model.RandomTimer("timer",
                                                  dist1,
                                                  cb_class.call))
        self.assertEqual(len(model1.components), 1)
        
        results = sim.irunf(100)
         
        trace1 = results.trace
        self.assertEqual(trace1[0]['time'], 7)
        self.assertEqual(trace1[1]['time'], 15)
        self.assertEqual(trace1[2]['time'], 23)
         
        #Test timer with immediate = True
        print()
        print("=====Testing RandomTimer with immediate = True======")
        model2 = dp.model.Component("Timer_Test_Model_B")
        dist2 = stats.poisson(150)
        model2.add_component(
                   dp.model.RandomTimer("Timer", dist2, timerCB_function))
        sim2 = dp.Simulation(model2)
        sim2.config.seed = 704
        results = sim2.irunf(1000)
        trace2 = results.trace
        self.assertEqual(trace2[0]['time'], 142)
        self.assertEqual(trace2[1]['time'], 285)
        self.assertEqual(len(trace2), 3)
         
        #Test timer with Priority.LATE
        print()
        print("=====Testing Priority Attribute =======================")
        session = dp.Session.new()
        model3 = dp.model.Component("Timer_Test_Model_C")
 
        dist3 = drand.get_empirical_pmf([5, 10], [0.3, 0.7])
        model3.add_component(
                   dp.model.RandomTimer("timer", dist3, timerCB_function,
                                priority = dp.LATE))
        session.sim = sim3 = dp.Simulation(model3)
        session.config.seed = 731        
        results = sim3.irunf(100)
        trace3 = results.trace
        self.assertEqual(trace3[0]['priority'], 1)
        self.assertEqual(trace3[1]['priority'], 1)
        self.assertEqual(trace3[2]['interval'], 10)
        self.assertEqual(trace3[4]['interval'], 10)
        self.assertEqual(trace3[10]['interval'], 10)
        
if __name__ == '__main__':
    unittest.main()
        
    