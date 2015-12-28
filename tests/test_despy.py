#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest
import scipy.stats as stats

from despy.session import Session
from despy.simulation import Simulation
from despy.model.component import Component
from despy.event import Event, Priority, Callback
from despy.model.process import Process

class testDespyb(unittest.TestCase):
       
    ### Simulation Class Tests
    def test_now(self):
        # Verify that Simulation.now is set to 0 by default.
        Session.new()
        exp1 = Simulation(Component("Test"))
        cfg = exp1.config
         
        self.assertEqual(exp1.now, 0)
        self.assertTrue(cfg.console_trace)
         
        # Test console_output property.
        cfg.console_trace = False
        self.assertFalse(cfg.console_trace)
        cfg.console_trace = True
        self.assertTrue(cfg.console_trace)
         
        # Verify that Simulation.now can be set by the class constructor.
        Session.new()
        exp2 = Simulation(Component("Test"))
        exp2.config.initial_time = 42
        exp2.initialize()
        self.assertEqual(exp2.now, 42)
          
    ### Model Class Tests
    def test_name(self):
        #Create model with default simulation.
        Session.new()
        session = Session()
        testModel = Component("Test Model")
        session.model = testModel
        session.sim = Simulation()
        self.assertEqual(testModel.name, "Test Model")
        self.assertIsNotNone(testModel.sim.model)
        self.assertEqual(testModel.sim.model.name, "Test Model")
          
        # Verify Exception if name is not a string.
        self.assertRaises(TypeError, Component, 1)
        self.assertRaises(TypeError, Component, None)
          
        # Verify Exception if description is not a string.
        self.assertRaises(TypeError, Component, ("Model Name", None, 365))
          
        #Check simulation.
        session.model = Component("Test")
        exp = Simulation()
        session.sim = exp
        self.assertIsInstance(session.sim, Simulation)
          
        # Test description.
        modelDescription = \
        """ This is a test model. It does not have any components.
        It does not simulate any actual system."""
        testModel.description = modelDescription
        self.assertEqual(testModel.description, modelDescription)
          
        # Test component argument type checking.
        self.assertRaises(TypeError, Event, (29, "Event Name"))
  
    ###Event Scheduling Tests
    def test_peek(self):
        Session.new()
        session = Session()
        session.model = Component("Test Model #1")
        sim = session.sim = Simulation()
          
        self.assertEqual(sim.peek(), float('Infinity'))
          
        sim.schedule(Event("Event #1"),
                       20,
                       Priority.EARLY)
        self.assertEqual(sim.peek(), 20)
          
        sim.schedule(Event("Event #2"), 5)
        self.assertEqual(sim.peek(), 5)
          
    def test_step(self):
        #Create model and events.
        Session.new()
        session = Session()
        model = Component("Test Model #2")
        session.model = model
        session.sim = sim_ts = Simulation()
        sim_ts.initialize()
        ev_early = Event("Early Event")
        ev_standard = Event("Standard Event")
        ev_late = Event("Late Event")
          
        #Schedule Events
        sim_ts.schedule(ev_late, 5, Priority.LATE)
        model.sim.schedule(ev_early, 5, Priority.EARLY)
        model.sim.schedule(ev_standard, 5, Priority.STANDARD)
          
        #Verify events run in correct order.
        print()
        felItem = model.sim._step()
        self.assertEqual(felItem.event.name, "Early Event")
        felItem = model.sim._step()
        self.assertEqual(felItem.event.name, "Standard Event")
        felItem = model.sim._step()
        self.assertEqual(felItem.event.name, "Late Event")
        exp = model.sim
        self.assertEqual(exp.now, 5)
  
    def test_run(self):
        Session.new()
        session = Session()
        model = Component("RunTest Model")
        session.model = model
        session.sim = sim = Simulation()
        model.sim.schedule(Event("First Event"), 0)
        sim.schedule(Event("Second Event"), 4)
        sim.schedule(Event("Third Event"), 8)
        model.sim.initialize()
        model.sim.run()
        results = model.sim.finalize()
          
        self.assertEqual(results.trace.length, 3)
        evtTrace = results.trace
        self.assertEqual(evtTrace[0]['name'], "First Event")
        self.assertEqual(evtTrace[1]['name'], "Second Event")
        self.assertEqual(evtTrace[1]['time'], 4)
        self.assertEqual(evtTrace[2]['name'], "Third Event")
        self.assertEqual(evtTrace[2]['time'], 8)
          
    class AppendCallbackModel(Component):
        def __init__(self, name):
            super().__init__(name)
            self.evt1 = Event("First Event")
            self.evt1.append_callback(Callback(self.evt1_callback))
          
        def setup(self):
            self.sim.schedule(self.evt1, 5)
              
        def evt1_callback(self):
            evt2 = Event("Callback Event")
            self.sim.schedule(evt2, 10)
  
    def test_appendCallback(self):
        Session.new()
        session = Session()        
        model = self.AppendCallbackModel("AppendCallback Model")
        session.model = model
 
        cfg = session.config
        session.sim = sim_tc = Simulation()
        cfg.folder_basename = ("C:/Projects/despy_output/"
                                        "append_callback1")
        sim_tc.initialize()
        sim_tc.run()
        results = sim_tc.finalize()
        results.write_files()
          
        evtTrace = results.trace
        self.assertEqual(evtTrace.length, 2)
        self.assertEqual(evtTrace[0]['name'], "First Event")
        self.assertEqual(evtTrace[0]['time'], 5)
        self.assertEqual(evtTrace[1]['name'], "Callback Event")
        self.assertEqual(evtTrace[1]['time'], 15)
           
        #Test initialize method and until parameter
        model.sim.reset()
        self.assertEqual(sim_tc._trace.length, 0)
        cfg.folder_basename = \
                "C:/Projects/despy_output/append_callback2"
        self.assertEqual(session.config.folder_basename,
                         "C:/Projects/despy_output/append_callback2")
        model.sim.initialize()
        model.sim.run(10)
        evtTrace = model.sim._trace
        self.assertEqual(evtTrace.length, 1)
            
        #Verify that simulation can be restarted from current point.
        results = model.sim.runf(20)
        self.assertEqual(results.trace.length, 2)
        results.write_files()
          
    def test_process(self):
        session = Session.new()
        model = Component("Process Model")
          
        def generator(self):
            while True:
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Repeated Event", delay)
          
        process = Process("Test Process", generator)
          
        #Invalid attributes raise ValueError
        self.assertRaises(ValueError, model.add_component,
                          "Test Process", process)
        self.assertRaises(ValueError, model.add_component,
                          "sim", process)
          
        model.add_component("Test_Process", process)
        self.assertEqual(len(model.components), 1)
        session.model = model
        _ = Simulation()
        session.config.seed = 42
        process.start()
        model.sim.initialize()
        model.sim.runf(20)
          
    def test_simultaneous_events(self):
        #Test simultaneous, different events.
        Session.new()
        model = Component("Simultaneous Events Model")
          
        def setup(self):
            self.sim.schedule(Event("Event #1"), 3)
            self.sim.schedule(Event("Event #2"), 3)
        model.setup = setup
         
        session = Session() 
        session.model = model
        session.sim = sim = Simulation()
        sim.initialize()        
        sim.run()
        results = sim.finalize()
        self.assertEqual(results.trace.length, 2)
          
        #Test simultaneous, identical events.
        model2 = Component("Simultaneous Identical Events Model")
        session.model = model2
        sim = session.sim = Simulation()
        event = Event("The Event")
        model2.sim.schedule(event, 1)
        sim.schedule(event, 1)
        sim.initialize()
        results = sim.runf()
        self.assertEqual(results.trace.length, 2)
         
    def test_trace_control(self):
        Session.new()
        model = Component("Trace Control")
        session = Session()
        session.model = model
        session.sim = sim = Simulation()
        event = Event("Trace Control Event")
         
        def event_callback(self):
            self.sim.schedule(self.owner, 10)
             
        event.append_callback(Callback(event_callback))
        sim.schedule(event, 0)
         
        # Default settings limit trace to time < 500
        sim.initialize()
        sim.run(1000)
        results = sim.finalize()
        self.assertEqual(results.trace.length, 50)
          
        # User can set trace start and stop times
        sim.reset()
        sim.schedule(event, 0)
         
        session.config.trace_start = 200
        session.config.trace_stop = 300
         
        sim.console_output = False
        sim.initialize()
        sim.run(1000)
        results = sim.finalize()
        self.assertEqual(results.trace.length, 10)
        self.assertEqual(results.trace[0]['time'], 200)
        self.assertEqual(results.trace[9]['time'], 290)
         
        # Default maximum trace length is 1000 lines.
        sim.reset()     
        evt2 = Event("Trace Control Event Step=1")
          
        def event_callback2(self):
            self.sim.schedule(self.owner, 1)
          
        evt2.append_callback(Callback(event_callback2))
        model.sim.schedule(evt2, 0)
        session.config.trace_start = 0
        session.config.trace_stop = 1000
        model.sim.initialize()
        model.sim.run(5000)
        results = model.sim.finalize()
        self.assertEqual(results.trace.length, 1000)
          
        # User can set maximum trace length
        sim.name = "bigTrace"
        sim.reset()
        session.config.folder_basename = \
                "C:/Projects/despy_output/trace_control"
        sim.schedule(evt2, 0)
        session.config.trace_max_length = 2000
        session.config.trace_start = 365
        session.config.trace_stop = 2999
        sim.initialize()
        sim.run(3000)
        results = model.sim.finalize()
        results.write_files()
        self.assertEqual(results.trace.length, 2000)
        self.assertEqual(results.trace[0]['time'], 365)
        self.assertEqual(results.trace[1999]['time'], 2364)

if __name__ == '__main__':
    unittest.main()

