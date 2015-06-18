#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest
import scipy.stats as stats
import despy.core as dp

class testDespyb(unittest.TestCase):
       
    ### Simulation Class Tests
    def test_now(self):
        # Verify that Simulation.now is set to 0 by default.
        exp1 = dp.Simulation()
        self.assertEqual(exp1.now, 0)
        self.assertTrue(exp1.gen.console_trace)
        
        # Test console_output property.
        exp1.gen.console_trace = False
        self.assertFalse(exp1.gen.console_trace)
        exp1.gen.console_trace = True
        self.assertTrue(exp1.gen.console_trace)
        
        # Verify that Simulation.now can be set by the class constructor.
        exp2 = dp.Simulation(42)
        self.assertEqual(exp2.now, 42)
        
        # Verify that a name can be assigned to the simulation.
        exp2.name = "Simulation Name!"
        self.assertEqual(exp2.name, "Simulation Name!")
        self.assertEqual(exp2.slug, "Simulation_Name_")
        
    ### Model Class Tests
    def test_name(self):
        #Create model with default simulation.
        testModel = dp.Model("Test Model")
        self.assertEqual(testModel.name, "Test Model")
        self.assertEqual(testModel.sim.name, "Test Model:Default Simulation")
        self.assertEqual(testModel.sim.slug, "Test_Model_Default_Simulation")
        self.assertEqual(len(testModel.sim.models), 1)
        self.assertEqual(testModel.sim.models[0].name, "Test Model")
        
        # Verify Exception if name is not a string.
        self.assertRaises(TypeError, dp.Model, 1)
        self.assertRaises(TypeError, dp.Model, None)
        
        # Verify Exception if description is not a string.
        self.assertRaises(TypeError, dp.Model, ("Model Name", None, 365))
        
        #Replace simulation.
        exp = dp.Simulation()
        exp.name = "New Simulation C\\C/C|C*C?C"
        self.assertEqual(exp.slug, "New_Simulation_C_C_C_C_C_C")
        self.assertIsInstance(testModel.sim, dp.Simulation)
        self.assertIsNot(testModel.sim, exp)
        testModel.sim = exp
        self.assertIs(testModel.sim, exp)
        
        # Test description.
        modelDescription = \
        """ This is a test model. It does not have any components.
        It does not simulate any actual system."""
        testModel.description = modelDescription
        self.assertEqual(testModel.description, modelDescription)
        
        # Test component argument type checking.
        self.assertRaises(TypeError, dp.Event, (29, "Event Name"))

    ###Event Scheduling Tests
    def test_peek(self):
        model = dp.Model("Test Model #1")
        
        self.assertEqual(model.sim.peek(), float('Infinity'))
        
        model.schedule(dp.Event(model, "Event #1"),
                       20,
                       dp.fi.PRIORITY_EARLY)
        self.assertEqual(model.sim.peek(), 20)
        
        model.schedule(dp.Event(model, "Event #2"), 5)
        self.assertEqual(model.sim.peek(), 5)
        
    def test_step(self):
        #Create model and events.
        model = dp.Model("Test Model #2")
        ev_early = dp.Event(model, "Early Event")
        ev_standard = dp.Event(model, "Standard Event")
        ev_late = dp.Event(model, "Late Event")
        
        #Schedule Events
        model.schedule(ev_late, 5, dp.fi.PRIORITY_LATE)
        model.schedule(ev_early, 5, dp.fi.PRIORITY_EARLY)
        model.schedule(ev_standard, 5, dp.fi.PRIORITY_STANDARD)
        
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
        model = dp.Model("RunTest Model")
        model.schedule(dp.Event(model, "First Event"), 0)
        model.schedule(dp.Event(model, "Second Event"), 4)
        model.schedule(dp.Event(model, "Third Event"), 8)
        model.sim.run()
        
        self.assertEqual(len(model.components), 3)
        component_keys = list(model.components.keys())
        model.delete_component(component_keys[0])
        self.assertEqual(len(model.components), 2)
        model.delete_component(component_keys[1])
        self.assertEqual(len(model.components), 1)
        
        self.assertEqual(model.sim.gen.trace.length, 3)
        evtTrace = model.sim.gen.trace
        self.assertEqual(evtTrace[0]['name'], "First Event")
        self.assertEqual(evtTrace[1]['name'], "Second Event")
        self.assertEqual(evtTrace[1]['time'], 4)
        self.assertEqual(evtTrace[2]['name'], "Third Event")
        self.assertEqual(evtTrace[2]['time'], 8)

    def test_appendCallback(self):
        model = dp.Model("AppendCallback Model")
        evt1 = dp.Event(model, "First Event")
        
        def evt1_callback(self):
            evt2 = dp.Event(self.model, "Callback Event")
            self.model.schedule(evt2, 10)

        evt1.append_callback(evt1_callback)
        
        def initializeModel(self):
            self.schedule(evt1, 5)
        
        model.set_initialize_method(initializeModel)
        model.sim.gen.folder_basename = \
                "C:/Projects/despy_output/append_callback1"
        model.sim.run()
        
        evtTrace = model.sim.gen.trace
        self.assertEqual(evtTrace.length, 2)
        self.assertEqual(evtTrace[0]['name'], "First Event")
        self.assertEqual(evtTrace[0]['time'], 5)
        self.assertEqual(evtTrace[1]['name'], "Callback Event")
        self.assertEqual(evtTrace[1]['time'], 15)
        
        #Test reset method and until parameter
        model.sim.reset()
        model.sim.gen.folder_basename = \
                "C:/Projects/despy_output/append_callback2"
        model.sim.run(10)
        evtTrace = model.sim.gen.trace
        self.assertEqual(evtTrace.length, 1)
        
        #Verify that simulation can be restarted from current point.
        model.sim.run()
        self.assertEqual(evtTrace.length, 2)
        
    def test_process(self):
        model = dp.Model("Process Model")
        model.sim.seed = 42
        
        def generator(self):
            while True:
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Repeated Event", delay)
        
        process = dp.Process(model, "Test Process", generator)
        self.assertEqual(process.id,  "Process_Model.Test_Process.1")
        self.assertEqual(len(model.components), 1)
        process.start()
        model.sim.run(20)
        
    def test_simultaneous_events(self):
        #Test simultaneous, different events.
        model = dp.Model("Simultaneous Events Model")
        model.schedule(dp.Event(model, "Event #1"), 3)
        model.schedule(dp.Event(model, "Event #2"), 3)
        self.assertEqual(len(model.components), 2)
        model.sim.run()
        self.assertEqual(model.sim.gen.trace.length, 2)
        
        #Test simultaneous, identical events.
        model2 = dp.Model("Simultaneous Identical Events Model")
        event = dp.Event(model2, "The Event")
        model2.schedule(event, 1)
        model2.schedule(event, 1)
        model2.sim.run()
        self.assertEqual(model2.sim.gen.trace.length, 2)
        
    def test_trace_control(self):
        model = dp.Model("Trace Control")
        event = dp.Event(model, "Trace Control Event")
        
        def event_callback(self):
            self.model.schedule(self, 10)
            
        event.append_callback(event_callback)
        model.sim.schedule(event, 0)
        
        # Default settings limit trace to time < 500
        model.sim.run(1000)
        self.assertEqual(model.trace.length, 50)
         
        # User can set trace start and stop times
        model.sim.reset()
        model.sim.schedule(event, 0)
        model.trace.start = 200
        model.trace.stop = 300
        model.sim.console_output = False
        model.sim.run(1000)
        self.assertEqual(model.trace.length, 10)
        self.assertEqual(model.trace[0]['time'], 200)
        self.assertEqual(model.trace[9]['time'], 290)
        
        # Default maximum trace length is 1000 lines.
        model.sim.reset()        
        evt2 = dp.Event(model, "Trace Control Event Step=1")
        
        def event_callback2(self):
            self.model.schedule(self, 1)
        
        evt2.append_callback(event_callback2)
        model.sim.schedule(evt2, 0)
        model.trace.start = 0
        model.trace.stop = 10000
        model.sim.run(5000)
        self.assertEqual(model.trace.length, 1000)
        
        # User can set maximum trace length
        model.sim.reset()
        model.sim.schedule(evt2, 0)
        model.trace.max_length = 2000
        model.trace.start = 365
        model.trace.stop = 2999
        model.sim.run(3000)
        self.assertEqual(model.trace.length, 2000)
        self.assertEqual(model.trace[0]['time'], 365)
        self.assertEqual(model.trace[1999]['time'], 2364)

if __name__ == '__main__':
    unittest.main()

