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
    List of messages and events that occurred during the simulation.
    
..  todo::

    Modify other classes to return length through a property, not a
    callable method.
    
    Modify trace report order so main event message comes first,
    event related messages second.
    
    Replace get_row with get_standard_fields and get_custom_fields.
    Each method will have a Boolean argument that specifies whether
    returned list will include labels.
"""
from collections import OrderedDict
import csv
from despy.output.datatype import Datatype
        
class TraceRecord(OrderedDict):
    """Single record in a trace report containing multiple data fields.
    
    A TraceRecord object represents a single occurrence that
    happens during the simulation. By default, TraceRecord objects
    contain the following fields:
    
    1. ``_number:`` Every TraceRecord is assigned a unique sequential
    integer starting at 0.
    2. ``time:`` The simulation time at which the TraceRecord occurred.
    3. ``priority:`` The priority of the event associated with the
    TraceRecord.
    4. ``record_type:`` A string that describes the type of TraceRecord.
    5. ``name:`` The name of the event or occurrence associated with
    the TraceRecord.
    
    Each TraceRecord field consists of a descriptive label and the
    associate value. TraceRecord inherits from collections.OrderedDict,
    so all dictionary and ordered dictionary methods and attributes are
    available.
        
    **Attributes**
      * :attr:`TraceRecord.standard_labels`: List of standard field
        labels included in every TraceRecord.
      * :attr:`TraceRecord.custom_labels`: List of custom field labels
        added to TraceRecord by designer.
    
    **Methods**
        * :meth:`TraceRecord.__str__`: Returns a string representation
          of the TraceRecord.
        * :meth:`TraceRecord.add_fields`: Adds a custom data field to
          the TraceRecord object.
        * :meth:`TraceRecord.get_row`: Returns a list of TraceRecord
          fields.
    """
    def __init__(self, number, time, priority, record_type, name):
        """Construct a TraceRecord object.
        
        *Arguments*
            ``_number`` (Integer)
                The TraceRecord _number. Starts at zero.
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
        super().__init__()
        
        self['number'] = number
        self['time'] = time
        self['priority'] = priority
        self['record_type'] = record_type
        self['name'] = name
        self._standard_labels = list(self.keys())
       
    def __str__(self):
        """Returns a string representation of the TraceRecord.
        
        Used to generate console trace output. The string consists of
        the number, time and priority (-1 for early, 0 for standard, +1
        for late), record_type, name, and custom fields, separated by
        vertical bars (|). A typical TraceRecord string looks like
        this::
        
            2|    0+0| Event| Customer Arrives| Interarrival_Time: None| Customer: Resource Model:Customer#1
            
        *Returns:* String
        """
        #Format data from default fields
        tem1 = "{number:4}|{time:5}{priority:+2}| {record_type}| "
        tem2 = "{name}"
        template = tem1 + tem2
        default_fields = template.format(**self)
        
        #Format data from custom fields
        custom_field_list = []
        for label in self.custom_labels:
            custom_field_list.append("| {}: {}".format(label,
                                                   self[label]))
        custom_fields = "".join(custom_field_list)
                               
        return default_fields + custom_fields
    
    @property
    def standard_labels(self):
        """List of standard field labels included in every TraceRecord.
        
        *Type:* Python list containing String values.
        """
        return self._standard_labels
    
    @property
    def custom_labels(self):
        """List of custom field labels added to TraceRecord by designer.
        
        *Type:* Python list containing String values.
        """
        num_standard_fields = len(self.standard_labels)
        if len(self) > num_standard_fields:
            custom_labels = list(self.keys())
            for _ in range(0, num_standard_fields):
                del custom_labels[0]
            return custom_labels
        else:
            return []

    def add_fields(self, fields):
        """Adds a custom data field to the TraceRecord object.
        
        *Arguments*
            ``fields`` (dict or collections.OrderedDict object)
                A custom label and data field.
        """
        for label, data in fields.items():
            self[label] = data
            
    def get_row(self):
        """Returns a list of TraceRecord fields.
        
        The first five items of the list are the standard field values
        in order (number, time, priority, record_type, and name). The
        standard fields will be followed by a field label and value for
        every custom field that was added by the designer. This method
        is used by the Trace object to write rows in the csv trace
        report.
        
        *Returns:* Python list
        """
        trace_row = []
        for label in self.standard_labels:
            trace_row.append(self[label])
        
        for label in self.custom_labels:
            trace_row.append(label + ":")
            trace_row.append(self[label])
            
        return trace_row
        
class Trace(object):
    """List of messages and events that occurred during the simulation.
    
    **Attributes**
        * :attr:`Trace.start`: Trace will start recording events at this
          simulation time.
        * :attr:`Trace.stop`: Trace will stop recording events at this
          simulation time.
        * :attr:'Trace.max_length: Maximum number of TraceRecords in
          Trace object.
        * :attr:`Trace.length`: Number of records in Trace object.
          Read-only.
          
    **Methods**
        * :meth:`Trace.__getitem__`: Enables accessing TraceRecord with
          square brackets and index.
        * :meth:`Trace.is_active`: True if Trace object is currently
          recording.
        * :meth:`Trace.add`: Adds TraceRecords to Trace class and writes
          console output.
    """
    
    
    def __init__(self, generator):
        #Public attributes
        self._start = 0
        self._stop = 500
        self._max_length = 1000        
        
        #Private attributes
        self._gen = generator #Associated despy.core.output.generator
        self._sim = self._gen._sim #Convenient link to simulation object
        self._record_list = [] #List of TraceRecords
        self._number = 0

    @property
    def start(self):
        """Trace will start recording events at this simulation time.
        
        Defaults to simulation time 0.
        
        *Type:* Integer
        """
        return self._start
    
    @start.setter
    def start(self, start_time):
        self._start = start_time

    @property
    def stop(self):
        """Trace will stop recording events at this simulation time.
        
        Defaults to simulation time 500.
        If trace.stop < trace.start, then trace.stop will have no
        effect. The Trace object will record events until reaching
        trace.max_length or until the simulation ends.
        
        *Type: Integer
        """
        return self._stop
    
    @stop.setter
    def stop(self, stop):
        try:
            if stop > self.start:
                self._stop = round(stop)
        except:
            pass
        
    @property
    def max_length(self):
        """Maximum number of TraceRecords in Trace object.
        
        Defaults to 500. The Trace object will stop recording once it
        reaches 500 TraceRecords.
        """
        return self._max_length
    
    @max_length.setter
    def max_length(self, max_length):
        self._max_length = max_length
        
    @property
    def length(self):
        """Number of records in Trace object. Read-only.
        
        *Type:* Integer
        """
        return len(self._record_list)
    
    def __getitem__(self, index):
        """Enables accessing TraceRecord with square brackets and index.
        
        *Arguments*
            ``index`` (Integer)
                The first Record added to the Trace will be at
                index = 0, the second at index = 1, and so on.
        """
        return self._record_list[index]
    
    def is_active(self):
        """True if Trace object is currently recording.
        
        True if max_length not reached and current simulation time
        between Trace.start and Trace.stop. False otherwise.
        
        *Returns:* Boolean
        """
        now = self._sim.now
        return (now < self.stop) and (self._number < self.max_length) \
            and (now >= self.start)
        
    def add(self, trace_records):
        """Adds TraceRecords to Trace class and writes console output.
        
        *Arguments:*
            `trace_records`: :class:`despy.output.trace.TraceRecord`
                A single or list of TraceRecord objects
        """
        if self.is_active():
            
            #Check if argument is a single TraceRecord or a list.
            if isinstance(trace_records, TraceRecord):
                records = [trace_records]
            elif isinstance(trace_records, list):
                records = trace_records
                
            #Save each TraceRecord object to the Trace object.
            for rec in records:
                self._record_list.append(rec)
                self._number = self._number + 1
                
                #Write TraceRecord to the console.
                if self._sim.gen.console_trace:
                    assert isinstance(rec, TraceRecord)
                    print(rec)
            
    def add_message(self, message, fields = None):
        trace_record = TraceRecord(self._number, self._sim.now,
                                   self._sim.pri, "Msg", message)
        if fields is not None:
            trace_record.add_fields(fields)
        
        self.add(trace_record)
        if self._gen._sim.evt is not None:
            self._gen._sim.evt.trace_records.append(trace_record)
            
#         if self._gen._sim.evt is None:
#             self.add(trace_record)
#         else:
#             self._gen._sim.evt.trace_records.append(trace_record)
    
    def add_event(self, time, priority, event):
        if self.is_active():
            trace_record = TraceRecord(self._number, time, priority, 'Event',
                                       event.name)
            self.add(event._update_trace_record(trace_record))
        
    def clear(self):
        del self._record_list[:]
        self._number = 0
    
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
            self.render_output(self._sim.get_data(), trace_writer)
            
            # Write trace table
            trace_writer.writerow(['Record #', 'Time', 'Priority',
                                   'Record Type', 'Name'])
            for trace_record in self._record_list:
                trace_writer.writerow(trace_record.get_row())
            file.close()