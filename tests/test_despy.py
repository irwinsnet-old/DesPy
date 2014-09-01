#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest

import despy.core as dp
import scipy.stats as stats

Experiment = dp.Experiment
FelItem = dp.FelItem
Model = dp.Model
Event = dp.Event
Process = dp.Process

class testDespyb(unittest.TestCase):
       
    ### Experiment Class Tests
    def test_now(self):
        # Verify that Experiment.now is set to 0 by default.
        exp1 = Experiment()
        self.assertEqual(exp1.now, 0)
        self.assertTrue(exp1.console_output)
        
        # Test console_output property.
        exp1.console_output = False
        self.assertFalse(exp1.console_output)
        exp1.console_output = True
        self.assertTrue(exp1.console_output)
        
        # Verify that Experiment.now can be set by the class constructor.
        exp2 = Experiment(42)
        self.assertEqual(exp2.now, 42)
        
        # Verify that a name can be assigned to the experiment.
        exp2.name = "Experiment Name!"
        self.assertEqual(exp2.name, "Experiment Name!")
        
    ### Model Class Tests
    def test_name(self):
        #Create model with default experiment.
        testModel = Model("Test Model")
        self.assertEqual(testModel.name, "Test Model")
        self.assertEqual(testModel.experiment.name, "Default Experiment")
        self.assertEqual(len(testModel.experiment.models), 1)
        self.assertEqual(testModel.experiment.models[0].name, "Test Model")
        
        #Replace experiment.
        exp = Experiment()
        exp.name = "New Experiment"
        self.assertIsInstance(testModel.experiment, Experiment)
        self.assertIsNot(testModel.experiment, exp)
        testModel.experiment = exp
        self.assertIs(testModel.experiment, exp)
        
        # Test description.
        modelDescription = \
        """ This is a test model. It does not have any components.
        It does not simulate any actual system."""
        testModel.description = modelDescription
        self.assertEqual(testModel.description, modelDescription)

    ###Event Scheduling Tests
    def test_peek(self):
        model = Model("Test Model #1")
        
        self.assertEqual(model.experiment.peek(), float('Infinity'))
        
        model.schedule(Event(model, "Event #1",
                dp.PRIORITY_EARLY), 20)
        self.assertEqual(model.experiment.peek(), 20)
        
        model.schedule(Event(model, "Event #2"), 5)
        self.assertEqual(model.experiment.peek(), 5)
        
    def test_step(self):
        #Create model and events.
        model = Model("Test Model #2")
        ev_early = Event(model, "Early Event")
        ev_standard = Event(model, "Standard Event")
        ev_late = Event(model, "Late Event")
        
        #Schedule Events
        model.schedule(ev_late, 5, dp.PRIORITY_LATE)
        model.schedule(ev_early, 5, dp.PRIORITY_EARLY)
        model.schedule(ev_standard, 5, dp.PRIORITY_STANDARD)
        
        #Verify events run in correct order.
        print()
        felItem = model.experiment.step()
        self.assertEqual(felItem.fel_event.name, "Early Event")
        felItem = model.experiment.step()
        self.assertEqual(felItem.fel_event.name, "Standard Event")
        felItem = model.experiment.step()
        self.assertEqual(felItem.fel_event.name, "Late Event")
        exp = model.experiment
        self.assertEqual(exp.now, 5)

    def test_run(self):
        model = Model("RunTest Model")
        model.schedule(Event(model, "First Event"), 0)
        model.schedule(Event(model, "Second Event"), 4)
        model.schedule(Event(model, "Third Event"), 8)
        model.experiment.run()
        
        self.assertEqual(model.experiment.trace.length(), 3)
        evtTrace = model.experiment.trace
        self.assertEqual(evtTrace.get(0).evt_name, "First Event")
        self.assertEqual(evtTrace.get(1).evt_name, "Second Event")
        self.assertEqual(evtTrace.get(1).time, 4)
        self.assertEqual(evtTrace.get(2).evt_name, "Third Event")
        self.assertEqual(evtTrace.get(2).time, 8)

    def test_appendCallback(self):
        model = Model("AppendCallback Model")
        evt1 = Event(model, "First Event")
        
        def evt1_callback(self):
            evt2 = Event(self.model, "Callback Event")
            self.model.schedule(evt2, 10)        

        evt1.append_callback(evt1_callback)
        
        def initializeModel(self):
            self.schedule(evt1, 5)
        
        model.set_initialize_method(initializeModel)
        model.experiment.run()
        
        evtTrace = model.experiment.trace
        self.assertEqual(evtTrace.length(), 2)
        self.assertEqual(evtTrace.get(0).evt_name, "First Event")
        self.assertEqual(evtTrace.get(0).time, 5)
        self.assertEqual(evtTrace.get(1).evt_name, "Callback Event")
        self.assertEqual(evtTrace.get(1).time, 15)
        
        #Test reset method and until parameter
        model.experiment.reset()
        model.experiment.run(10)
        evtTrace = model.experiment.trace
        self.assertEqual(evtTrace.length(), 1)
        
        #Verify that simulation can be restarted from current point.
        model.experiment.run()
        self.assertEqual(evtTrace.length(), 2)
        
    def test_process(self):
        model = Model("Process Model")
        model.experiment.seed = 42
        
        def generator(self):
            while True:
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Repeated Event", delay)
        
        process = Process(model, "Test Process", generator)
        process.start()
        model.experiment.run(20)
        
    def test_simultaneous_events(self):
        model = Model("Simuleaneous Events Model")
        model.schedule(Event(model, "Event #1"), 3)
        model.schedule(Event(model, "Event #2"), 3)
        model.experiment.run()

if __name__ == '__main__':
    unittest.main()

