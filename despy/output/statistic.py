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
    def setup(self):
        """Called by sim to notify Statistic that new rep is starting.
        """
        pass

    @abstractmethod
    def teardown(self, time = None):
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
        
    def setup(self):
        self._index.append([len(self._times), 0])
        
    def teardown(self, time = None):
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
#                 self.initialize()            
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
        self._total_time = None
        self._mean = None
        self._reps = None
        self._rep_lengths = None
        self._rep_means = None
        self.properties.append(['total_length', 'total_time', 'mean',
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
        
    def setup(self):
        self._index.append([len(self._times), 0, None])
        
    def teardown(self, time):
        # Method finalize() is only run once
        if len(self._index) == 0:
            return
        assert self._grt(-1) is None
        
        self._spans.append(time + 1 - self._times[-1])
        self._index[-1][2] = time + 1
        
        # Spans sum to rep time      
        #assert np.sum(self._spans[self._grb(-1):self._gre(-1)]) == self._grt(-1)
                                  
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
        if self._finalized:
            raise StatisticError("Cannot append to "
                                 "finalized statistics.")
            
        if (self._grl(-1) == 0) and (time != self._initial_time):
            raise StatisticError("For TimeWeightedStatistic, first "
                        "value appended in rep must be at "
                        "Simulation.initial_time: {0}. Attempted to "
                        "append value at time "
                        "{1}.".format(self._initial_time, time))
        
        if self._grl(-1) == 1:
            self._spans.append(time - self._initial_time)
        elif self._grl(-1) > 1:
            self._spans.append(time - self._times[-1])

        self._times.append(time)
        self._values.append(value)         
        self._index[-1][1] += 1
        assert len(self._values) == len(self._times)
        assert len(self._spans) == len(self._times) - 1
        
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
    def total_time(self):
        if self._total_time is not None:
            return self._total_time
        else:
            total_time = np.sum(self._spans)
            if self._finalized:
                self._total_time = total_time
            return total_time
            
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
            #assert np.sum(rep_lengths) == self.total_length
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