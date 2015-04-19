#!/usr/bin/env python3
from collections import OrderedDict
import csv
from despy.output.datatype import Datatype
        
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
    
    def add_fields(self, fields):
        for key, value in fields.items():
            self.records[key] = value

class Trace(object):
    
    def __init__(self, output):
        self.gen = output
        self.sim = self.gen.sim
        self._list = []
        self.number = 0
        self.start = 0
        self._stop = 500
        self.max_length = 1000
        
    @property
    def stop(self):
        return self._stop
    
    @stop.setter
    def stop(self, stop):
        try:
            if stop > self.start:
                self._stop = round(stop)
        except:
            pass
    
    def active(self):
        now = self.sim.now
        return (now < self.stop) and (self.number < self.max_length) \
            and (now >= self.start) 
    
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
        
    def add(self, trace_records):
        if self.active():
            if isinstance(trace_records, TraceRecord):
                records = [trace_records]
            elif isinstance(trace_records, list):
                records = trace_records
            for rec in records:
                self.append(rec)
                self.number = self.number + 1
                
                if self.sim.gen.console_trace:
                    console_trace = str(rec['time']).rjust(8) + \
                        ':   ' + rec['name']
                    print(console_trace)
            
    def add_message(self, message, fields = None):
        trace_record = TraceRecord(self.number, self.sim.now, "N/A", "Msg",
                                   message)
        if fields is not None:
            trace_record.add_fields(fields)
        if self.gen.sim.evt is None:
            self.add(trace_record)
        else:
            self.gen.sim.evt.trace_records.append(trace_record)
    
    def add_event(self, time, priority, event):
        if self.active():
            trace_record = TraceRecord(self.number, time, priority, 'Event',
                                       event.name)
            self.add(event.update_trace_record(trace_record))
        
    def clear(self):
        del self._list[:]
        self.number = 0
    
    def __getitem__(self, index):
        return self._list[index]
    
    def length(self):
        return len(self._list)
    
    def render_output(self, output, writer):
        for section in output:
            self.render_section(section, writer)
    
    def render_section(self, section, writer):
        if section[0] == Datatype.title:
            writer.writerow([section[1]])
        if section[0] == Datatype.param_list:
            for field in section[1]:
                writer.writerow([field[0], field[1]])
    
    def write_csv(self, directory):
        # Add time stamp to file name
        trace_file = directory + '/trace.csv'
        
        # Open csv file
        with open(trace_file, 'w', newline='') as file:
            trace_writer = csv.writer(file)
            
            # Write header rows
            self.render_output(self.sim.get_data(), trace_writer)
            
            # Write trace table
            trace_writer.writerow(['Record #', 'Time', 'Priority',
                                   'Record Type', 'Name', 'Target'])
            for trace_record in self._list:
                csv_row = []
                for _, field in trace_record.items():
                    csv_row.append(field)
                trace_writer.writerow(csv_row)
            file.close()