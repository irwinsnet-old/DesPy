#!/usr/bin/env python3
"""
test_core_queue.py tests queue performance.
===============================================================================
"""

import unittest
import itertools

import despy.core as dp
import scipy.stats as stats

Experiment = dp.Experiment
FelItem = dp.FelItem
Event = dp.Event
Process = dp.Process

class testQueue(unittest.TestCase):
    def test_negative_time(self):
        #If an event is scheduled at time 0 with PRIORITY_EARLY, then the raw
        #  FEL Time will be negative. Test verifies that negative time still
        #  works.
        print()
        model = dp.Model("Negative Time Model")
        model.schedule(dp.Event(model, "Positive Time"),
                       priority = dp.PRIORITY_LATE)        
        model.schedule(dp.Event(model, "Negative Time"),
                       priority = dp.PRIORITY_EARLY)
        self.assertEqual(model.experiment.peek(False), -0.1)

        model.experiment.run()
        
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
            self.customer_process.start(0, dp.PRIORITY_EARLY)
            self.service_process.start()
            
        class CustArrProcess(dp.Process):
            def __init__(self, model):
                super().__init__(model, "Customer Generator", self.generator)

            def generator(self):
                first_customer = self.model.Customer(self.model)
                yield self.schedule_timeout(\
                        "Customer #{0} arrives.".format(first_customer.number))
                while True:
                    customer = self.model.Customer(self.model)
                    self.model.c_qu.add(customer)
                    delay = round(stats.expon.rvs(scale = 3))
                    yield self.schedule_timeout(\
                            "Customer #{0} arrives.".format(customer.number),
                            delay)
                    self.model.service_process.wake()
        
        class CustServiceProcess(dp.Process):
            def __init__(self, model):
                super().__init__(model, "Customer Server", self.generator)
                
            def generator(self):
                while True:
                    if self.model.c_qu.length > 0:
                        customer = self.model.c_qu.remove()
                        delay = round(stats.expon.rvs(scale = 4))
                        yield self.schedule_timeout(\
                                "Finished serving customer #{0}, Service time: {1}".format(customer.number, delay),
                                delay)
                    else:
                        yield self.sleep()
        
        def __init__(self, name):
            super().__init__(name)
            self.c_qu = dp.Queue(self, "Customer Queue")
            self.customer_process = self.CustArrProcess(self)
            self.service_process = self.CustServiceProcess(self)

    def test_queue_in_experiment(self):
        print()
        self.QuModel.Customer.set_counter()
        model = self.QuModel("Queue Model")
        experiment = model.experiment
        experiment.trace_file = "trace/test_queue_in_experiment.csv"
        
        experiment.run(100)

        
if __name__ == '__main__':
    unittest.main()

