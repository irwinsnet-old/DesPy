#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest

from despy.environment import Environment
from despy.model import Model
from despy.event import Event

class testDespyb(unittest.TestCase):
       
    ### Environment Class Tests
    def test_now(self):
        # Verify that Environment.now is set to 0 by default.
        env1 = Environment()
        self.assertEqual(env1.now, 0)
        self.assertTrue(env1.console_output)
        
        # Test console_output property.
        env1.console_output = False
        self.assertFalse(env1.console_output)
        env1.console_output = True
        self.assertTrue(env1.console_output)
        
        # Verify that Environment.now can be set by the class constructor.
        env2 = Environment(42)
        self.assertEqual(env2.now, 42)
        
        # Verify that a name can be assigned to the environment.
        env2.name = "Environment Name!"
        self.assertEqual(env2.name, "Environment Name!")
        
    ### Model Class Tests
    def test_name(self):
        #Create model with default environment.
        testModel = Model("Test Model")
        self.assertEqual(testModel.name, "Test Model")
        self.assertEqual(testModel.environment.name, "Default Environment")
        
        #Replace environment.
        env = Environment()
        env.name = "New Environment"
        self.assertIsInstance(testModel.environment, Environment)
        self.assertIsNot(testModel.environment, env)
        testModel.environment = env
        self.assertIs(testModel.environment, env)
        self.assertRaises(NotImplementedError, testModel.do_initial_events)
        
        # Test description.
        modelDescription = \
        """ This is a test model. It does not have any components.
        It does not simulate any actual system."""
        testModel.description = modelDescription
        self.assertEqual(testModel.description, modelDescription)

    ###Event Scheduling Tests
    def test_peek(self):
        model = Model("Test Model #1")
        
        self.assertEqual(model.environment.peek(), float('Infinity'))
        
        model.schedule(Event(model, "Event #1",
                Event.PRIORITY_EARLY), 20)
        self.assertEqual(model.environment.peek(), 20)
        
        model.schedule(Event(model, "Event #2"), 5)
        self.assertEqual(model.environment.peek(), 5)
        
    def test_step(self):
        #Create model and events.
        model = Model("Test Model #2")
        ev_early = Event(model, "Early Event",
                Event.PRIORITY_EARLY)
        ev_standard = Event(model, "Standard Event",
                Event.PRIORITY_STANDARD)
        ev_late = Event(model, "Late Event",
                Event.PRIORITY_LATE)
        
        #Schedule Events
        model.schedule(ev_late, 5)
        model.schedule(ev_early, 5)
        model.schedule(ev_standard, 5)
        
        #Verify events run in correct order.
        print()
        felItem = model.environment.step()
        self.assertEqual(felItem.evt.name, "Early Event")
        felItem = model.environment.step()
        self.assertEqual(felItem.evt.name, "Standard Event")
        felItem = model.environment.step()
        self.assertEqual(felItem.evt.name, "Late Event")
        env = model.environment
        self.assertEqual(env.now, 5)

    def test_run(self):
        model = Model("RunTest Model")
        model.schedule(Event(model, "First Event"), 0)
        model.schedule(Event(model, "Second Event"), 4)
        model.schedule(Event(model, "Third Event"), 8)
        model.environment.run()
        
        self.assertEqual(len(model.environment.eventTrace), 3)
        evtTrace = model.environment.eventTrace
        self.assertEqual(evtTrace[0].evt_name, "First Event")
        self.assertEqual(evtTrace[1].evt_name, "Second Event")
        self.assertEqual(evtTrace[1].time, 4)
        self.assertEqual(evtTrace[2].evt_name, "Third Event")
        self.assertEqual(evtTrace[2].time, 8)

    def test_appendCallback(self):
        model = Model("AppendCallback Model")
        evt1 = Event(model, "First Event")
        
        

if __name__ == '__main__':
    unittest.main()

