#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
**********************
despy.output.statistic
**********************

..  autosummary::


..  todo::


"""
from collections import namedtuple

import numpy as np

from despy.base.named_object import NamedObject

class Statistic(NamedObject):
    """
    
    b1, i1, i2, i4, i8, u1, u2, u4, u8, f2, f4, f8, c8, c16, a
    """
    
    def __init__(self, name, description, dtype):
        super().__init__(name, description)
        self.dtype = dtype
        self.reps = list()
        self.batches = list()
        self.times = list()
        self.values = list()
        self.finalized = False
        
    def append_value(self, time, value, rep = 1, batch = 1):
        self.reps.append(time)
        self.batches.append(batch)
        self.times.append(time)
        self.values.append(value)
        
    def __len__(self):
        return len(self.values)
    
    def finalize(self):
        self.np_arr = np.zeros(len(self),
                dtype=[('rep', 'u2'), ('batch', 'u2')('time', 'u4'),
                       ('value', self.dtype)])
        
        self.np_arr['rep'] = self.reps
        self.np_arr['batch'] = self.batches
        self.np_arr['time'] = self.times
        self.np.arr['value'] = self.values
        
        self.finalize = True
        
        
        
        
    