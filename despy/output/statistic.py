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
    
    Point = namedtuple('Point', 'rep batch time value')
    
    def __init__(self, name, dtype, description = None ):
        super().__init__(name, description)
        self.dtype = dtype
        self.reps = list()
        self.batches = list()
        self.times = list()
        self.values = list()
        self.finalized = False
        
    def append(self, rep, batch, time, value):
        self.reps.append(rep)
        self.batches.append(batch)
        self.times.append(time)
        self.values.append(value)
        
    def append_point(self, point):
        self.append(point.rep, point.batch, point.time,
                          point.value)
        
    def __len__(self):
        return len(self.values)
    
    def __getitem__(self, i):
        return self.Point(self.reps[i], self.batches[i], \
                          self.times[i], self.values[i])
    
    def finalize(self):
        self.final = np.zeros(len(self),
                dtype=[('rep', 'u2'), ('batch', 'u2'), ('time', 'u4'),
                       ('value', self.dtype)])
        
        self.final['rep'] = self.reps
        self.final['batch'] = self.batches
        self.final['time'] = self.times
        self.final['value'] = self.values
        
        self.finalize = True
        
        self.reps = self.final['rep']
        self.batches = self.final['batch']
        self.times = self.final['time']
        self.values = self.final['value']
        

        
        
        
        
    