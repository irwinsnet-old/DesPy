#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""Despy model for the Abel-Baker problem, example 2.2.

From 'Discrete Event System Simulation, 4th ed.; Banks, Carson, Nelson,
and Nicole
"""

import despy as dp


class AbelBakerModel(dp.model.Component):
    def __init__(self):
        super().__init__("Abel Baker Model")
        assert(isinstance(self, dp.model.abstract.AbstractModel))
        
        # Customer Arrival Timer
        arrival_dist = dp.stats_random.get_empirical_pmf([1, 2, 3, 4],
                                    [0.25, 0.4, 0.2, 0.15],
                                    "Customer Arrival Distribution")

        self.add_component("arr_timer", 
                    dp.model.RandomTimer("Arrival Timer",
                    arrival_dist,
                    AbelBakerModel.CustomerArrivalCallback(rep_model = self),
                    True,
                    -1))
        
        # Servers and Resource Queue
        abel_dist = dp.stats_random.get_empirical_pmf([2, 3, 4, 5],
                                          [0.3, 0.28, 0.25, 0.17],
                                          "Abel Service Distribution")
        baker_dist = dp.stats_random.get_empirical_pmf([3, 4, 5, 6],
                                           [0.35 ,0.25, 0.2, 0.2],
                                           "Baker Service Distribution")
        
        self.add_component("res_q",
                           dp.model.ResourceQueue("Customer Servers"))
        self.res_q.assign_resource(dp.model.Resource("Abel", 1, abel_dist))
        self.res_q.assign_resource(dp.model.Resource("Baker", 1, baker_dist))
        
        dp.model.Entity.set_counter()
                           
    class CustomerArrivalCallback(dp.fel.AbstractCallback):
        def call(self, **args):
            new_customer = dp.model.Entity("Customer")
            timer_evt = args["timer_evt"]
            timer_evt.trace_fields["Customer"] = str(new_customer)
          
            self.args["rep_model"].res_q.request(new_customer)