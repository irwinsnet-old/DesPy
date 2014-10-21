#!/usr/bin/env python3
import os
from despy.output.trace import Trace

class Results(object):
    def __init__(self, simulation):
        self.sim = simulation
        self.trace = Trace(self)
        self.timestamp = None
        
    def write_files(self, path):
        self.path = path
        self.timestamp = self.sim.run_stop_time.strftime('_%y_%j_%H_%M_%S')
        run_folder = self.path + '/Run' + self.timestamp
        if not os.path.exists(run_folder):
            os.makedirs(run_folder)
        self.trace.write_csv(run_folder)
