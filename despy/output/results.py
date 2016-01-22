#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
from despy.output.report import HtmlReport
"""
********************
despy.output.results
********************

..  autosummary::

    
..  todo::

"""
import os

from despy.session import Session
from despy.output.trace import Trace

class Results(object):
    def __init__(self, sim):
        self._session = Session()
        self._sim = sim
        self._mod = sim.model
        self._trace = Trace()      
        self._report = None
        self._run_start_time = None
        self._run_stop_time = None
        self._seed = None
        
        self._values = dict()
            
    @property
    def values(self):
        return self._values
        
    @property
    def seed(self):
        """Random number generator seed used for simulation. Read-only
        
        *Type:* ``None`` or Integer
        """
        return self._seed
    
    @property
    def trace(self):
        """Events and messages will be recorded in this Trace object.
        
        *Type:* :class:`despy.output.trace.Trace`
        """
        return self._trace
    
    @property
    def run_start_time(self):
        """The real-world start time for the simulation. Read-only.
        
        *Type:* ``None`` or :class:`datetime.datetime`
        
        Despy uses the run_start_time attribute to calculate the simulation's
        elapsed time. Elapsed time does not include initialization or
        finalization of the simulation, only time that elapses within the
        Simulation.run() method. The attribute will return 'None' if the
        simulation has not yet entered the Simulation.run() method.
        """
        return self._run_start_time
    
    @run_start_time.setter
    def run_start_time(self, time):
        self._run_start_time = time
    
    @property
    def run_stop_time(self):
        """The real-world stop time for the simulation. Read-only.
        
        *Type:* ``None`` or :class:`datetime.datetime`
        
        Despy uses the run_start_time attribute to calculate the simulation's
        elapsed time. Elapsed time does not include initialization or
        finalization of the simulation, only time that elapses within the
        Simulation.run() method. The attribute will return 'None' if the
        simulation is still running events.
        """
        return self._run_stop_time
    
    @run_stop_time.setter
    def run_stop_time(self, time):
        self._run_stop_time = time
    
    @property
    def elapsed_time(self):
        """Real world duration of simulation..
        
        Read-only. Elapsed time between initialization and finalization
        of simulation.
        
        *Type:* ``None`` or :class:`datetime.datetime`
        """
        if self._run_stop_time is not None:
            if self._run_start_time is not None:
                return self._run_stop_time - self._run_start_time
        
    @property
    def report(self):
        return self._report
    
    def write_files(self):
        """Creates trace and HTML reports in folder_basename location.
        """
        self._report = HtmlReport()
        
        # Take no action if no output folder specified.
        if not self._session.config.write_files:
            return None
        if self._session.config.folder_basename is None:
            return None
        
        # Finalize model and components.
        
        # Write trace csv file.
        self.set_full_path()
        self._trace.write_csv(self._full_path)
        
        #Get data for all components and create HTML report.
        self.report.append_output(self._sim.get_data())
            
        for _, component in self._mod.components.items():
            output = component.get_data(self._full_path)
            if output is not None:
                self._report.append_output(output)
        
        self._report.write_report(self._full_path)
        
    def set_full_path(self):
        """Adds time-stamp to end of Generator.folder_basename.
        
        The time-stamp is the stop time for the simulation.
        """
        timestamp = \
                self.run_stop_time.strftime('_%y_%j_%H_%M_%S')
        self._full_path = self._session.config.folder_basename + '/Run' + timestamp
                
        if not os.path.exists(self._full_path):
            os.makedirs(self._full_path) 

