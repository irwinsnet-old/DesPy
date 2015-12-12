#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
********************
despy.output.results
********************

..  autosummary::

    
..  todo::

"""
import os

from despy.output.trace import Trace
from despy.output.report import HtmlReport

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
            ``simulation`` :class:`despy.core.simulation.Simulation`
                Corresponding simulation object.
        """
        
        #Public Attributes
        self.folder_basename = None
        self.console_trace = True
        
        #Read-only Public Attributes
        self._full_path = None

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
        
    def get_results(self, sim):
        return Results(sim, self)


class Results(object):
    def __init__(self, sim, config):
        self._sim = sim
        self._cfg = config
        self._mod = sim.model
        self._trace = Trace(self)
        self._report = HtmlReport()  
    
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
        
        # Take no action if no output folder specified.
        if self._cfg.folder_basename is None:
            return None
        
        # Finalize model and components.
        
        # Write trace csv file.
        self.set_full_path()
        self._trace.write_csv(self._full_path)
        
        #Get data for all components and create HTML report.
        self._cfg.report.append_output(self._sim.get_data())
            
        for _, component in self._mod.components.items():
            output = component.get_data()
            if output is not None:
                self._cfg.report.append_output(output)
        
        self._report.write_report(self._full_path)
        
    def set_full_path(self):
        """Adds time-stamp to end of Generator.folder_basename.
        
        The time-stamp is the stop time for the simulation.
        """
        timestamp = \
                self._sim.run_stop_time.strftime('_%y_%j_%H_%M_%S')
        self._full_path = self.folder_basename + '/Run' + timestamp
                
        if not os.path.exists(self._full_path):
            os.makedirs(self._full_path) 

