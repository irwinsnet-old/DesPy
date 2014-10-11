#!/usr/bin/env python3

from despy.core.base import Component

class Entity(Component):
    
    def __init__(self, model, name):
        super().__init__(model, name)