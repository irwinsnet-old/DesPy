#!/usr/bin/env python3

import unittest

import despy.core as dp
import scipy.stats as stats
from collections import OrderedDict

class testResource(unittest.TestCase):
    def get_rnd_exp(self):
        return round(stats.expon.rvs(scale = 4))
    
    def test_resource_init(self):
        print()
        print("TEST RESOURCE INIT OUTPUT")
        model = dp.Model("Resource Test #1")
        server = dp.Resource(model, "Server", 2)
        server.activity_time = self.get_rnd_exp
        self.assertEqual(server.name, "Server")
        ents = []
        for i in range(3):
            ents.append(dp.Entity(model, "Entity #{0}".format(i)))

        #   Verify resource has two positions with keys 1 and 2, and that both
        # are empty (i.e., contain None object).
        self.assertEqual(len(server._positions), 2)
        self.assertEqual(server.capacity, 2)
        self.assertTrue(1 in server._positions)
        self.assertTrue(2 in server._positions)
        self.assertFalse(0 in server._positions)
        self.assertFalse(3 in server._positions)
         
        self.assertTrue(server[1].user is None)
        self.assertTrue(server[2].user is None)
        self.assertEqual(server[1].name, "Server #1")
        self.assertEqual(server[2].name, "Server #2")
         
        #   Check that entities were created.
        self.assertEqual(ents[0].name, "Entity #0")
        self.assertEqual(ents[1].name, "Entity #1")
         
        #   Check get_empty_position()
        position = server.get_empty_position()
        self.assertEqual(position, 1)
         
        #   Check request(user)
        position = server.request(ents[0])
        self.assertEqual(position, 1)
        self.assertTrue(server[position].user is not None)
        self.assertEqual(server[position].user.name, "Entity #0")
        self.assertTrue(server[2].user is None)
         
    class ResModel(dp.Model):
        class Customer(dp.Entity):
            def __init__(self, model):
                super().__init__(model, "Customer")
             
        def initialize(self):
            self.customer_process.start(0, dp.PRIORITY_EARLY)
            super().initialize()
             
        class CustServiceResource(dp.Resource):
            def __init__(self, model, capacity):
                super().__init__(model, "Server", capacity)
                self.queue = dp.Queue(model, "Server Queue")
             
            def get_activity_time(self):
                return round(stats.expon.rvs(scale = 4))
         
        class CustArrProcess(dp.Process):
            def __init__(self, model, server_resource):
                super().__init__(model, "Customer Generator", self.generator)
                self.server_resource = server_resource
             
            def generator(self):
                customer = self.model.Customer(self.model)
                args1 = OrderedDict()
                args1["Customer"] = "Customer #{0}".format(customer.number)
                yield self.schedule_timeout("Customer Arrives", 0,
                                            trace_fields = args1)

                while True:
                    self.server_resource.request(customer)
                    delay = stats.expon.rvs(scale = 3)
                    customer = self.model.Customer(self.model)
                    args2 = OrderedDict()
                    args2["Customer"] = "Customer #{0}".format(customer.number)
                    args2["Interarrival_Time"] = delay
                    yield self.schedule_timeout("Customer Arrives", delay,
                            trace_fields = args2)
                     
        def __init__(self, name):
            super().__init__(name)
            self.server_resource = self.CustServiceResource(self, 2)
            self.customer_process = self.CustArrProcess(self,
                                                        self.server_resource)
     
    def test_resource_in_simulation(self):
        print()
        print("TEST RESOURCE IN EXPERIMENT OUTPUT")
        self.ResModel.Customer.set_counter()
        model = self.ResModel("Resource Model")
        simulation = model.sim
        simulation.output_folder = "C:/Projects/despy_output/resource_sim"
        simulation.run(100)
        
if __name__ == '__main__':
    unittest.main()
    