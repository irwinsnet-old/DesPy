#!/usr/bin/env python3
from collections import namedtuple
import os, csv

class Output(object):
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
        
        
TraceRecord = namedtuple('TraceRecord', ['record_number_fld', 'time_fld',
                         'priority_fld', 'record_type_fld', 'name_fld'])

# TODO: Change output process -- user specifies an output folder, which will
#   receive the trace csv file, graphics, plots, etc.
class Trace(object):
    
    def __init__(self, output):
        self.out = output
        self.sim = self.out.sim
        self._list = []
        self.event_number = 0
    
    def append(self, item):
        self._list.append(item)
        
    def add_trace_record(self, time, priority, record_type, name):
        trace_record = TraceRecord(record_number_fld=self.event_number,
                                   time_fld=time, priority_fld=priority,
                                   name_fld=name,
                                   record_type_fld=record_type)
        self.append(trace_record)
        self.event_number = self.event_number + 1
        
        if self.sim.console_output:
            console_output = str(trace_record.time_fld).rjust(8) + \
                ':   ' + trace_record.name_fld
            print(console_output)
            
    def add_output(self, output):
        self.add_trace_record(self.sim.now, "N/A", "Std. Ouput", output)
    
    def add_event(self, time, priority, name):
        self.add_trace_record(time, priority, "Event", name)
        
    def clear(self):
        self._list = []
    
    def get(self, index):
        return self._list[index]
    
    def length(self):
        return len(self._list)
    
    def write_csv(self, directory):
        # Add time stamp to file name
        trace_file = directory + '/trace.csv'
        
        # Open csv file
        with open(trace_file, 'w', newline='') as file:
            trace_writer = csv.writer(file)
            
            # Write header rows
            trace_writer.writerow(['Simulation:', self.sim.name])
            trace_writer.writerow(['File:', trace_file])
            trace_writer.writerow(['Seed:', self.sim.seed])
            trace_writer.writerow(['Start Time:',
                                   self.sim.run_start_time.ctime()])
            trace_writer.writerow(['Stop Time:',
                                   self.sim.run_stop_time.ctime()])
            elapsed_time = self.sim.run_stop_time - self.sim.run_start_time
            trace_writer.writerow(['Elapsed Time:', elapsed_time.microseconds])
            trace_writer.writerow([])
            
            # Write trace table
            trace_writer.writerow(['Record #', 'Time', 'Priority',
                                   'Record Type', 'Name'])
            for row in self._list:
                trace_writer.writerow([row.record_number_fld, row.time_fld,
                                      row.priority_fld, row.record_type_fld,
                                      row.name_fld])
            file.close()