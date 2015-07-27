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

    Add a time-weighted mean.
    Add mins and maxs
    Add variances
    Add standard deviations
    Add medians


"""
from collections import namedtuple

import numpy as np

from despy.base.named_object import NamedObject

class Statistic(NamedObject):
    """
    
    b1, i1, i2, i4, i8, u1, u2, u4, u8, f2, f4, f8, c8, c16, a
    """
    
#     Point = namedtuple('Point', 'rep time value')
    
    def __init__(self, name, dtype, reps = 1, time_weighted = False, 
                 description = None):
        super().__init__(name, description)
        self._dtype = dtype
        self._reps = reps
        self._time_weighted = time_weighted
        
        self._times = [list() for _ in range(self.reps)]
        self._values = [list() for _ in range(self.reps)]
        
        self._finalized = False
        self._total_length = None
        self._rep_lengths = None 
        self._mean = None
        self._rep_means = None
        self._min = None

    @property
    def dtype(self):
        return self._dtype
    
    @property
    def reps(self):
        return self._reps
    
    @property
    def time_weighted(self):
        return self._time_weighted

    @property
    def times(self):
        if self.finalized:
            return self._times
        else:
            return np.array(self._times)

    @property
    def values(self):
        if self.finalized:
            return self._values
        else:
            return np.array(self._values)
        
    @property
    def finalized(self):
        return self._finalized
    
    @property
    def total_length(self):
        if self._total_length is not None:
            return self._total_length
        else:
            total_length = np.sum(self.rep_lengths)
            if self.finalized:
                self._total_length = total_length
            return total_length
    
    @property
    def rep_lengths(self):
        if self._rep_lengths is not None:
            return self._rep_lengths
        else:
            reps = len(self.times)            
            rep_lengths = np.array(\
                    [len(self.times[i]) for i in range(reps)])
            if self.finalized:
                self._rep_lengths = rep_lengths
            return rep_lengths
    
    @property
    def mean(self):
        if self._mean is not None:
            return self._mean
        else:
            mean = np.sum(self.rep_means * self.rep_lengths) / \
                    self.total_length
            if self.finalized:
                self._mean = mean
            return mean
                
    @property
    def rep_means(self):
        if self._rep_means is not None:
            return self._rep_means
        else:
            reps = len(self.times)
            rep_means = np.array(\
                    [np.mean(self.values[i]) for i in range(reps)])
            if self.finalized:
                self._rep_means = rep_means
            return rep_means
        
    def append(self, rep, time, value):
        if not self.finalized:
            self._times[rep].append(time)
            self._values[rep].append(value)
        else:
            raise StatisticNotFinalizedError("Cannot append to"
                                             "finalized statistics.")
    
    def finalize(self):
        np_times = np.array(self.times)
        np_values = np.array(self.values)
        
        self._times = np_times
        self._values = np_values
        
        self._finalized = True
        
class StatisticNotFinalizedError(Exception):
    pass
        

        
        
        
        
    