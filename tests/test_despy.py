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
        dp.Session().model = dp.Component("Test")
        exp1 = dp.Simulation()
        self.assertEqual(exp1.now, 0)
        self.assertTrue(exp1.gen.console_trace)
        
        # Test console_output property.
        exp1.gen.console_trace = False
        self.assertFalse(exp1.gen.console_trace)
        exp1.gen.console_trace = True
        self.assertTrue(exp1.gen.console_trace)
        
        # Verify that Simulation.now can be set by the class constructor.
        dp.Session().model = dp.Component("Test")
        exp2 = dp.Simulation(42)
        self.assertEqual(exp2.now, 42)
        
        # Verify that a name can be assigned to the simulation.
        exp2.name = "Simulation Name!"
        self.assertEqual(exp2.name, "Simulation Name!")
        self.assertEqual(exp2.slug, "Simulation_Name_")
        
    ### Model Class Tests
    def test_name(self):
        #Create model with default simulation.
        testModel = dp.Component("Test Model")
        dp.Session().model = testModel
        _ = dp.Simulation(name = "Test Simulation")
        self.assertEqual(testModel.name, "Test Model")
        self.assertEqual(testModel.sim.name, "Test Simulation")
        self.assertEqual(testModel.sim.slug, "Test_Simulation")
        self.assertIsNotNone(testModel.sim.model)
        self.assertEqual(testModel.sim.model.name, "Test Model")
        
        # Verify Exception if name is not a string.
        self.assertRaises(TypeError, dp.Component, 1)
        self.assertRaises(TypeError, dp.Component, None)
        
        # Verify Exception if description is not a string.
        self.assertRaises(TypeError, dp.Component, ("Model Name", None, 365))
        
        #Check simulation.
        dp.Session().model = dp.Component("Test")
        exp = dp.Simulation()
        exp.name = "New Simulation C\\C/C|C*C?C"
        self.assertEqual(exp.slug, "New_Simulation_C_C_C_C_C_C")
        self.assertIsInstance(testModel.sim, dp.Simulation)
#         self.assertIsNot(testModel.sim, exp)
        testModel.session.sim = exp
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
        dp.Session().model = dp.Component("Test Model #1")
        sim = dp.Simulation()
        
        self.assertEqual(sim.peek(), float('Infinity'))
        
        sim.schedule(dp.Event("Event #1"),
                       20,
                       dp.Priority.EARLY)
        self.assertEqual(sim.peek(), 20)
        
        sim.schedule(dp.Event("Event #2"), 5)
        self.assertEqual(sim.peek(), 5)
        
    def test_step(self):
        #Create model and events.
        model = dp.Component("Test Model #2")
        dp.Session().model = model
        sim_ts = dp.Simulation()
        ev_early = dp.Event("Early Event")
        ev_standard = dp.Event("Standard Event")
        ev_late = dp.Event("Late Event")
        
        #Schedule Events
        sim_ts.schedule(ev_late, 5, dp.Priority.LATE)
        model.sim.schedule(ev_early, 5, dp.Priority.EARLY)
        model.sim.schedule(ev_standard, 5, dp.Priority.STANDARD)
        
        #Verify events run in correct order.
        print()
        felItem = model.sim.step()
        self.assertEqual(felItem.event.name, "Early Event")
        felItem = model.sim.step()
        self.assertEqual(felItem.event.name, "Standard Event")
        felItem = model.sim.step()
        self.assertEqual(felItem.event.name, "Late Event")
        exp = model.sim
        self.assertEqual(exp.now, 5)

    def test_run(self):
        model = dp.Component("RunTest Model")
        dp.Session().model = model
        sim = dp.Simulation()
        model.sim.schedule(dp.Event("First Event"), 0)
        sim.schedule(dp.Event("Second Event"), 4)
        sim.schedule(dp.Event("Third Event"), 8)
        model.sim.initialize()
        model.sim.run()
        model.sim.finalize()
        
        self.assertEqual(model.sim.gen.trace.length, 3)
        evtTrace = model.sim.gen.trace
        self.assertEqual(evtTrace[0]['name'], "First Event")
        self.assertEqual(evtTrace[1]['name'], "Second Event")
        self.assertEqual(evtTrace[1]['time'], 4)
        self.assertEqual(evtTrace[2]['name'], "Third Event")
        self.assertEqual(evtTrace[2]['time'], 8)
        
    class AppendCallbackModel(dp.Component):
        def __init__(self, name):
            super().__init__(name)
            self.evt1 = dp.Event("First Event")
            self.evt1.append_callback(dp.Callback(self.evt1_callback))
        
        def initialize(self):
            self.sim.schedule(self.evt1, 5)
            
        def evt1_callback(self):
            evt2 = dp.Event("Callback Event")
            self.sim.schedule(evt2, 10)
            

    def test_appendCallback(self):
        model = self.AppendCallbackModel("AppendCallback Model")
        
        dp.Session().model = model
        sim_tc = dp.Simulation()
        sim_tc.gen.folder_basename = ("C:/Projects/despy_output/"
                                        "append_callback1")
        sim_tc.initialize()
        sim_tc.run()
        sim_tc.finalize()
        
        evtTrace = model.sim.gen.trace
        self.assertEqual(evtTrace.length, 2)
        self.assertEqual(evtTrace[0]['name'], "First Event")
        self.assertEqual(evtTrace[0]['time'], 5)
        self.assertEqual(evtTrace[1]['name'], "Callback Event")
        self.assertEqual(evtTrace[1]['time'], 15)
         
        #Test initialize method and until parameter
        model.sim.reset()
        model.sim.gen.folder_basename = \
                "C:/Projects/despy_output/append_callback2"
        model.sim.initialize()
        model.sim.run(10)
        evtTrace = model.sim.gen.trace
        self.assertEqual(evtTrace.length, 1)
          
        #Verify that simulation can be restarted from current point.
        model.sim.runf(20)
        self.assertEqual(evtTrace.length, 2)
        
    def test_process(self):
        model = dp.Component("Process Model")
        
        def generator(self):
            while True:
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Repeated Event", delay)
        
        process = dp.Process("Test Process", generator)
        
        #Invalid attributes raise ValueError
        self.assertRaises(ValueError, model.add_component,
                          "Test Process", process)
        self.assertRaises(ValueError, model.add_component,
                          "sim", process)
        
        model.add_component("Test_Process", process)
        self.assertEqual(len(model.components), 1)
        dp.Session().model = model
        _ = dp.Simulation()
        model.sim.seed = 42
        process.start()
        model.sim.initialize()
        model.sim.run(20)
        
    def test_simultaneous_events(self):
        #Test simultaneous, different events.
        model = dp.Component("Simultaneous Events Model")
        
        def setup(self):
            self.sim.schedule(dp.Event("Event #1"), 3)
            self.sim.schedule(dp.Event("Event #2"), 3)
        model.setup = setup
        
        dp.Session().model = model
        sim = dp.Simulation()
        sim.initialize()        
        sim.run()
        sim.finalize()
        self.assertEqual(model.sim.gen.trace.length, 2)
        
        #Test simultaneous, identical events.
        model2 = dp.Component("Simultaneous Identical Events Model")
        dp.Session().model = model2
        _ = dp.Simulation()
        event = dp.Event("The Event")
        model2.sim.schedule(event, 1)
        model2.sim.schedule(event, 1)
        model2.initialize()
        model2.sim.run()
        self.assertEqual(model2.sim.gen.trace.length, 2)
        
    def test_trace_control(self):
        model = dp.Component("Trace Control")
        dp.Session().model = model
        _ = dp.Simulation()
        event = dp.Event("Trace Control Event")
        
        def event_callback(self):
            self.sim.schedule(self.owner, 10)
            
        event.append_callback(dp.Callback(event_callback))
        model.sim.schedule(event, 0)
        
        # Default settings limit trace to time < 500
        model.sim.initialize()
        model.sim.run(1000)
        model.sim.finalize()
        self.assertEqual(model.sim.gen.trace.length, 50)
         
        # User can set trace start and stop times
        model.sim.reset()
        model.sim.schedule(event, 0)
        model.sim.gen.trace.start = 200
        model.sim.gen.trace.stop = 300
        model.sim.console_output = False
        model.sim.initialize()
        model.sim.run(1000)
        model.sim.finalize()
        self.assertEqual(model.sim.gen.trace.length, 10)
        self.assertEqual(model.sim.gen.trace[0]['time'], 200)
        self.assertEqual(model.sim.gen.trace[9]['time'], 290)
        
        # Default maximum trace length is 1000 lines.
        model.sim.reset()     
        evt2 = dp.Event("Trace Control Event Step=1")
         
        def event_callback2(self):
            self.sim.schedule(self.owner, 1)
         
        evt2.append_callback(dp.Callback(event_callback2))
        model.sim.schedule(evt2, 0)
        model.sim.gen.trace.start = 0
        model.sim.gen.trace.stop = 1000
        model.sim.initialize()
        model.sim.run(5000)
        model.sim.finalize()
        self.assertEqual(model.sim.gen.trace.length, 1000)
         
        # User can set maximum trace length
        model.sim.name = "bigTrace"
        model.sim.reset()
        model.sim.gen.folder_basename = \
                "C:/Projects/despy_output/trace_control"
        model.sim.schedule(evt2, 0)
        model.sim.gen.trace.max_length = 2000
        model.sim.gen.trace.start = 365
        model.sim.gen.trace.stop = 2999
        model.sim.initialize()
        model.sim.run(3000)
        model.sim.finalize()
        self.assertEqual(model.sim.gen.trace.length, 2000)
        self.assertEqual(model.sim.gen.trace[0]['time'], 365)
        self.assertEqual(model.sim.gen.trace[1999]['time'], 2364)

if __name__ == '__main__':
    unittest.main()

