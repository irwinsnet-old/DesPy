#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*******************
despy.output.config
*******************

..  autosummary::

    
..  todo::

"""

from despy.output.trace import Trace
from despy.output.report import HtmlReport
from despy.core.session import Session
    
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
    
            
    def __init__(self, simulation):
        """Construct a Config object.
        
        *Arguments*
            ``simulation`` :class:`despy.core.simulation.Simulation`
                Corresponding simulation object.
        """
        self._session = Session()
        self._session.out = self
        
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
