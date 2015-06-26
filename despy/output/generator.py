#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
**********************
despy.output.generator
**********************

:class:`Generator`
    Generates the simulation's output reports and graphs.
    
..  todo::

    Make _full_path attribute a documented public attribute.
"""
import os
from despy.output.trace import Trace
from despy.output.report import HtmlReport
    
class Generator(object):
    """Generates the simulation's output reports and graphs.
    
    *Attributes*
        * :attr:`Generator.console_trace`: If True, send Trace object
          data to standard console output.
        * :attr:`Generator.folder_basename`: If ``None`` (the default
          value), the simulation will not generate any output or
          trace files.
        * :attr:`Generator.sim`: Link to Simulation object documented
          by the Generator.         

    *Methods*
        * :meth:`Generator.write_files`: Creates trace and HTML reports
          in folder_basename location.
        * :meth:`Generator.set_full_path`: Adds time-stamp to end of
          Generator.folder_basename.
            
    **Python Library Dependencies**
        * :mod:`os`
    
    """
    
            
    def __init__(self, simulation):
        """Construct a Generator object.
        
        *Arguments*
            ``simulation`` :class:`despy.core.simulation.Simulation`
                Corresponding simulation object.
        """
        #Public Attributes
        self.folder_basename = None
        self.console_trace = True
        self.trace = Trace(self)
        self.report = HtmlReport()        
        
        #Read-only Public Attributes
        self._full_path = None    
        self._sim = simulation

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
    def sim(self):
        """Link to Simulation object documented by the Generator.
         
        *Type:* :class:`despy.core.simulation.Simulation`
        Read Only
        """
        return self._sim
    
    @property
    def trace(self):
        """Events and messages will be recorded in this Trace object.
        
        *Type:* :class:`despy.output.trace.Trace`
        """
        return self._trace
    
    @trace.setter
    def trace(self, trace):
        self._trace = trace
        
    def write_files(self):
        """Creates trace and HTML reports in folder_basename location.
        """
        #Take no action if no output folder specified.
        if self.folder_basename is None:
            return None
        
        #Write trace csv file.
        self.set_full_path()
        self.trace.write_csv(self._full_path)
        
        #Get data for all components and create HTML report.
        for model in self._sim.models:
            self.report.append_output(self.sim.get_data())
            
            for _, component in model.components.items():
                output = component.get_data(self._full_path)
                if output is not None:
                    self.report.append_output(output)
            
            self.report.write_report(self._full_path)
                 
    def set_full_path(self):
        """Adds time-stamp to end of Generator.folder_basename.
        
        The time-stamp is the stop time for the simulation.
        """
        timestamp = \
                self._sim.run_stop_time.strftime('_%y_%j_%H_%M_%S')
        self._full_path = self.folder_basename + '/Run' + timestamp
                
        if not os.path.exists(self._full_path):
            os.makedirs(self._full_path)             
        

