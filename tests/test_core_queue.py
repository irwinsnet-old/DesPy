#!/usr/bin/env python3
"""
test_core_queue.py tests queue performance.
===============================================================================
"""

import unittest

import scipy.stats as stats

import despy as dp

class testQueue(unittest.TestCase):
    def test_negative_time(self):
        #If an event is scheduled at time 0 with Priority.EARLY, then the raw
        #  FEL Time will be negative. Test verifies that negative time still
        #  works.
        print()
        print("=====Negative Time Test=====")
        session = dp.Session()
        session.sim = sim = dp.Simulation()         
        session.model = model = dp.model.Component("Negative Time Model")
        sim.schedule(dp.Event("Positive Time"),
                       priority = dp.Priority.LATE)        
        model.sim.schedule(dp.Event("Negative Time"),
                       priority = dp.Priority.EARLY)
        self.assertEqual(sim.peek(False), -0.1)

        sim.irun()
        
    def test_entity_counter(self):
        print()
        print("=====Entity Counter Test=====")
        dp.model.Entity.set_counter()
        ent1 = dp.model.Entity("Entity #1")
        self.assertEqual(ent1.number, 1)
        ent2 = dp.model.Entity("Entity #2")
        self.assertEqual(ent2.number, 2)
 
    def test_queue(self):
        print()
        print("=====Test Queue=====")
        model = dp.model.Component("Q-test")
        qu = dp.model.Queue("TestQueue")
        model.add_component("q", qu)
        session = dp.Session()
        session.model = model
        session.sim = dp.Simulation()
        self.assertEqual(qu.name, "TestQueue")
        customers = []
        dp.model.Entity.set_counter()
        for i in range(5):
            customers.append(dp.model.Entity("Customer #{0}".format(i)))
        self.assertEqual(len(customers), 5)
         
        qu.dp_setup()
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
 
    def test_queue_in_simulation(self):
        print()
        print("=====Test Queue In Simulation======")
        Customer.set_counter()
        model = QuModel("Queue Model")
        session = dp.Session()
        session.model = model
        self.assertIsInstance(dp.Session().model, QuModel)
        session.sim = sim = dp.Simulation()
        session.config.folder_basename = \
                "C:/Projects/despy_output/queue_sim"
         
        sim.irunf(100)
        self.assertGreater(len(model.components), 0)
         
class QuModel(dp.model.Component):
    def __init__(self, name):
        super().__init__(name, "Queue Model Test")
        self.add_component("c_qu", dp.model.Queue("Customer Queue"))
        self.add_component("customer_process", CustArrProcess())
        self.add_component("service_process", CustServiceProcess())
         
    def initialize(self):
        self.customer_process.start(0, dp.Priority.EARLY)
        self.service_process.start()
 
class Customer(dp.model.Entity):
    def __init__(self):
        super().__init__("Customer")
         
class CustArrProcess(dp.model.Process):
    def __init__(self):
        super().__init__("Customer Generator", self.generator)
 
    def generator(self):
        first_customer = Customer()
        self.model.c_qu.add(first_customer)                
        yield self.schedule_timeout(\
                "Customer #{0} arrives.".format(first_customer.number))
        while True:
            delay = round(stats.expon.rvs(scale = 3))
            customer = Customer()                    
            yield self.schedule_timeout(\
                    "Customer #{0} arrives.".format(customer.number),
                    delay)
            self.model.c_qu.add(customer)
            self.model.service_process.wake()
 
class CustServiceProcess(dp.model.Process):
    def __init__(self):
        super().__init__("Customer Server", self.generator)
         
    def generator(self):
        while True:
            if self.model.c_qu.length > 0:
                customer = self.model.c_qu.remove()
                delay = round(stats.expon.rvs(scale = 4))
                yield self.schedule_timeout("Finished serving customer"
                        " #{0}, Service time: {1}"
                        .format(customer.number, delay), delay)
            else:
                yield self.sleep()

if __name__ == '__main__':
    unittest.main()

