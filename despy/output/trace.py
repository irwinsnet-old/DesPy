#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
******************
despy.output.trace
******************
   
:class:`TraceRecord`
    Single record in a trace report containing multiple data fields.
    
:class:`Trace`
    
..  todo::
"""
from collections import OrderedDict
import csv
from despy.output.datatype import Datatype
        
class TraceRecord():
    """Single record in a trace report containing multiple data fields.
    
    A TraceRecord object represents a single occurrence that
    happens during the simulation. By default, TraceRecord objects
    contain the following fields:
    
    1. ``number:`` Every TraceRecord is assigned a unique sequential
    integer starting at 0.
    2. ``time:`` The simulation time at which the TraceRecord occurred.
    3. ``priority:`` The priority of the event associated with the
    TraceRecord.
    4. ``record_type:`` A string that describes the type of TraceRecord.
    5. ``name:`` The name of the event or occurrence associated with
    the TraceRecord.
    
    Individual TraceRecord fields can be access with the following
    syntax:::
    
        time = traceRecord_instance['time']
        
    **Attributes**
      * :attr:`TraceRecord.fields`: OrderedDict object containing
        TraceRecord key value pairs.
    
    **Methods**
        * :meth:`TraceRecord.__getitem__`: Allows using square brackets
          to access TraceRecord fields.
        * :meth:`TraceRecord.__setitem__`: Allows using square brackets
          to set TraceRecord fields.
        * :meth:`TraceRecord.__delitem__`: Removes a field from a
          TraceRecord object.
        * :meth:`TraceRecord.__iter__`: Allows iteration over the
          TraceRecord object.
        * :meth:`TraceRecord.items`: Returns an ordered view of the
          TraceRecord's key-value pairs.
        * :meth:`TraceRecord.add_fields`: Adds a custom data field to
          the TraceRecord object.
    """
    def __init__(self, number, time, priority, record_type, name):
        """Construct a TraceRecord object.
        
        *Arguments*
            ``number`` (Integer)
                The TraceRecord number. Starts at zero.
            ``time`` (Integer)
                The simulation time associated with the TraceRecord.
            ``priority`` (Integer from -4 to 4)
                The priority of the event associated with the
                TraceRecord.
            ``record_type`` (String)
                A string that describes the type of TraceRecord.
            ``name``
                The name of the event or occurrence associated with
                the TraceRecord.
        """
        self._fields = OrderedDict()
        self._fields['number'] = number
        self._fields['time'] = time
        self._fields['priority'] = priority
        self._fields['record_type'] = record_type
        self._fields['name'] = name
        
    @property
    def fields(self):
        """OrderedDict object containing TraceRecord label-data pairs.
        
        *Type:* Python OrderedDict Object.
        """
        return self._fields
        
    def __getitem__(self, label):
        """Allows using square brackets to access TraceRecord fields.
        
        *Arguments*
            ``label`` (String)
                TraceRecord field label.
                
        *Returns:* Data from TraceRecord field.
        """
        return self._fields[label]
    
    def __setitem__(self, label, data):
        """Allows using square brackets to set TraceRecord fields.
        
        *Arguments*
            ``label`` (String)
                TraceRecord field label.
            ``data``
                Value of TraceRecord field.
        """
        self._fields[label] = data
        
    def __delitem__(self, label):
        """Removes a field from a TraceRecord object.
        
        *Arguments*
            ``label`` (String)
                TraceRecord field label
        """
        del self._fields[label]
        
    def __iter__(self):
        """Allows iteration over the TraceRecord object.
        
        When iterated, TraceRecord will return fields in order, starting
        with 'number', then 'time', 'priority', 'record_type', 'name',
        and then on to custom fields added by the designer. The custom
        fields will be returned in the order they were added to the
        TraceRecord.
        
        *Returns:* A collections.OrderedDict object containing the
        TraceRecord object's data fields.
        """
        return iter(self._fields)
    
    def items(self):
        """Returns ordered view of the TraceRecord's label-data pairs.
        
        *Returns:* The collections.OrderedDict's items() view.
        """
        return self._fields.items()
    
    def add_fields(self, fields):
        """Adds a custom data field to the TraceRecord object.
        
        *Arguments*
            ``fields`` (dict or collections.OrderedDict object)
                A custom label and data field.
        """
        for label, data in fields.items():
            self._fields[label] = data

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
            self.add(event._update_trace_record(trace_record))
        
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