#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2014, Stacy Irwin

"""
..  module:: despy.core.__init__.py

**despy.core**
    The __init__.py module for the despy.core package imports typical
    core modules, so the user does not have to import each module
    individually. For example, the following statement imports all
    core modules under the ``dp`` namespace.::
    
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