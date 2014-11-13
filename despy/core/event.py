#!/usr/bin/env python3

import types
from despy.core.base import Component

class Event(Component):
    """ An base class for all events that can be scheduled on the future event
    list (FEL).

    Create an event by inheriting from the Event class. Subclasses of Event
    must instantiate one or more of the doPriorEvent(), do_event(), or
    doPostEvent() methods. The Simulation will execute these methods when the
    Event time occurs and the Event object is removed from the FEL.
    
    *Arguments*
        model (despy.Model):
            The model that the event is assigned to.
        name (string):
            A short name that describes the event. The event name is
            printed in simulation reports.
        priority (integer):
            When there are events scheduled to occurr at the same
            time, the priority determines if the simulation
            executes some events before other events.
            PRIORITY_EARLY events are executed before all other events
            with that are PRIORITY STANDARD or PRIORITY_LATE.
            PRIORITY_LATE events are executed after all other events
            that are PRIORITY_EARLY or PRIORITY_STANDARD. Defaults to
            PRIORITY_STANDARD.
    """

    def __init__(self, model, name, trace_fields = None):
        """Initialize the Event object.

        *Arguments*
            model (despy.Model):
                The Model that the event belongs to.
            name (string):
                A short string describing the event. The name will be
                printed in the event trace report.
            trace_fields (collections.OrderedDict)
                An ordered dictionary of fields that will be added to the
                trace record for this event.
        """

        super().__init__(model, name)
        self._description = "Event"
        self._callbacks = []
        self.trace_fields = trace_fields
        self.trace_records = []

    @property
    def priority(self):
        """Gets the priority of the event.
        
        *Returns:* An integer representing the priority of the event.
            * PRIORITY_EARLY = -1
            * PRIORITY_STANDARD = 0
            * PRIORITY_LATE = 1
        """
        return self._priority
    
    def append_callback(self, callback):
        """Appends a function to the event's callback list.
        
        The function will be called when the event is removed from the
        FEL and executed.
        
        *Arguments*
            callback (function):
                A variable that represents a class method or function.
        
        """
        self._callbacks.append(callback)

    def do_event(self):
        """Executes the callback functions that are on the event's
        callback list. _do_event() is called by the simulation's step
        method.
        
        """
        if len(self._callbacks)==0:
            return None
        else:
            for callback in self._callbacks:
                if isinstance(callback, types.FunctionType):
                    callback(self)
                elif isinstance(callback, types.MethodType):
                    callback()

            return True
        
    def append_trace_record(self, trace_record):
        self.trace_records.append(trace_record)
    
    def update_trace_record(self, trace_record):
        try:
            for key, value in self.trace_fields.items():
                trace_record[key] = value
            self.trace_records.insert(0, trace_record)
        except (TypeError, AttributeError):
            pass # Catches error if self.trace_fields is None.
        except ValueError as err:
            print(err)
            raise
        self.append_trace_record(trace_record)
        return self.trace_records
    
    def reset(self):
        self.trace_records = []
    
    def __lt__(self, y):
        return self.id < y.id
    
    def __gt__(self, y):
        return self.id > y.id
        