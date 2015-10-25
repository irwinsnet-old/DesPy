'''
Created on Oct 25, 2015

@author: stacy.irwin
'''
import unittest

import despy.core as dp
import despy.stats.random as dsr

class RepModel(dp.Component):
    def __init__(self):
        super().__init__("Multiple Rep Test")
        
        # Customer Arrival Timer
        arrival_dist = dsr.get_empirical_pmf([1, 2, 3, 4],
                                    [0.25, 0.4, 0.2, 0.15],
                                    "Customer Arrival Distribution")

        self.add_component("arr_timer", 
                    dp.RandomTimer("Arrival Timer",
                    arrival_dist,
                    RepModel.CustomerArrivalCallback(rep_model = self),
                    True,
                    -1))
        
        # Servers and Resource Queue
        abel_dist = dsr.get_empirical_pmf([2, 3, 4, 5],
                                          [0.3, 0.28, 0.25, 0.17],
                                          "Abel Service Distribution")
        baker_dist = dsr.get_empirical_pmf([3, 4, 5, 6],
                                           [0.35 ,0.25, 0.2, 0.2],
                                           "Baker Service Distribution")
        
        self.add_component("res_q",
                           dp.ResourceQueue("Customer Servers"))
        self.res_q.assign_resource(dp.Resource("Abel", 1, abel_dist))
        self.res_q.assign_resource(dp.Resource("Baker", 1, baker_dist))
                           
    class CustomerArrivalCallback(dp.AbstractCallback):
        def call(self):
            self.args["rep_model"].res_q.request(dp.Entity("Customer"))


class Test(unittest.TestCase):

    def test_reps(self):
        dp.Session().model = RepModel()
        sim = dp.Simulation()
        sim.gen.folder_basename = "C:/Projects/despy_output/mult_reps"
        sim.run(100)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_reps']
    unittest.main()