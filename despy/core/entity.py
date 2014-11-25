#!/usr/bin/env python3

from despy.core.component import Component

class Entity(Component):
    
    def __init__(self, model, name, description = None):
        super().__init__(model, name, description)