#!/usr/bin/env python3

import unittest
from collections import OrderedDict

import scipy.stats as stats

import despy.dp as dp

class testResource(unittest.TestCase):
    
    def test_resource_init(self):
        print()
        print("TEST RESOURCE INIT OUTPUT")
        model = dp.model.Component("Resource_Test_1")

        server = dp.model.Resource("server", 2, stats.expon(scale=4))
        model.add_component(server)
        session = dp.Session()
        session.model = model
        self.assertEqual(len(model.components), 1)
        self.assertEqual(server.name, "server")
        ents = []
        for _ in range(3):
            ents.append(dp.model.Entity("Entity"))

        #   Verify resource has two positions with keys 1 and 2, and that both
        # are empty (i.e., contain None object).
        self.assertEqual(len(server.stations), 2)
        self.assertEqual(server.capacity, 2)
         
        self.assertTrue(server[0].entity is None)
        self.assertTrue(server[1].entity is None)
        self.assertEqual(server[0].start_time, None)
        self.assertEqual(server[1].start_time, None)
         
        #   Check that entities were created.
        self.assertEqual(ents[0].name, "Entity")
        self.assertEqual(ents[1].name, "Entity")
         
        #   Check get_empty_position()
        position = server.get_available_station()
        self.assertEqual(position, 0)
         
        #   Check request(user)
        position = server.request(ents[0])
        self.assertEqual(position, 0)
        self.assertTrue(server[position].entity is not None)
        self.assertTrue(server[position].start_time is not None)
        self.assertTrue(server[1].entity is None)
         
    class ResModel(dp.model.Component):
        class Customer(dp.model.Entity):
            def __init__(self):
                super().__init__("Customer")
             
        def setup(self):
            self.customer_process.start(0, dp.EARLY)
             
        class CustServiceResource(dp.model.ResourceQueue):
            def __init__(self, capacity):             
                super().__init__("server_resource")
                self.assign_resource(dp.model.Resource("Server",
                                              capacity,
                                              stats.expon(scale=4)))                
         
        class CustArrProcess(dp.model.Process):
            def __init__(self, server_resource):
                super().__init__("customer_process", self.generator)
                self.server_resource = server_resource
             
            def generator(self):
                customer = self.owner.Customer()
                args1 = OrderedDict()
                args1["Interarrival_Time"] = None
                args1["Customer"] = customer
                yield self.schedule_timeout("Customer_Arrives", 0,
                                            trace_fields = args1)

                while True:
                    self.server_resource.request(customer)
                    delay = round(stats.expon.rvs(scale = 3))
                    customer = self.owner.Customer()
                    args2 = OrderedDict()
                    args2["Interarrival_Time"] = delay                    
                    args2["Customer"] = customer
                    yield self.schedule_timeout("Customer_Arrives",
                                                delay,
                                                trace_fields = args2)
                     
        def __init__(self, name):
            super().__init__(name)
            self.add_component(self.CustServiceResource(2))
            self.add_component(self.CustArrProcess(self.server_resource))
     
    def test_resource_in_simulation(self):
        print()
        print("TEST RESOURCE IN SIMULATION OUTPUT")
        self.ResModel.Customer.set_counter()
        model = self.ResModel("Resource_Model")
        session = dp.Session()
        session.model = model
        session.sim = simulation = dp.Simulation()
        session.config.folder_basename = \
                        "C:/Projects/despy_output/resource_sim"
        simulation.irunf(100).write_files()
        
if __name__ == '__main__':
    unittest.main()
    