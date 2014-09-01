import types
from despy.core._root import _ModelMember

class Event(_ModelMember):
    """ An base class for all events that can be scheduled on the future event
    list (FEL).

    Create an event by inheriting from the Event class. Subclasses of Event
    must instantiate one or more of the doPriorEvent(), do_event(), or
    doPostEvent() methods. The Experiment will execute these methods when the
    Event time occurs and the Event object is removed from the FEL.
    
    *Arguments*
        model (despy.Model):
            The model that the event is assigned to.
        name (string):
            A short name that describes the event. The event name is
            printed in simulation reports.
        priority (integer):
            When there are events scheduled to occurr at the same
            time, the priority determines if the experiment
            executes some events before other events.
            PRIORITY_EARLY events are executed before all other events
            with that are PRIORITY STANDARD or PRIORITY_LATE.
            PRIORITY_LATE events are executed after all other events
            that are PRIORITY_EARLY or PRIORITY_STANDARD. Defaults to
            PRIORITY_STANDARD.
    """

    PRIORITY_EARLY = -1
    PRIORITY_STANDARD = 0
    PRIORITY_LATE = 1
    
    def __init__(self, model, name, priority = PRIORITY_STANDARD):
        """Initialize the Event object.

        *Arguments*
            model (despy.Model):
                The Model that the event belongs to.
            name (string):
                A short string describing the event. The name will be
                printed in the event trace report.
        """

        self._name = name
        self._model = model
        self._priority = priority
        self._description = "Event"
        self._callbacks = []
        self._id = model.experiment.get_unique_id()

    @property
    def priority(self):
        """Gets the priority of the event.
        
        *Returns:* An integer representing the priority of the event.
            * PRIORITY_EARLY = -1
            * PRIORITY_STANDARD = 0
            * PRIORITY_LATE = 1
        """
        return self._priority
    
    @property
    def id(self):
        """Get the unique integer that is appended to every event in the
        experiment.
        
        Every event must have a unique id value, or else the FEL will
        cause an error whenever two or more events are schedueled to
        occur at the same time.
        
        *Returns:* A unique integer.
        """
        return self._id

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
        callback list. _do_event() is called by the experiment's step
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

    def get_event_record(self, printToConsole = True):
        """ Append an experiment traceTuple object to the traceEvent
        List. Prints the contents if the traceTuple to the console
        output if printToConsole is set to True.
        
        *Arguments*
            printToConsole (Boolean):
                If set to true, in addition to returning a string,
                recordEvent() will send the string to the standard
                output (i.e., console). Defaults to True.
        
        """
        env = self.model.experiment
        eventRecord = env.traceTuple(time = env.now, evt_name = self.name)
        return eventRecord
    
    def __lt__(self, y):
        return self.id < y.id
    
    def __gt__(self, y):
        return self.id > y.id
        