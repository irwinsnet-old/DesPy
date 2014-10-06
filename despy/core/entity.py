#!/usr/bin/env python3

from despy.core.base import _ModelComponent

class Entity(_ModelComponent):
    
    def __init__(self, model, name):
        super().__init__(model, name)