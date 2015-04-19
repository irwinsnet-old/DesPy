#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
..  module:: despy.core.__init__.py

**despy.core**

    The `despy.core` package includes classes that are essential for any
    Despy simulation.
    
        * :class:`despy.core.simulation.Simulation`: Every Despy
          simulation must have one instance of the `simulation` class.
          The `simulation` class initializes the top-level model and its
          components, manages the simulation clock and FEL, and executes
          events.
        * :class:`despy.core.simulation.FelItem`: Every item on the FEL
          must be an instance of FelItem. A FelItem consists of the
          event, the scheduled time, and priority.
        * :class:`despy.core.NoEventsRemainingError`: Raised by the
          `Simulation.step` method when no events remain on the FEL.
        * :class:`despy.core.event.Event`: Instances of the Event class
          are placed on the FEL and executed by the simulation. Users
          may define custom events by sub-classing the event class.
        * :class:`despy.core.Model.model`: The model represents the
          real- world system that is being simulated. The user will
          generally build their model by sub-classing the `model` class.
        * :class:`despy.core.component.Component`: Models consist of
          several components, such as queues, processes, and entities.
          The `Component` class is the base class for the model's
          components. It maintains a counter, which uniquely identifies
          components, and has attributes for access the model and
          simulation objects.
        * :class:`despy.core.entity.Entity`: An entity is a component
          that represents something in the real world that moves through
          the system.
        * :class:`despy.core.resource.Resource`: A resource is a
          component that represents a real-world resource -- generally
          an object or entity with limited availability that provides
          some kind of service.
        * :class:`despy.core.resource.ResourceFinishActivityEvent`:
          Occurs when a resource completes an activity and becomes
          available.
        * :class:`despy.core.process.Process`: The Process class
          supports process style simulations. It allows the user to
          implement a generator function that adds events to the FEL
          that represent a related sequence of real-world activities.
        * :class:`despy.core.process.ProcessTimeOutEvent`: A subclass
          of Event that is scheduled by a process.
        * :class:`despy.core.queue.Queue`: A component that represents
          a real world queue, such as a line of customers waiting for a
          a server, or a group of products waiting for a machine.

    The __init__.py module for the despy.core package imports all
    core modules, so the user does not have to import each module
    individually. For example, the following statement imports all
    core modules under the `dp` namespace.::
    
        import despy.core as dp
    
"""

from despy.core.simulation import Simulation
from despy.core.simulation import FelItem as fi
from despy.core.model import Model
from despy.core.event import Event
from despy.core.process import Process
from despy.core.queue import Queue
from despy.core.entity import Entity
from despy.core.resource import Resource