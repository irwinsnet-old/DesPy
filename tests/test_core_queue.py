#!/usr/bin/env python3
"""
test_core_queue.py tests queue performance.
===============================================================================
"""

import unittest

import despy.core as dp
import scipy.stats as stats

Experiment = dp.Experiment
FelItem = dp.FelItem
Event = dp.Event
Process = dp.Process

class testQueue(unittest.TestCase):
    
    def test_queue(self):
        model = dp.Model("Q-test")
        qu = dp.Queue(model, "TestQueue")
        self.assertEqual(qu.name, "TestQueue")
        customers = []
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
        
    def test_queue_in_experiment(self):
        class QuModel(dp.Model):
            def __init__(self, name):
                super().__init__(name)
                self.qu = dp.Queue(self, "Customer Queue")
                
        model = QuModel("Queue Model")
        experiment = model.experiment
        
        def customer_generator(self):
            i = 0
            while True:
                customer = dp.Entity(self.model, "Customer #{0}".format(i))
                self.qu.add(customer)
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Customer #{0} arrives.".format(i),
                                            delay)

        
if __name__ == '__main__':
    unittest.main()

