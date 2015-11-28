#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
from abc import abstractmethod

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
    
    Add datatype check to append().

"""
import abc

import numpy as np

from despy.base.named_object import NamedObject
from despy.core.simulation import Session

class StatisticError(Exception):
    pass

class AbstractStatistic(metaclass = abc.ABCMeta):
    def __init__(self, name, dtype):
        self.name = name
        if dtype in ['b1', 'i1', 'i2', 'i4', 'i8', 'u1', 'u2', 'u4',
                     'u8', 'f2', 'f4', 'f8', 'c8', 'c16', 'a']:
            self._dtype = dtype
        else:
            raise TypeError("Value passed to dtype parameter: "
                    "{}, is not a supported data type".format(dtype))
            
        self._description = None
        self._properties = []
            
    @property
    def name(self):
        """The name of the object.
        
        *Returns:* String
        
        *Raises:*
            ``TypeError`` if name is not a string.
        """
        return self._name
    
    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self._name = name
        else:
            message = "{0} passed to name".format(name.__class__) + \
                    " argument. Should be a string."
            raise TypeError(message)
        
    @property
    def dtype(self):
        """A string that specifies the data type for the statistic.
        
        Statistic uses numpy data types, which can be any one of the
        following values: b1, i1, i2, i4, i8, u1, u2, u4, u8, f2, f4,
        f8, c8, c16, a
        
        The letter specifies the type of data and the digit is the
        number of bytes.
        
            * b1: boolean, 
            * i1, i2, i4, i8: integer
            * u1, u2, u4, u8: unsigned integer
            * f2, f4, f8: float
            * c8, c16: complex
            * a: character, can by any number of digits
        
        """
        return self._dtype
    
    @property
    def description(self):
        """Gets a description of the model.
        
        *Returns:* string

        *Raises:* ``TypeError`` if description is not a string or type
        ``None``.
        """
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, str) or description is None:
            self._description = description
        else:
            message = "{0} passed to name".format(description.__class__) + \
                    " argument. Should be a string or None."             
            raise TypeError(message)
        
    @property
    def properties(self):
        """OrderedDict that lists all available output properties.
        """
        return self._properties

    @abstractmethod
    def append(self, value, time = None):
        """Append a data point to the statistic.

        *Arguments*
            ``value``: type corresponds to Statistic.dtype attribute
            ``time`` : integer, optional
                Statistics may require the time associated with the
                data point, e.g., time-weighted averages, plots, etc.
                
        *Raises*
            * ``TypeError`` if value type does not correspond to dtype.
            * ``RuntimeError`` if statistic is otherwise unable to
              append the value (e.g., the statistic has been finalized
              and is read-only).
        """
        pass

    @abstractmethod
    def start_rep(self):
        """Called by sim to notify Statistic that new rep is starting.
        """
        pass

    @abstractmethod
    def end_rep(self, time = None):
        """Called by sim to notify Statistic that rep has concluded.
        
        *Arguments*
            ``time``: integer, simulation time at which rep ends.
        """
        pass
    
    @abstractmethod
    def finalize(self):
        """Sim callback to notify statistic that simulation is ending.
        """
        pass
    
class  DiscreteStatistic(AbstractStatistic):
    """Basic statistic that is NOT time-weighted."""
    
    def __init__(self, name, dtype):
        super().__init__(name, dtype)        
        
        #### Readable Properties #####
        self._total_length = None
        self._mean = None
        self._reps = None
        self._rep_lengths = None
        self._rep_means = None
        self.properties.append(['total_length', 'mean',
                                'reps', 'rep_lengths', 'rep_means'])
        
        #### Internal Details #####
        self._times = [];
        self._values = [];
        self._index = []        
        # Index structure
        #[[rep1_beg, rep1_len], 
        # [rep2_beg, rep2_len],
        # ...
        # [repn_beg, repn_len]]
        self._finalized = False
        
    @property
    def reps(self):
        """The number of replications that have been commenced.
        """
        if self._reps is not None:
            return self._reps
        else:
            reps = len(self._index)
            if self._finalized:
                self._reps = reps
            return reps
        
    @property
    def times(self):
        return np.array(self._times)
    
    @property
    def values(self):
        return np.array(self._values)
        
    def start_rep(self):
        self._index.append([len(self._times), 0])
        
    def end_rep(self, time = None):
        pass
    
    def _grb(self, rep):
        """Returns the index for the first statistic value in rep.
        """
        return self._index[rep][0]
    
    def _gre(self, rep):
        """Returns the index for the last statistic value in rep.
        """
        return self._index[rep][0] + self._index[rep][1] - 1
    
    def _grl(self, rep):
        """Returns the number of statistic values in rep.
        """
        return self._index[rep][1]
    
    def append(self, time, value):
        """Append a data point to the statistic.

        *Arguments*
            ``value``: type corresponds to Statistic.dtype attribute
            ``time`` : integer, optional
                Statistics may require the time associated with the
                data point, e.g., time-weighted averages, plots, etc.
                
        *Raises*
            * ``TypeError`` if value type does not correspond to dtype.
            * ``RuntimeError`` if statistic is otherwise unable to
              append the value (e.g., the statistic has been finalized
              and is read-only).
        """
        if not self._finalized:
            self._times.append(time)
            self._values.append(value)
#             if len(self.index) == 0:
#                 self.start_rep()            
            self._index[-1][1] += 1
        else:
            raise StatisticError("Cannot append to finalized "
                                 "statistics.")
        
    def finalize(self):
        """Convert data to numpy arrays to speed up calculations."""       
        np_times = np.array(self._times, dtype='u8')
        np_values = np.array(self._values, dtype=self.dtype)
        self._times = np_times
        self._values = np_values
        self._finalized = True
        
    @property
    def total_length(self):
        if self._total_length is not None:
            return self._total_length
        else:
            total_length = len(self._times)
            if self._finalized:
                self._total_length = total_length
            return total_length
            
    @property
    def mean(self):
        if self._mean is not None:
            return self._mean
        else:
            mean = np.mean(self.values)
            if self._finalized:
                self._mean = mean
            return mean
        
    @property
    def rep_lengths(self):
        if self._rep_lengths is not None:
            return self._rep_lengths
        else:
            rep_lengths = np.array(
                    [self._grl(rep) for rep in range(self.reps)])
            if self._finalized:
                self._rep_lengths = rep_lengths
            return rep_lengths
        
    @property
    def rep_means(self):
        if self._rep_means is not None:
            return self._rep_means
        else:
            rep_means = np.array([np.mean(
                            self._values[self._grb(i):self._gre(i)+1])\
                            for i in range(self.reps)])
            if self._finalized:
                self._rep_means = rep_means
            return rep_means

class  TimeWeightedStatistic(AbstractStatistic):
    """Basic statistic that is NOT time-weighted."""
    
    def __init__(self, name, dtype):
        super().__init__(name, dtype)
               
        #### Readable Properties #####
        self._total_length = None
        self._mean = None
        self._reps = None
        self._rep_lengths = None
        self._rep_means = None
        self.properties.append(['total_length', 'mean',
                                'reps', 'rep_lengths', 'rep_means'])
        
        #### Internal Details #####
        self._initial_time = 0
        self._times = [];
        self._values = [];
        self._spans = []
        self._index = []        
        # Index structure
        #[[rep1_beg, rep1_len, rep1_time], 
        # [rep2_beg, rep2_len, rep2_time],
        # ...
        # [repn_beg, repn_len, repn_time]]
        self._finalized = False
        
    @property
    def initial_time(self):
        return self._initial_time
    
    @initial_time.setter
    def initial_time(self, time):
        assert isinstance(time, int)
        assert time >= 0
        self._initial_time = time
    
    @property
    def reps(self):
        """The number of replications that have been commenced.
        """
        if self._reps is not None:
            return self._reps
        else:
            reps = len(self._index)
            if self._finalized:
                self._reps = reps
            return reps
        
    @property
    def times(self):
        return np.array(self._times)
    
    @property
    def spans(self):
        return np.array(self._spans)
    
    @property
    def values(self):
        return np.array(self._values)
        
    def start_rep(self):
        self._index.append([len(self._times), 0, None])
        
    def end_rep(self, time):
        # Method end_rep() is only run once
        assert self._grt(-1) is None
        
        self._spans.append(time + 1 - self._spans(-1))
        self._index[-1][2] = time + 1
        
        # Spans sum to rep time      
        assert np.sum(self._spans[self._grb(-1):
                                  self.gre(-1)]) == self._grt(-1)
                                  
        # Same length for spans, times, and values
        assert len(self._spans) == len(self._times)
        assert len(self._values) == len(self._times)
    
    def _grb(self, rep):
        """Returns the index for the first statistic value in rep.
        """
        return self._index[rep][0]
    
    def _gre(self, rep):
        """Returns the index for the last statistic value in rep.
        """
        return self._index[rep][0] + self._index[rep][1] - 1
    
    def _grl(self, rep):
        """Returns the number of statistic values in rep.
        """
        return self._index[rep][1]
    
    def _grt(self, rep):
        return self._index[rep][2]
    
    def append(self, time, value):
        """Append a data point to the statistic.

        *Arguments*
            ``value``: type corresponds to Statistic.dtype attribute
            ``time`` : integer, optional
                Statistics may require the time associated with the
                data point, e.g., time-weighted averages, plots, etc.
                
        *Raises*
            * ``TypeError`` if value type does not correspond to dtype.
            * ``RuntimeError`` if statistic is otherwise unable to
              append the value (e.g., the statistic has been finalized
              and is read-only).
        """
        if not self._finalized:
            if self._grl(-1) == 0:
                if time != self._initial_time:
                    raise StatisticError("For TimeWeightedStatistic, "
                            "first value appended in rep must be at "
                            "Simulation.initial_time: {0}. Attempted "
                            "to append value at time {1}"
                            ".".format(self._initial_time, time))
                else:
                    self._spans.append(time - self._spans(-1))
            self._times.append(time)
            self._values.append(value)         
            self._index[-1][1] += 1
            assert len(self._values) == len(self._spans)
            assert len(self._spans) == len(self._times) - 1
        else:
            raise StatisticError("Cannot append to "
                                 "finalized statistics.")
        
    def finalize(self):
        """Convert data to numpy arrays to speed up calculations."""
        assert not self._finalized      
        self._times = np.array(self._times, dtype='u8')
        self._values = np.array(self._values, dtype=self.dtype)
        self._spans = np.array(self._spans, dtype = 'u8')
        self._finalized = True
        
    @property
    def total_length(self):
        if self._total_length is not None:
            return self._total_length
        else:
            total_length = len(self._times)
            assert total_length == np.sum(self.rep_lengths)
            if self._finalized:
                self._total_length = total_length
            return total_length
            
    @property
    def mean(self):
        if self._mean is not None:
            return self._mean
        else:
            mean = np.average(self.values, weights = self._spans,
                              returned = True)
            assert mean[1] == np.sum(self._spans)
            if self._finalized:
                self._mean = mean[0]
            return mean[0]
        
    @property
    def rep_lengths(self):
        if self._rep_lengths is not None:
            return self._rep_lengths
        else:
            rep_lengths = np.array(
                    [self._grl(rep) for rep in range(self.reps)])
            assert np.sum(rep_lengths) == self.total_length
            if self._finalized:
                self._rep_lengths = rep_lengths
            return rep_lengths
        
    @property
    def rep_means(self):
        if self._rep_means is not None:
            return self._rep_means
        else:
            rep_means = np.array(
                [np.average(
                    self.values[self._grb(i):self._gre(i)],
                    weights = self._spans[self._grb(i):self._gre(i)])
                for i in range(self.reps)])
            if self._finalized:
                self._rep_means = rep_means
            return rep_means

class Statistic_old(NamedObject):
    """
    b1, i1, i2, i4, i8, u1, u2, u4, u8, f2, f4, f8, c8, c16, a
    """
    
    def __init__(self, name, dtype, time_weighted = False, 
                 description = None):
        super().__init__(name, description)
        self._dtype = dtype
        self._time_weighted = time_weighted
        
        self._times = []; self._values = []
        
        #Index structure
        #[[rep1_beg, rep1_len], 
        # [rep2_beg, rep2_len],
        # ...
        # [repn_beg, repn_len]]
        self._index = []
        
        #Index structure
        #[[[rep1_beg, rep1_end], [b1_beg, b1_end] ... [bn_beg, bn_end]],
        # [[rep2_beg, rep2_end], [b1_beg, b1_end] ... [bn_beg, bn_end]],
        # ...
        # [[repn_beg, repn_end], [b1_beg, b1_end] ... [bn_beg, bn_end]]]

        self._batches = []
        
        self._finalized = False
        self._total_length = None
        self._rep_lengths = None
        self._max_rep_length = None
        self._time_spans = None
        self._mean = None
        self._rep_means = None
        self._min = None
        self.session = Session()


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
        return self.index[rep][0]
#     
#     def _srb(self, rep, beg):
#         self.index[rep][0] = beg
    
    def _gre(self, rep):
        return self.index[rep][0] + self.index[rep][1] - 1
    
    def _grl(self, rep):
        return self.index[rep][1]
#     
#     def _sre(self, rep, end):
#         self.index[rep][1] = end
        
    def append(self, time, value):
        if not self.finalized:
            self._times.append(time)
            self._values.append(value)
            if len(self.index) == 0:
                self.increment_rep(time)            
            self.index[-1][1] += 1
        else:
            raise StatisticError("Cannot append to"
                                "finalized statistics.")

    def increment_rep(self, now):
        if self.time_weighted:
            if self.times[-1] != now:
                self.append(now, self.values[-1])
        self.index.append([len(self.times), 0])
        
    def get_val(self, rep, index):
        if rep > self.reps:
            raise IndexError("rep is greater than number of "
                             "reps: {}".format(self.reps))
        if index > self._gre(rep):
            raise IndexError("index cannot be larger "
                             "than {}".format(self._gre()))
        else:
            return self.values[self._grb(rep) + index]

    def finalize(self, now):
        if self.reps == 0:
            self.increment_rep(now)
        if self.time_weighted and self.times[-1] != now:
            self.append(now, self.values[-1])
            
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
            rep_lengths = np.array(
                    [self._grl(rep) for rep in range(self.reps)])
            if self.finalized:
                self._rep_lengths = rep_lengths
            return rep_lengths
        
    @property
    def max_rep_length(self):
        if self.reps == 0:
            self.index.append([len(self.times), 0])
        if self._max_rep_length is not None:
            return self._max_rep_length
        else:
            print("Rep-lengths: {}".format(self.rep_lengths)) #DEBUG:
            max_rep_length = np.amax(self.rep_lengths)
        if self.finalized:
            self._max_rep_length = max_rep_length
        return max_rep_length
        
    @property
    def time_spans(self):
        if self._time_spans is not None:
            return self._time_spans
        else:
            spans = []
            for r_idx in range(0, self.reps):
                first_span = [self.times[self._grb(r_idx)]]
                other_spans = [self.times[i] - self.times[i-1] \
                               for i in range(self._grb(r_idx)+1, 
                                              self._gre(r_idx)+1)]
                spans += first_span + other_spans
            if self.finalized:
                self._time_spans = spans
            return spans
                 
    @property
    def mean(self):
        if self._mean is not None:
            return self._mean
        else:
            if self.time_weighted:
                return np.average(self.values, weights = self.time_spans)
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
            rep_means = np.array(
                    [np.mean(
                        self.values[
                            self._grb(i):self._gre(i)+1])\
                    for i in range(self.reps)])
            if self.finalized:
                self._rep_means = rep_means
            return rep_means

        

        
        
        
        
    