#!/usr/bin/env python3

from despy.core.base import _ModelMember

class Entity(_ModelMember):
    
    def __init__(self, model, name):
        super().__init__(model, name)