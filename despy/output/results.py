#!/usr/bin/env python3
import os
from despy.output.trace import Trace
# from itertools import count
# import matplotlib.pyplot as plt

class Results(object):
    def __init__(self, simulation):
        self.sim = simulation
        self.trace = Trace(self)
        self.timestamp = None
        self.path = None
        self.folder = None
        
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
            for _, component in model.components.items():
                component.get_report(self.folder)
#                 counter = count(1)
#                 if report is not None:
#                     file_name = '/' + "Rpt{0}.png".format(next(counter))
#                     report.savefig(self.folder + file_name)
                    
            
