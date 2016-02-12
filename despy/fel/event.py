#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.model.event
****************

..  autosummary::

    Event
    
    
..  todo

    Refactor event so it no longer inherits from Component.
    
    Add remove_trace_field method.
    
    Consider getting rid of trace_record history.
    
    Use custom event CB object that receives event class as argument.
"""

import types
from collections import OrderedDict

from despy.model.component import Component
from despy.output.trace import TraceRecord

EARLY = -1
STANDARD = 0
LATE = 1 

class Priority():
    """Define priorities for ordering events scheduled at the same time.
    
    **Priority Levels**
        The Priority class defines three constants that are used to
        prioritize events that are scheduled to occur at the same time.
        Events assigned a higher priority will occur before events that
        are assigned lower priorities.
        
        *Priority.STANDARD*
            Despy uses Priority.STANDARD as the default priority when no
            other priority is specified.
            
        *Priority.EARLY*
            Events assigned Priority.EARLY will be executed before
            Priority.STANDARD and Priority.LATE events.
            
        *Priority.LATE*
            Events assigned Priority.LATE will be executed after
            Priority.EARLY and Priority.STANDARD events.
            
        Events scheduled to occur at the same time with the same
        priority may be executed in any order.
        
        The priority integer value is added to the scheduled event time.
        Internally, Despy multiplies the scheduled time by 10. This
        means that events scheduled to occur at time 1 are internally
        scheduled for time 10, time 12 events would occur at internal
        time 120, etc. This scheduling mechanism allows priorities as
        high as 4 and as low as -4. A model that requires more than
        three different priorities probably needs to be redesigned,
        therefore, Despy only provides named constants for priorities
        from -1 to 1.
    """
    EARLY = -1
    STANDARD = 0
    LATE = 1

class Event(Component):
    """ A base class for all events.

    Create an event by inheriting from the Event class. Subclasses of
    Event must instantiate one or more of the doPriorEvent(),
    do_event(), or doPostEvent() methods. The Simulation will execute
    these methods when the Event time occurs and the Event object is
    removed from the FEL.
      
    **Inherited Classes**
      * :class:`despy.model.component.Component`
    
    **Members**
    
    ..  autosummary::
    
        trace_fields
        trace_records
        append_callback
        add_trace_field
        do_event
        dp_update_trace_record
        _reset
        __lt__
        __gt__
    """


    def __init__(self, name, trace_fields = None):
        """Initialize the Event object.

        *Arguments*
            ``model`` (:class:`despy.model.model.Model`):
                The Model that the event belongs to.
            ``name`` (string):
                A short string describing the event. The name will be
                printed in the event trace report.
            ``trace_fields`` (collections.OrderedDict)
                An ordered dictionary of fields that will be added to the
                trace record for this event.
        """

        super().__init__(name)
        self.description = "Event"
        self._callbacks = []
        self._trace_fields = OrderedDict()
        if trace_fields is not None:
            for key, value in trace_fields.items():
                self.trace_fields[key] = value
        self._trace_records = []
        
    @property
    def trace_fields(self):
        """An ordered dictionary containing custom trace data.
        
        *Returns:* An instance of ``OrderedDict`` with custom trace data
        stored as key: value pairs.
        """
        return self._trace_fields
    
    @property
    def trace_records(self):
        """A list of trace records for completed events.
        
        A single event object can be reused by rescheduling it on the
        FEL. The ``trace_records`` attribute is a list of all
        trace records that have been completed for the ``Event`` object.
        
        *Returns:* A list of :class:`despy.output.trace.TraceRecord`
        objects.
        """
        
        return self._trace_records
    
    def append_callback(self, callback):
        """Appends a function to the event's callback list.
        
        The function will be called when the event is removed from the
        FEL and executed.
        
        *Arguments*
            callback (function):
                A variable that represents a class method or function.
        
        """
        if isinstance(callback, types.FunctionType) or isinstance(callback,
                                                            types.MethodType):
            self._callbacks.append(callback)
        else:
            raise TypeError("Object passed to Event.append_callback() was a "
                            "{} object. Nust be a function or method "
                            "object.".format(callback.__class__))
    
    def add_trace_field(self, key, value):
        """Add custom fields to the event's trace record.
        
        This method is typically called from an event's callback method.
        It adds ``value`` to the event's trace record, labeled with the
        text in ``key``.
        
        *Arguments*
            ``key`` (String)
                A text label that describes the data in ``value``.
            ``value`` (String or Number)
                A number, string, or other text-convertible value.
        """
        self.trace_fields[key] = value
        
    def add_message(self, message, fields):
        msg_record = TraceRecord(self.sim.rep, self.sim.now,
                                 self.sim.pri, "Msg", message)
        
        if fields is not None:
            msg_record.add_fields(fields)
            
        self.trace_records.append(msg_record)

    def dp_do_event(self):
        """Executes an event's callback functions.
        
        Internal Method. The ``_do_event`` called by the ``Simulation``
        class's ``step()`` method. It is not intended to be called by the
        user.
        
        *Returns:* ``True`` if a callback method is executed. ``None`` if
        there are no callbacks attached to the event.
        """
        # Event record will precede any messages created in do_event().
        evt_record = TraceRecord(self.sim.rep, self.sim.now,
                                 self.sim.pri, "Event", self.name)
        self.trace_records.append(evt_record)
        
        self.do_event()
        for callback in self._callbacks:
            if isinstance(callback, types.FunctionType):
                callback(self)
            if isinstance(callback, types.MethodType):
                callback()
            
        # Modify record with info generated during event.
        self.trace_records[0] = self.dp_update_trace_record(evt_record)
        self.sim.results.trace.add(self.trace_records)
        
        # Clean up in case event is re-used.
        self.trace_records.clear()  

    def do_event(self):
        pass
    
    def dp_update_trace_record(self, trace_record):
        """Updates a trace record with custom fields.
        
        Internal Method. The ``dp_update_trace_record`` method is called
        by the ``trace`` object. It is not intended to be called by the
        user.
        
        *Arguments*
            ``trace_record``
                A :class:`despy.output.trace.TraceRecord` object. The
                TraceRecord will be added to the simulation's trace
                report to record the occurrence of the event.
        
        *Returns:* A Python list containing the updated trace record.
        
        """  
        trace_record = self.update_trace_record(trace_record)
        
        if self.trace_fields is not None:
            for key, value in self.trace_fields.items():
                trace_record[key] = value        
        
        return trace_record
    
    def update_trace_record(self, trace_record):
        return trace_record
    
    def __lt__(self, y):
        """Defines how ``Event`` objects respond to less-than operator.
        
        The Python magic methods ``__lt__`` and ``__gt__`` are necessary
        because the FEL is implemented as a heap. All items on a heap
        must be sortable. Events are primarily sorted by simulation time.
        For events that are scheduled to occur at the same time, this
        method provides a secondary sort order based on the ``Event``
        object's ``id`` attribute.
        
        *Arguments*
            ``y``
                The other ``Event`` object that is being compared with
                the less-than operator.
                
        *Returns:* ``True`` if ``self.id < y.id``, ``False`` otherwise.
        """
        return self.id < y.id
     
    def __gt__(self, y):
        """Defines how ``Event`` objects respond to '>' operator.
        
        See documentation for ``__lt__`` for an explanation of why this
        Python magic method is necessary.
        
        *Arguments*
            ``y``
                The other ``Event`` object that is being compared with
                the greater-than operator.
                
        *Returns:* ``True`` if ``self.id > y.id``, ``False`` otherwise.
        """
        return self.id > y.id

        