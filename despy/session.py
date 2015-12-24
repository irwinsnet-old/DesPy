#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
******************
despy.model.session
******************

..  autosummary::

    Session   
"""
import random

import numpy as np

class Session:
    class __Session:
        def __init__(self):
            self._sim = None
            self._model = None
            self._ouput_config = Config()
            
        @property
        def sim(self):
            return self._sim
        
        @sim.setter
        def sim(self, sim):
            self._sim = sim
            
        @property
        def model(self):
            return self._model
        
        @model.setter
        def model(self, model):
            self._model = model
            
        @property
        def config(self):
            return self._ouput_config
        
        @config.setter
        def config(self, config):
            self._output_config = config
    
    _instance = None
    
    def __init__(self):
        if Session._instance is None:          
            Session._instance = Session.__Session()
    
    def __getattr__(self, name):
        return getattr(self._instance, name)
    
    def __setattr__(self, name, value):
        setattr(self._instance, name, value)
    
    @staticmethod    
    def new():
        Session._instance = Session.__Session()
        return Session()
        
        
class Config(object):
    """Generates the simulation's output reports and graphs.
    
    **Members**
    
    ..  autosummary
    
        console_trace
        folder_basename
        sim
        set_full_path
            
    **Python Library Dependencies**
        * :mod:`os`
    
    """
    
            
    def __init__(self):
        """Construct a Config object.
        
        *Arguments*
            ``simulation`` :class:`despy.model.simulation.Simulation`
                Corresponding simulation object.
        """
        
        #Public Attributes
        self.folder_basename = None
        self.console_trace = True
        self._trace_start = 0
        self._trace_stop = 500
        self._trace_max_length = 1000
        self._trace_reps = (0, 1)
        self._reps = 1
        self.initial_time = 0
        self._seed = None
        
        #Read-only Public Attributes
        self._full_path = None

    @property
    def trace_start(self):
        """Trace will start recording events at this simulation time.
        
        Defaults to simulation time 0.
        
        *Type:* Integer
        """
        return self._trace_start
    
    @trace_start.setter
    def trace_start(self, start):
        self._trace_start = start
    
    @property
    def trace_max_length(self):
        """Maximum number of TraceRecords in Trace object.
        
        Defaults to 500. The Trace object will stop recording once it
        reaches 500 TraceRecords.
        """
        return self._trace_max_length
    
    @trace_max_length.setter
    def trace_max_length(self, max_length):
        self._trace_max_length = max_length
    
    @property
    def trace_stop(self):
        """Trace will stop recording events at this simulation time.
        
        *Type:* Integer
        """
        return self._trace_stop
    
    @trace_stop.setter
    def trace_stop(self, stop):
        try:
            if stop > self.trace_start:
                self._trace_stop = round(stop)
        except:
            pass

    @property
    def console_trace(self):
        """If True, send Trace object data to standard console output.
        
        *Type:* Boolean
        *Default Value:* True
        """
        return self._console_trace

    @console_trace.setter
    def console_trace(self, console_trace):
        self._console_trace = console_trace
        
    @property
    def folder_basename(self):
        """Folder where output reports and graphs will be placed.
        
        If ``None`` (the default value), the simulation will not
        generate any output or trace files. The value stored in
        ``folder_basename`` should be an absolute reference.
        For example::
        
            gen.folder_basename = "C:/despy_output/resource_sim"
            
        The Generator object will add a time-stamp to the end of the
        folder name when generating the output files. This allows the
        use to run the simulation several times without overwriting
        data from previous simulations.
        """
        return self._folder_basename
    
    @folder_basename.setter
    def folder_basename(self, basename):
        self._folder_basename = basename
        
    @property
    def reps(self):
        return self._reps
    
    @reps.setter
    def reps(self, reps):
        self._reps = reps
        
    @property
    def initial_time(self):
        return self._initial_time
    
    @initial_time.setter
    def initial_time(self, initial_time):
        self._initial_time = initial_time
    
    @property
    def seed(self):
        """Calls seed methods in both numpy and standard random modules. 
        
        Set seed to an integer, or to ``None`` (default).
        
        By default (i.e., when seed is set to None), Despy will use a
        different seed, and hence a different random number sequence for
        each run of the simulation. For troubleshooting or testing
        purposes, it's often useful to repeatedly run the simulation
        with the same sequence of random numbers. This can be
        accomplished by setting the seed variable.
        
    
        Designers should use this seed property when seeding the random
        number generators. While despy will use the numpy random number
        generator instead of the generator built into Python's random
        module, we can't guarantee that Python random module functions
        won't sneak into a custom subclass. The numpy and Python random
        number generators use different random number sequences, so it's
        necessary to seed both generators to ensure a consistent random
        number sequence thoughout the simulation.
        return self._seed
        """
        
        return self._seed
    
    @seed.setter
    def seed(self, seed):
        self._seed = seed