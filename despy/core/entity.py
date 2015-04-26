#!/usr/bin/env python3

from despy.core.component import Component

class Entity(Component):
    """An entity is a component
          that represents something in the real world that moves through
          the system.
    """
    
    def __init__(self, model, name, description = None):
        super().__init__(model, name, description)