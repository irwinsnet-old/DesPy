#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest

import despy.core as dp
import scipy.stats as stats

Simulation = dp.Simulation
FelItem = dp.FelItem
Model = dp.Model
Event = dp.Event
Process = dp.Process

class testDespyb(unittest.TestCase):
       
    ### Simulation Class Tests
    def test_now(self):
        # Verify that Simulation.now is set to 0 by default.
        exp1 = Simulation()
        self.assertEqual(exp1.now, 0)
        self.assertTrue(exp1.console_output)
        
        # Test console_output property.
        exp1.console_output = False
        self.assertFalse(exp1.console_output)
        exp1.console_output = True
        self.assertTrue(exp1.console_output)
        
        # Verify that Simulation.now can be set by the class constructor.
        exp2 = Simulation(42)
        self.assertEqual(exp2.now, 42)
        
        # Verify that a name can be assigned to the simulation.
        exp2.name = "Simulation Name!"
        self.assertEqual(exp2.name, "Simulation Name!")
        
    ### Model Class Tests
    def test_name(self):
        #Create model with default simulation.
        testModel = Model("Test Model")
        self.assertEqual(testModel.name, "Test Model")
        self.assertEqual(testModel.sim.name, "Test Model:Default Simulation")
        self.assertEqual(len(testModel.sim.models), 1)
        self.assertEqual(testModel.sim.models[0].name, "Test Model")
        
        #Replace simulation.
        exp = Simulation()
        exp.name = "New Simulation"
        self.assertIsInstance(testModel.sim, Simulation)
        self.assertIsNot(testModel.sim, exp)
        testModel.sim = exp
        self.assertIs(testModel.sim, exp)
        
        # Test description.
        modelDescription = \
        """ This is a test model. It does not have any components.
        It does not simulate any actual system."""
        testModel.description = modelDescription
        self.assertEqual(testModel.description, modelDescription)

    ###Event Scheduling Tests
    def test_peek(self):
        model = Model("Test Model #1")
        
        self.assertEqual(model.sim.peek(), float('Infinity'))
        
        model.schedule(Event(model, "Event #1"),
                       20,
                       dp.PRIORITY_EARLY)
        self.assertEqual(model.sim.peek(), 20)
        
        model.schedule(Event(model, "Event #2"), 5)
        self.assertEqual(model.sim.peek(), 5)
        
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
        felItem = model.sim.step()
        self.assertEqual(felItem.event_fld.name, "Early Event")
        felItem = model.sim.step()
        self.assertEqual(felItem.event_fld.name, "Standard Event")
        felItem = model.sim.step()
        self.assertEqual(felItem.event_fld.name, "Late Event")
        exp = model.sim
        self.assertEqual(exp.now, 5)

    def test_run(self):
        model = Model("RunTest Model")
        model.schedule(Event(model, "First Event"), 0)
        model.schedule(Event(model, "Second Event"), 4)
        model.schedule(Event(model, "Third Event"), 8)
        model.sim.run()
        
        self.assertEqual(len(model.components), 3)
        component_keys = list(model.components.keys())
        model.delete_component(component_keys[0])
        self.assertEqual(len(model.components), 2)
        model.delete_component(component_keys[1])
        self.assertEqual(len(model.components), 1)
        
        self.assertEqual(model.sim.out.trace.length(), 3)
        evtTrace = model.sim.out.trace
        self.assertEqual(evtTrace.get(0).name_fld, "First Event")
        self.assertEqual(evtTrace.get(1).name_fld, "Second Event")
        self.assertEqual(evtTrace.get(1).time_fld, 4)
        self.assertEqual(evtTrace.get(2).name_fld, "Third Event")
        self.assertEqual(evtTrace.get(2).time_fld, 8)

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
        model.sim.run()
        
        evtTrace = model.sim.out.trace
        self.assertEqual(evtTrace.length(), 2)
        self.assertEqual(evtTrace.get(0).name_fld, "First Event")
        self.assertEqual(evtTrace.get(0).time_fld, 5)
        self.assertEqual(evtTrace.get(1).name_fld, "Callback Event")
        self.assertEqual(evtTrace.get(1).time_fld, 15)
        
        #Test reset method and until parameter
        model.sim.reset()
        model.sim.run(10)
        evtTrace = model.sim.out.trace
        self.assertEqual(evtTrace.length(), 1)
        
        #Verify that simulation can be restarted from current point.
        model.sim.run()
        self.assertEqual(evtTrace.length(), 2)
        
    def test_process(self):
        model = Model("Process Model")
        model.sim.seed = 42
        
        def generator(self):
            while True:
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Repeated Event", delay)
        
        process = Process(model, "Test Process", generator)
        self.assertEqual(process.id,  "<class 'despy.core.process.Process'>#1")
        self.assertEqual(len(model.components), 1)
        process.start()
        model.sim.run(20)
        
    def test_simultaneous_events(self):
        #Test simultaneous, different events.
        model = Model("Simultaneous Events Model")
        model.schedule(Event(model, "Event #1"), 3)
        model.schedule(Event(model, "Event #2"), 3)
        self.assertEqual(len(model.components), 2)
        model.sim.run()
        self.assertEqual(model.sim.out.trace.length(), 2)
        
        #Test simultaneous, identical events.
        model2 = Model("Simultaneous Identical Events Model")
        event = Event(model2, "The Event")
        model2.schedule(event, 1)
        model2.schedule(event, 1)
        model2.sim.run()
        self.assertEqual(model2.sim.out.trace.length(), 2)

if __name__ == '__main__':
    unittest.main()

