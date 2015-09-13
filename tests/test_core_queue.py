#!/usr/bin/env python3
"""
test_core_queue.py tests queue performance.
===============================================================================
"""

import unittest

import scipy.stats as stats

import despy.core as dp

class testQueue(unittest.TestCase):
    def test_negative_time(self):
        #If an event is scheduled at time 0 with Priority.EARLY, then the raw
        #  FEL Time will be negative. Test verifies that negative time still
        #  works.
        print()
        model = dp.Model("Negative Time Model")
        sim = dp.Simulation(model = model)
        sim.schedule(dp.Event(model, "Positive Time"),
                       priority = dp.Priority.LATE)        
        model.sim.schedule(dp.Event(model, "Negative Time"),
                       priority = dp.Priority.EARLY)
        self.assertEqual(sim.peek(False), -0.1)

        sim.run()
        
    def test_entity_counter(self):
        print()
        model = dp.Model("Entity Counter Test")
        dp.Entity.set_counter()
        ent1 = dp.Entity(model, "Entity #1")
        self.assertEqual(ent1.number, 1)
        ent2 = dp.Entity(model, "Entity #2")
        self.assertEqual(ent2.number, 2)

    def test_queue(self):
        print()
        model = dp.Model("Q-test")
        _ = dp.Simulation(model = model)
        qu = dp.Queue(model, "TestQueue")
        self.assertEqual(qu.name, "TestQueue")
        customers = []
        dp.Entity.set_counter()
        for i in range(5):
            customers.append(dp.Entity(model, "Customer #{0}".format(i)))
        self.assertEqual(len(customers), 5)
        
        qu.add(customers[0])
        self.assertEqual(qu.length, 1)
        qu.add(customers[1])
        qu.add(customers[2])
        self.assertEqual(qu.length, 3)
        
        entity = qu.remove()
        self.assertEqual(entity.name, "Customer #0")
        self.assertEqual(qu.length, 2)
        entity = qu.remove()
        self.assertEqual(entity.name, "Customer #1")
        self.assertEqual(qu.length, 1)
        entity = qu.remove()
        self.assertEqual(entity.name, "Customer #2")
        self.assertEqual(qu.length, 0)
        
    class QuModel(dp.Model):

        class Customer(dp.Entity):
            def __init__(self, model):
                super().__init__(model, "Customer")
                
        def initialize(self):
            self.customer_process.start(0, dp.Priority.EARLY)
            self.service_process.start()
            
        class CustArrProcess(dp.Process):
            def __init__(self, model):
                super().__init__(model, "Customer Generator", self.generator)

            def generator(self):
                first_customer = self.mod.Customer(self.mod)
                self.mod.c_qu.add(first_customer)                
                yield self.schedule_timeout(\
                        "Customer #{0} arrives.".format(first_customer.number))
                while True:
                    delay = round(stats.expon.rvs(scale = 3))
                    customer = self.mod.Customer(self.mod)                    
                    yield self.schedule_timeout(\
                            "Customer #{0} arrives.".format(customer.number),
                            delay)
                    self.mod.c_qu.add(customer)
                    self.mod.service_process.wake()
        
        class CustServiceProcess(dp.Process):
            def __init__(self, model):
                super().__init__(model, "Customer Server", self.generator)
                
            def generator(self):
                while True:
                    if self.mod.c_qu.length > 0:
                        customer = self.mod.c_qu.remove()
                        delay = round(stats.expon.rvs(scale = 4))
                        yield self.schedule_timeout(\
                                "Finished serving customer #{0}, Service time: {1}".format(customer.number, delay),
                                delay)
                    else:
                        yield self.sleep()
        
        def __init__(self, name):
            super().__init__(name)
            self["c_qu"] = dp.Queue(self, "Customer Queue")
            self["customer_process"] = self.CustArrProcess(self)
            self["service_process"] = self.CustServiceProcess(self)

    def test_queue_in_simulation(self):
        print()
        self.QuModel.Customer.set_counter()
        model = self.QuModel("Queue Model")
        sim = dp.Simulation(model = self.QuModel)
        sim.gen.folder_basename = \
                "C:/Projects/despy_output/queue_sim"
        
        sim.run(100)
        self.assertGreater(len(model.components), 0)

if __name__ == '__main__':
    unittest.main()

