#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.core.event
****************

..  autosummary::

    Event
    
    
..  todo

    Refactor event so it no longer inherits from Component.
    
    Add remove_trace_field method.
"""

import types
import abc
from collections import OrderedDict

from despy.core.component import Component
from despy.core.session import Session

class AbstractCallback(metaclass = abc.ABCMeta):
    def __init__(self, **args):
        self.session = Session()
        self.mod = self.session.model
        self.sim = self.session.sim
        self.args = args
    @abc.abstractmethod
    def call(self):
        pass

class Callback(AbstractCallback):
    def __init__(self, callback_function, owner = None):
        super().__init__()
        if isinstance(callback_function, types.FunctionType):
            self.call = types.MethodType(callback_function, self)
        elif isinstance(callback_function, types.MethodType):
            self.call = callback_function
        else:
            raise TypeError("Argument to Callback.__init__() "
                    "via callback_function argument is not a function "
                    "or method\n"
                    "Argument: {}".format(repr(callback_function)))
        self.owner = owner
        
    def call(self):
        pass        
    

class Event(Component):
    """ A base class for all events.

    Create an event by inheriting from the Event class. Subclasses of
    Event must instantiate one or more of the doPriorEvent(),
    do_event(), or doPostEvent() methods. The Simulation will execute
    these methods when the Event time occurs and the Event object is
    removed from the FEL.
      
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
    
    **Members**
    
    ..  autosummary::
    
        trace_fields
        trace_records
        append_callback
        add_trace_field
        do_event
        _update_trace_record
        _reset
        __lt__
        __gt__
    """


    def __init__(self, name, trace_fields = None):
        """Initialize the Event object.

        *Arguments*
            ``model`` (:class:`despy.core.model.Model`):
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
        if isinstance(callback, AbstractCallback):
            self._callbacks.append(callback)
            callback.owner = self
    
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

    def dp_do_event(self):
        """Executes an event's callback functions.
        
        Internal Method. The ``_do_event`` called by the ``Simulation``
        class's ``step()`` method. It is not intended to be called by the
        user.
        
        *Returns:* ``True`` if a callback method is executed. ``None`` if
        there are no callbacks attached to the event.
        """
        self.do_event()
        
        if len(self._callbacks)==0:
            return None
        else:
            for callback in self._callbacks:
                callback.call()
            return True
        
    def do_event(self):
        pass
    
    def _update_trace_record(self, trace_record):
        """Updates a trace record with custom fields.
        
        Internal Method. The ``_update_trace_record`` method is called
        by the ``trace`` object. It is not intended to be called by the
        user.
        
        *Arguments*
            ``trace_record``
                A :class:`despy.output.trace.TraceRecord` object. The
                TraceRecord will be added to the simulation's trace
                report to record the occurrence of the event.
        
        *Returns:* A Python list containing the updated trace record.
        
        """
        if self.trace_fields is not None:
            for key, value in self.trace_fields.items():
                trace_record[key] = value
        
        # If the event object is reused, object will keep list of all
        # of it's trace records.        
        self._trace_records.insert(0, trace_record)
        return trace_record
    
    def _reset(self):
        """Resets the event to it's initial state.
        
        Internal Method. The ``reset`` method is called by the
        `Simulation` class's ``reset`` method. It deletes all
        trace_records from the event.
        """
        self._trace_records = []
    
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

        