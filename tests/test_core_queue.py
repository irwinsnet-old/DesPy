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
        print("=====Negative Time Test=====")
        model = dp.Component("Negative Time Model")
        sim = dp.Simulation(model = model)
        sim.schedule(dp.Event("Positive Time"),
                       priority = dp.Priority.LATE)        
        model.sim.schedule(dp.Event("Negative Time"),
                       priority = dp.Priority.EARLY)
        self.assertEqual(sim.peek(False), -0.1)

        sim.run()
        
    def test_entity_counter(self):
        print()
        print("=====Entity Counter Test=====")
        dp.Entity.set_counter()
        ent1 = dp.Entity("Entity #1")
        self.assertEqual(ent1.number, 1)
        ent2 = dp.Entity("Entity #2")
        self.assertEqual(ent2.number, 2)

    def test_queue(self):
        print()
        print("=====Test Queue=====")
        model = dp.Component("Q-test")
        qu = dp.Queue("TestQueue")
        model.add_component("q", qu)
        _ = dp.Simulation(model = model)
        self.assertEqual(qu.name, "TestQueue")
        customers = []
        dp.Entity.set_counter()
        for i in range(5):
            customers.append(dp.Entity("Customer #{0}".format(i)))
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

    def test_queue_in_simulation(self):
        print()
        print("=====Test Queue In Simulation======")
        Customer.set_counter()
        model = QuModel("Queue Model")
        self.assertIsInstance(dp.Session().model, QuModel)
        sim = dp.Simulation(model = model)
        sim.gen.folder_basename = \
                "C:/Projects/despy_output/queue_sim"
        
        sim.run(100)
        self.assertGreater(len(model.components), 0)
        
class QuModel(dp.Component):
    def __init__(self, name):
        super().__init__(name, "Queue Model Test", is_model = True)
        self.add_component("c_qu", dp.Queue("Customer Queue"))
        self.add_component("customer_process", CustArrProcess())
        self.add_component("service_process", CustServiceProcess())
        
    def initialize(self):
        self.customer_process.start(0, dp.Priority.EARLY)
        self.service_process.start()

class Customer(dp.Entity):
    def __init__(self):
        super().__init__("Customer")
        
class CustArrProcess(dp.Process):
    def __init__(self):
        super().__init__("Customer Generator", self.generator)

    def generator(self):
        first_customer = Customer()
        self.parent.c_qu.add(first_customer)                
        yield self.schedule_timeout(\
                "Customer #{0} arrives.".format(first_customer.number))
        while True:
            delay = round(stats.expon.rvs(scale = 3))
            customer = Customer()                    
            yield self.schedule_timeout(\
                    "Customer #{0} arrives.".format(customer.number),
                    delay)
            self.parent.c_qu.add(customer)
            self.parent.service_process.wake()

class CustServiceProcess(dp.Process):
    def __init__(self):
        super().__init__("Customer Server", self.generator)
        
    def generator(self):
        while True:
            if self.parent.c_qu.length > 0:
                customer = self.parent.c_qu.remove()
                delay = round(stats.expon.rvs(scale = 4))
                yield self.schedule_timeout("Finished serving customer"
                        " #{0}, Service time: {1}"
                        .format(customer.number, delay), delay)
            else:
                yield self.sleep()

if __name__ == '__main__':
    unittest.main()

