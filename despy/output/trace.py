#!/usr/bin/env python3
from collections import OrderedDict
import csv
        
class TraceRecord():
    def __init__(self, number, time, priority, record_type, name):
        self.records = OrderedDict()
        self.records['number'] = number
        self.records['time'] = time
        self.records['priority'] = priority
        self.records['record_type'] = record_type
        self.records['name'] = name
        
    def __getitem__(self, key):
        return self.records[key]
    
    def __setitem__(self, key, value):
        self.records[key] = value
        
    def __delitem__(self, key):
        del self.records[key]
        
    def __iter__(self):
        return iter(self.records)
    
    def items(self):
        return self.records.items()

class Trace(object):
    
    def __init__(self, output):
        self.out = output
        self.sim = self.out.sim
        self._list = []
        self.number = 0
    
    def append(self, item):
        self._list.append(item)
        
    def create_trace_record(self, time, priority, record_type, name,
                         entity = None, duration = None):
        trace_record = TraceRecord(self.number, time, priority, record_type,
                                   name)
        if entity is not None:
            trace_record['entity'] = entity
        if duration is not None:
            trace_record['duration'] = duration
            
        return trace_record
        
    def add(self, trace_record):
        self.append(trace_record)
        self.number = self.number + 1
        
        if self.sim.console_output:
            console_output = str(trace_record['time']).rjust(8) + \
                ':   ' + trace_record['name']
            print(console_output)
            
    def add_message(self, message):
        trace_record = TraceRecord(self.number, self.sim.now, "N/A", "Msg", message)
        self.add(trace_record)
    
    def add_event(self, time, priority, event, entity = None, duration = None):
        trace_record = TraceRecord(self.number, time, priority, 'Event',
                                   event.name)
        self.add(event.update_trace_record(trace_record))
        
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
                                   'Record Type', 'Name', 'Label', 'Value'])
            for trace_record in self._list:
                csv_row = []
                for _, field in trace_record.items():
                    csv_row.append(field)
                trace_writer.writerow(csv_row)
            file.close()