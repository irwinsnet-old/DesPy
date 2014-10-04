#!/usr/bin/env python3

from despy.core.base import _ModelMember
from itertools import count

class Entity(_ModelMember):
    
    def __init__(self, model, name):
        super().__init__(model, name)
        
        if not hasattr(self, "count"):
            self.set_counter()
        self.number = self.get_id()
    
    @classmethod
    def set_counter(cls):
        cls.count = count(1)
    
    @classmethod
    def get_id(cls):
        return next(cls.count)