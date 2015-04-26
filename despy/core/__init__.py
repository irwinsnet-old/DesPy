#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
..  module:: despy.core.__init__.py

The `despy.core` package includes classes that are essential for any
Despy simulation.

The __init__.py module for the despy.core package imports all
core modules, so the user does not have to import each module
individually. For example, the following statement imports all
core modules under the `dp` namespace.::
    
    import despy.core as dp

despy.core.simulation
=====================
..  automodule:: despy.core.simulation
    :noindex:

despy.core.event
================
..  automodule:: despy.core.event
    :noindex:
    
despy.core.model
================
..  automodule:: despy.core.model
    :noindex:
    
despy.core.component
====================
..  automodule:: despy.core.component
    :noindex:
    
despy.core.entity
=================
..  automodule:: despy.core.entity
    :noindex:
    
despy.core.resource
===================
..  automodule:: despy.core.resource
    :noindex:
    
despy.core.resource
===================
..  automodule:: despy.core.process
    :noindex:
    
despy.core.queue
===================
..  automodule:: despy.core.queue
    :noindex:
"""

from despy.core.simulation import Simulation
from despy.core.simulation import FelItem as fi
from despy.core.model import Model
from despy.core.event import Event
from despy.core.process import Process
from despy.core.queue import Queue
from despy.core.entity import Entity
from despy.core.resource import Resource