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
from collections import OrderedDict


class Results(object):
    def __init__(self, sim, config):
        self._simulation = sim
        self._sim = OrderedDict()
        self._sim["run_start_time"] = sim.run_start_time
        self.sim["run_stop_time"] = sim.run_stop_time
        self.sim["elapsed_time"] = sim.run_stop_time - sim.run_start_time
        self._config = config
        self._mod = sim.model
        self._report = None
        self._trace = sim._trace
        
    @property
    def config(self):
        return self._config
    
    @property
    def sim(self):
        return self._sim
    
    @property
    def trace(self):
        """Events and messages will be recorded in this Trace object.
        
        *Type:* :class:`despy.output.trace.Trace`
        """
        return self._trace
        
    @property
    def report(self):
        return self._report
    
    def write_files(self):
        """Creates trace and HTML reports in folder_basename location.
        """
        self._report = HtmlReport()
        
        # Take no action if no output folder specified.
        if self._config.folder_basename is None:
            return None
        
        # Finalize model and components.
        
        # Write trace csv file.
        self.set_full_path()
        self._trace.write_csv(self._full_path)
        
        #Get data for all components and create HTML report.
        self.report.append_output(self._simulation.get_data())
            
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
                self._sim["run_stop_time"].strftime('_%y_%j_%H_%M_%S')
        self._full_path = self._config.folder_basename + '/Run' + timestamp
                
        if not os.path.exists(self._full_path):
            os.makedirs(self._full_path) 

