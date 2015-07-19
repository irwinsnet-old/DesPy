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
        self._dtype = dtype
        self._finalized = False        
        self._reps = list()
        self._batches = list()
        self._times = list()
        self._obs = list()
        self._mean = None

    @property
    def dtype(self):
        return self._dtype
    
    @property
    def finalized(self):
        return self._finalized
    
    @property
    def reps(self):
        return self._reps
    
    @property
    def batches(self):
        return self._batches
    
    @property
    def times(self):
        return self._times
    
    @property
    def obs(self):
        return self._obs
    
    @property
    def mean(self):
        if not self.finalized:
            return np.mean(np.array(self.obs))
        elif self._mean is None :
            self._mean = np.mean(self.obs)
            return self._mean
        else:
            return self._mean
        
    def append(self, rep, batch, time, value):
        if not self.finalized:
            self._reps.append(rep)
            self._batches.append(batch)
            self._times.append(time)
            self._obs.append(value)
        else:
            raise StatisticNotFinalizedError("Cannot append to"
                                             "finalized statistics.")
        
    def append_point(self, point):
        self.append(point.rep, point.batch, point.time,
                          point.value)
        
    def __len__(self):
        return len(self.obs)
    
    def __getitem__(self, i):
        return self.Point(self.reps[i], self.batches[i], \
                          self.times[i], self.obs[i])
    
    def finalize(self):
        self.final = np.zeros(len(self),
                dtype=[('rep', 'u2'), ('batch', 'u2'), ('time', 'u4'),
                       ('value', self.dtype)])
        
        self.final['rep'] = self.reps
        self.final['batch'] = self.batches
        self.final['time'] = self.times
        self.final['value'] = self.obs
        
        self._finalized = True
        
        self._reps = self.final['rep']
        self._batches = self.final['batch']
        self._times = self.final['time']
        self._obs = self.final['value']
        
class StatisticNotFinalizedError(Exception):
    pass
        

        
        
        
        
    