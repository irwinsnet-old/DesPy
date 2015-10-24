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

import numpy as np

from despy.base.named_object import NamedObject

class StatisticNotFinalizedError(Exception):
    pass


class Statistic(NamedObject):
    """
    
    b1, i1, i2, i4, i8, u1, u2, u4, u8, f2, f4, f8, c8, c16, a
    """
    
    def __init__(self, name, dtype, time_weighted = False, 
                 description = None):
        super().__init__(name, description)
        self._dtype = dtype
        self._time_weighted = time_weighted
        
        self._times = []; self._values = []; self._index = []
        #Index structure
        #[[[rep1_beg, rep1_end], [b1_beg, b1_end] ... [bn_beg, bn_end]],
        # [[rep2_beg, rep2_end], [b1_beg, b1_end] ... [bn_beg, bn_end]],
        # ...
        # [[repn_beg, repn_end], [b1_beg, b1_end] ... [bn_beg, bn_end]]]
       
        self._finalized = False
        self._total_length = None
        self._rep_lengths = None 
        self._mean = None
        self._rep_means = None
        self._min = None
        
#         self._add_rep()

    @property
    def dtype(self):
        return self._dtype
    
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
    def index(self):
        return self._index
    
    @property
    def reps(self):
        return len(self.index)
    
    def _grb(self, rep):
        return self.index[rep][0][0]
    
    def _srb(self, rep, beg):
        self.index[rep][0][0] = beg
    
    def _gre(self, rep):
        return self.index[rep][0][1]
    
    def _sre(self, rep, end):
        self.index[rep][0][1] = end
        
    def _add_rep(self):
        self.index.append([[len(self.times), None]])
        
    def _close_curr_rep(self):
        self._sre(-1, len(self.times)-1)
        
    def increment_rep(self):
        if self.reps > 0:
            self._close_curr_rep()
        self._add_rep()
        
    def append(self, time, value):
        if not self.finalized:
            self._times.append(time)
            self._values.append(value)
        else:
            raise StatisticNotFinalizedError("Cannot append to"
                                             "finalized statistics.")

    def finalize(self):    
        np_times = np.array(self.times, dtype='u8')
        np_values = np.array(self.values, dtype=self.dtype)
        
        self._times = np_times
        self._values = np_values
        
        self._finalized = True

    @property
    def finalized(self):
        return self._finalized
    
    @property
    def total_length(self):
        if self._total_length is not None:
            return self._total_length
        else:
            total_length = len(self.times)
            if self.finalized:
                self._total_length = total_length
            return total_length
    
    @property
    def rep_lengths(self):
        if self._rep_lengths is not None:
            return self._rep_lengths
        else:
            self._close_curr_rep()
            rep_lengths = np.array(
                    [self._gre(i) - self._grb(i) + 1 \
                     for i in range(self.reps)])
            if self.finalized:
                self._rep_lengths = rep_lengths
            return rep_lengths
    
    @property
    def mean(self):
        if self._mean is not None:
            return self._mean
        else:
            mean = np.mean(self.values)
            if self.finalized:
                self._mean = mean
            return mean
                
    @property
    def rep_means(self):
        if self._rep_means is not None:
            return self._rep_means
        else:
            self._close_curr_rep()
            rep_means = np.array(
                    [np.mean(
                        self.values[
                            self._grb(i):self._gre(i)+1])\
                    for i in range(self.reps)])
            if self.finalized:
                self._rep_means = rep_means
            return rep_means

        

        
        
        
        
    