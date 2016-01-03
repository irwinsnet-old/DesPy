#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""Despy model for a single channel queue, example 2.2.

From 'Discrete Event System Simulation, 4th ed.; Banks, Carson, Nelson,
and Nicole
"""

import despy as dp
import scipy.stats as stats


class SingleChannelQueue(dp.model.Component):
    def __init__(self):
        super().__init__("single_q_model")
        
        # Customer arrival distribution
        # Inter-arrival times follow uniform discrete distribution
        #    varying from 1 to 8 minutes.
        arrival_dist = stats.randint(1, 9)
        self.add_component(dp.model.RandomTimer("arrival_timer",
                    arrival_dist,
                    SingleChannelQueue.CustomerArrivalCB(mod = self),
                    True,
                    dp.fel.Priority.EARLY))        
        
        
        # Service time distribution
        # Empirical distribution varying from 1 to 6 minutes.
        service_dist = dp.stats_random.get_empirical_pmf([1, 2, 3, 4, 5, 6],
                                          [0.1, 0.2, 0.3, 0.25, .1, .05],
                                          "service_time_dist")       
        self.add_component(dp.model.ResourceQueue("server_q"))
        self.server_q.assign_resource(dp.model.Resource("server", 1, service_dist))
        
        dp.model.Entity.set_counter()
                           
    class CustomerArrivalCB(dp.fel.AbstractCallback):
        def call(self, **args):
            new_customer = dp.model.Entity("Customer")
            timer_evt = args["timer_evt"]
            timer_evt.trace_fields["Customer"] = str(new_customer)
          
            self.args["mod"].server_q.request(new_customer)