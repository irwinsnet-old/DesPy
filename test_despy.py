#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest

import despy

class testDespyb(unittest.TestCase):
       
    ### Environment Class Tests
    def test_now(self):
        # Verify that Environment.now is set to 0 by default.
        env1 = despy.Environment()
        self.assertEqual(env1.now, 0)
        self.assertTrue(env1.console_output)
        
        # Test console_output property.
        env1.console_output = False
        self.assertFalse(env1.console_output)
        env1.console_output = True
        self.assertTrue(env1.console_output)
        
        # Verify that Environment.now can be set by the class constructor.
        env2 = despy.Environment(42)
        self.assertEqual(env2.now, 42)
        
        # Verify that a name can be assigned to the environment.
        env2.name = "Environment Name!"
        self.assertEqual(env2.name, "Environment Name!")
        
    ### Model Class Tests
    def test_name(self):
        #Create model with default environment.
        testModel = despy.Model("Test Model")
        self.assertEqual(testModel.name, "Test Model")
        self.assertEqual(testModel.environment.name, "Default Environment")
        
        #Replace environment.
        env = despy.Environment()
        env.name = "New Environment"
        self.assertIsInstance(testModel.environment, despy.Environment)
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
        model = despy.Model("Test Model #1")
        
        self.assertEqual(model.environment.peek(), float('Infinity'))
        
        model.schedule(despy.Event(model, "Event #1",
                despy.Event.PRIORITY_EARLY), 20)
        self.assertEqual(model.environment.peek(), 20)
        
        model.schedule(despy.Event(model, "Event #2"), 5)
        self.assertEqual(model.environment.peek(), 5)
        
    def test_step(self):
        #Create model and events.
        model = despy.Model("Test Model #2")
        ev_early = despy.Event(model, "Early Event",
                despy.Event.PRIORITY_EARLY)
        ev_standard = despy.Event(model, "Standard Event",
                despy.Event.PRIORITY_STANDARD)
        ev_late = despy.Event(model, "Late Event",
                despy.Event.PRIORITY_LATE)
        
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
        

if __name__ == '__main__':
    unittest.main()

