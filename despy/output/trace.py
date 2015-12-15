#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
******************
despy.output.trace
******************

..  autosummary::

    TraceRecord
    Trace
    CSV_file

    
..  todo::

    Modify other classes to return length through a property, not a
    callable method.
    
    Modify trace report order so main event message comes first,
    event related messages second.
    
    Replace get_row with get_standard_fields and get_custom_fields.
    Each method will have a Boolean argument that specifies whether
    returned list will include labels.
    
    Add external dependencies to all class docstrings. Use intersphinx.
    
    Add assert statements to verify correct data types for input.
    
    Refactor to remove use of "_" for private attributes. Only use for
    read-only attributes.
    
    Write column headers to console trace.
"""
from collections import OrderedDict
import csv

from despy.output.report import Datatype
from despy.core.session import Session
        
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
        
    **Members**
    
    ..  autosummary::
    
        standard_labels
        custom_labels
        __str__
        add_fields
        get_row
          
    **Python Library Dependencies**
        * :class:`collections.OrderedDict`
    """
    def __init__(self, rep, time, priority, record_type, name):
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
        
        self['number'] = None
        self['rep'] = rep
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
        template = "{number:4}|{rep:4}|{time:5}{priority:+2}|" \
            "{record_type:8}|{name}"
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
    
    **Members**
    
    ..  autosummary::
    
        start
        stop
        max_length
        __len__
        __getitem__
        is_active
        add
    """
    
    
    def __init__(self):
        
        #Public attributes
        self._max_length = 1000  
        
        #Private attributes
        self._record_list = [] #List of TraceRecords
        self._number = 0
        self._session = Session()
        self._config = self._session.config
        
    @property
    def sim(self):
        return self._session.sim

    @property
    def start(self):
        """Trace will start recording events at this simulation time.
        
        Defaults to simulation time 0.
        
        *Type:* Integer
        """
        return self._config.trace_start

    @property
    def stop(self):
        """Trace will stop recording events at this simulation time.
        
        Defaults to simulation time 500.
        If trace.stop < trace.start, then trace.stop will have no
        effect. The Trace object will record events until reaching
        trace.max_length or until the simulation ends.
        
        *Type:* Integer
        """
        return self._config.trace_stop

        
    @property
    def max_length(self):
        """Maximum number of TraceRecords in Trace object.
        
        Defaults to 500. The Trace object will stop recording once it
        reaches 500 TraceRecords.
        """
        return self._config.trace_max_length
        
    @property
    def length(self):
        """Number of records in Trace object. Read-only.
        
        *Type:* Integer
        """
        return len(self._record_list)
    
    def __len__(self):
        """Built-in len() function will return number of records.
        
        *Returns:* Integer
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
        now = self.sim.now
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
                rec["number"] = self._number
                self._record_list.append(rec)
                self._number = self._number + 1
                
                #Write TraceRecord to the console.
                if self._config.console_trace:
                    assert isinstance(rec, TraceRecord)
                    print(rec)
            
    def add_event(self, rep, time, priority, event):
        """Record an event on the Trace report.
        
        *Arguments:*
            `time` (Integer)
                Simulation time at which the event occurs.
            `priority` (Integer)
                Priority at which the event was scheduled.
            `event` (:class:`despy.core.event.Event)
                Event object that is being recorded.
        """
        if self.is_active():
            trace_record = TraceRecord(rep, time,
                                       priority, 'Event', event.name)
            self.add(event.dp_update_trace_record(trace_record))

    def add_message(self, message, fields = None):
        """Creates a message TraceRecord and adds it to the Trace.
        
        *Arguments:*
            `message` (String)
                A short message that will be saved to the Trace.
            `fields` (Python dictionary)
                Custom fields that will be added to the TraceRecord.
                Optional. Defaults to None.
        """
        trace_record = TraceRecord(self.sim.rep,
                                   self.sim.now,
                                   self.sim.pri, "Msg", message)
        if fields is not None:
            trace_record.add_fields(fields)
        
        #Record message in event trace records.
        self.add(trace_record)
            
    def print_trace_records(self):
        for trace_record in self._record_list:
            print(trace_record)
            
    def write_csv(self, directory):
        """Create a CSV file_name containing all trace data.
        
        *Arguments:*
            ``directory`` (String)
                The full path to the folder that will contain the csv
                file_name.
        """
        file = CSV_file(self, directory)
        file.write()
        return file
        
    def clear(self):
        """Remove all TraceRecords from Trace object.
        """
        del self._record_list[:]
        self._number = 0
        
        
class CSV_file(object):
    """A comma separated values file that displays the trace report.
    
    **Members**
        * :attr:`CSV_file.file_name`: The full name, including the path,
          of the CSV file.
        * :attr:`CSV_file.trace`: The CSV_file will display this Trace
          object.
        * :meth:`CSV_file.write`: Writes self.trace to CSV file at
          location self.file_name.
          
    **Python Library Dependencies**
        * :mod:`csv`
    """
    def __init__(self, trace, directory):
        """Construct a CSV_file object.
        
        *Arguments*
            ``trace`` :class:`despy.core.trace.Trace`
                The CSV_file will display this Trace object.
            ``directory``
                The full path to the location of the CSV file. The CSV
                file will be named "trace.csv".
        """
        #Public attributes
        self._trace = trace
        self._file_name = directory + '/trace.csv'
        
        #Private attributes
        self._writer = None
        
    @property
    def file_name(self):
        """The full name, including the path, of the CSV file.
        
        *Type:* String
        """
        return self._file_name
    
    @file_name.setter
    def file_name(self, file_name):
        self.file_name = file_name
        
    @property
    def trace(self):
        """The CSV_file will display this Trace object.
        
        *Type:* :class:`despy.core.trace.Trace`
        """
        return self._trace
    
    @trace.setter
    def trace(self, trace):
        self._trace = trace
        
    def write(self):
        """Writes self.trace to CSV file at location self.file_name.
        """  
        # Open csv file
        with open(self.file_name, 'w', newline='') as file:
            self._writer = csv.writer(file)
            
            # Write header rows
            self.write_sim_header_data(self.trace.sim.get_data())
            
            # Write trace table
            self._writer.writerow(['Record #', 'Rep', 'Time',
                                   'Priority', 'Record Type', 'Name'])
            for trace_record in self.trace._record_list:
                self._writer.writerow(trace_record.get_row())
            file.close()
            
    def write_sim_header_data(self, output):
        """Convert output list to CSV rows and write to file.
        """
        for section in output:
            if section[0] == Datatype.title:
                self._writer.writerow([section[1]])
            if section[0] == Datatype.param_list:
                for field in section[1]:
                    self._writer.writerow([field[0], field[1]])
                    