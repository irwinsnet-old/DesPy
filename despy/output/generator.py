#!/usr/bin/env python3
import os
from despy.output.trace import Trace
from despy.output.report import HtmlReport
    
class Generator(object):
    """ The Generator class generates the simulation's output.
    
    *Attributes*
          * :attr:`.console_trace`: If ``True``, the trace record for each
            event will be sent to the standard output. The default value
            is True. Type: Boolean.
          * :attr:`.output_folder`: If ``None`` (the default value), the
            simulation will not generate any output or trace files.
    
    """
    
    
    @property
    def console_trace(self):
        """ Send trace record to standard output (console) if ``True``.

        The default value is True. Type: Boolean.
        """
        return self._console_output
        
    @property
    def output_folder(self):
        """ A string that identifies the folder where output reports and
        graphs will be placed.
        
        If ``None`` (the default value), the simulation will not generate
        any output or trace files. The value stored in ``output_folder``
        should be an absolute reference. For example::
        
            simulation.output_folder = "C:/Projects/despy_output/resource_sim"
        """
        return self._output_folder
    
    @output_folder.setter
    def output_folder(self, folder):
        self._output_folder = folder
    
    @console_trace.setter
    def console_trace(self, output):
        self._console_output = output
            
    def __init__(self, simulation):
        self.sim = simulation
        self.trace = Trace(self)
        self.timestamp = None
        self.path = None
        self.folder = None
        self.report = HtmlReport()
        
    def set_folder(self, path):
        self.path = path
        self.timestamp = self.sim.run_stop_time.strftime('_%y_%j_%H_%M_%S')
        self.folder = self.path + '/Run' + self.timestamp
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)             
        
    def write_files(self, path):
        self.set_folder(path)
        self.trace.write_csv(self.folder)
        
        for model in self.sim.models:
            self.report.append_output(self.sim.get_data())
            
            for _, component in model.components.items():
                output = component.get_data(self.folder)
                if output is not None:
                    self.report.append_output(output)
            
            self.report.write_report(self.folder)
