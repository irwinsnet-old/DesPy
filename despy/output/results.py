#!/usr/bin/env python3
import os
from despy.output.trace import Trace
from despy.output.report import HtmlReport
    
class Output(object):
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
            self.report.append_output(self.sim.get_output())
            
            for _, component in model.components.items():
                output = component.get_output(self.folder)
                if output is not None:
                    self.report.append_output(output)
            
            self.report.write_report(self.folder)
