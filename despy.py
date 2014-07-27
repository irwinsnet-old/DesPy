#!/usr/bin/env python3
"""
Contains the core classes for the despy framework.

Classes:
--------

    * **Model**
        Represents the system that will be simulated.
        Contains entities, servers, proceses, queues and other
        components of the system.
    * **Environoment**
        The environment schedules events and
        maintains the future event list (FEL).
    * **Entity**
        An entity represents any component of the system,
        such as a customer, or vehicle.
    * **Process**
        A process represents a component of a system over
        it's entire lifecycle and periodically schedules events.
    * **Event**
        An event is an entity that can be placed on the FEL
        and represents some change that occurs in the system.
    * **NoEventsRemaining**
        An exception that is raised by the
        Environment object when no events remain on the FEL.

"""

#TODO: Implement run()

from heapq import heappush, heappop
from itertools import count
from collections import namedtuple

class Model(object):

    """Contains the logical elements of the simulation, such as
    servers, entities, processes, and queues.

    *Constructor Arguments*
        modelName (string):
            A short string that will be displayed in trace reports
            and other outputs.
        modelName (string):
            A short name for the model. The model name is displayed
            in output reports.
        environment (despy.Environment) (Optional):
            The model object must be attached to an environment
            object, which will run the model's events on the FEL.
            If the environment argument is omitted, the constructor
            will create and assign a default enviroment object to
            the model. A different environment can be assigned later
            using the model object's environment property.

    """

    def __init__(self, modelName, environment = None):
        """Create a model object."""
        self._name = modelName
        if environment == None:
            env = Environment()
            env.name = "Default Environment"
            self._environment = env
        else:
            self._environment = environment

    @property
    def name(self):
        """Gets the name of the model.
        
        *Returns:* string
        
        """
        return self._name

    @property
    def environment(self):
        """Gets the environment object.
        
        *Returns:* (despby.Environment)
        
        """
        return self._environment
    
    @environment.setter
    def environment(self, environment):
        """Assigns the model to a new environment.
        
        *Arguments*
            environment (despy.Environment):
                An environment object that will run the simulation
                and execute the model's events.
        
        """
        self._environment = environment
    
    @property
    def description(self):
        """Gets a description of the model.
        
        *Returns:* A string that describes the purpose and components
        of the model. The description will be printed in simulation
        output reports.
        
        """
        return self._description

    @description.setter
    def description(self, modelDescription):
        """Sets the description of the model.
        
        *Arguments*
            modelDescription (string):
                One or more paragraphs that describe the purpose and
                components of the model.


        """
        self._description = modelDescription

    def do_initial_events(self):
        """Place initial events on the FEL and initiate processes.

        Model subclasses must implement this method, or the Model
        class will raise a NotImplementedError.
        """
        raise NotImplementedError()

    def schedule(self, event, delay = 0):
        """A convenience method that calls the Environment object's
        schedule() method to schedule an event on the FEL.

        *Arguments*
            event (despby.Event):
                The event that will be scheduled.
            delay (integer):
                A non-negative integer that specifies how much time
                will elapse before the event will be scheduled. The
                delay plus the current time equals the absolute time
                that the event will occur.

        """
        self.environment.schedule(event, delay)

class Environment(object):

    """ Schedule events and manage the future event list (FEL).

    *Constructor Arguments*
        initial_time (integer):
            A non-negative integer that defaults to zero.

    """

    def __init__(self, initial_time = 0):
        """Initialize the event object.
        """
        self._now = initial_time * 10
        self._futureEventList = []
        #  Each event gets a unique integer ID, starting with 0 for the first
        #event.
        self._eventId = count()
        self._console_output = True
        self.felTuple = namedtuple('felTuple', ['time', 'id', 'evt'])

    @property
    def now(self):
        """The current time of the environment. The time is a unit-less
        integer."""
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10

    @property
    def name(self):
        """Gets the name of the environment.
        
        *Returns:* A short string.
        
        """
        return self._name

    @name.setter
    def name(self, environmentName):
        """Sets the name of the environment.
        
        *Arguments*
            modelName (string):
                A short string that describes the environment.

        """
        self._name = environmentName

    @property
    def console_output(self):
        return self._console_output
    
    @console_output.setter
    def console_output(self, output):
        self._console_output = output

    def schedule(self, event, delay = 0):
        """ Add an event to the FEL.

        *Arguments*
            event (despy.Event):
                An instance or subclass of the despy.Event class.
            delay (integer):
                A non-negative integer that defaults to zero, meaning
                the event will be scheduled to occur mmediately.

        """
        # Places a tuple onto the FEL, consisting of the event time, ID,
        # and event object.
        scheduleTime = self._now + (delay * 10) + event.priority
        
        
        heappush(self._futureEventList,
                 self.felTuple(time = scheduleTime, id = next(self._eventId),
                          evt = event))

    def peek(self):
        """Return the time of the next scheduled event, or infinity if there
        is no remaining events.
        """
        try:
            return int((self._futureEventList[0].time - \
                    self._futureEventList[0].evt.priority) / 10)
        except IndexError:
            return float('Infinity')

    def step(self):
        """Advance simulation time to the next time on the FEL and
        executes the next event.

        *Raises*
            NoEventsRemaining:
                Occurs if no more events are scheduled on the FEL.
        """

        # FEL items are tuples in format (eventTime, event ID, event)
        try:
            current_FEL_item = heappop(self._futureEventList)
        except IndexError:
            raise NoEventsRemaining
        else:
            self.now = int((current_FEL_item.time - \
                    current_FEL_item.evt.priority) / 10)

        #Run event
        current_FEL_item[2].doEvent()
        current_FEL_item[2].printEvent(not self.console_output)
        
        return current_FEL_item

    def run(self, until=None):
        """ Continue to advance simulation time and execute events on the FEL
        until there are no more events or until the time specified in the
        "until" parameter is reached.

        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. Defaults to 'None',
                meaining the simulation will run until there are no
                remaining events on the FEL.  The events at the time
                specified in 'until' will be executed. For example, if
                until = 100 and there are events scheduled at time
                100, those events will be executed, but events at time
                101 or later will not.
        """
        pass

class Entity:
    def __init__(self, entityName, entityNumber = None, model = None):
        self._name = entityName
        self._number = entityNumber
        self._model = model

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    @property
    def model(self):
        return self._model

class Process:
    """Represents a simulation process that periodically schedules events and
    maintains state (i.e., retains variable values) between events.
    """

    def __init__(self, processName = None, model = None):
        """Creates a process object.

        @param processName  A short string that will be displayed in trace
                            reports and other outputs. Default = None.
        @param model        A despy.Model object that contains the process
                            object.
        """
        self._name = processName
        self._model = model
        self.generator = self._generator()

    @property
    def name(self):
        """The name of the process."""
        return self._name

    @property
    def model(self):
        return self._model

    def scheduleProcessEvent(self, event, delay = 0):
        event.appendEventCallback(self.getNextEvent)
        self.model.schedule(event, delay)
        return True

    def getNextEvent(self):
        return next(self.generator)

    def resetProcess(self):
        self.generator = self._generator()

    def _generator(self):
        """Conduct the simulation and periodically yield events."""
        yield

class Event(object):
    """ An base class for all events that can be scheduled on the future event
    list (FEL).

    Create an event by inheriting from the Event class. Subclasses of Event
    must instantiate one or more of the doPriorEvent(), doEvent(), or
    doPostEvent() methods. The Environment will execute these methods when the
    Event time occurs and the Event object is removed from the FEL.
    
    *Arguments*
        model (despy.Model):
            The model that the event is assigned to.
        name (string):
            A short name that describes the event. The event name is
            printed in simulation reports.
        priority (integer):
            When there are events scheduled to occurr at the same
            time, the priority determines if the environment
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

        Arguments:
        model: The Model that the event belongs to.
        name: A short string describing the event. The name will be printed in
                the event trace report.
        """

        self._name = name
        self._model = model
        self._priority = priority
        self._description = "Event"
        self._callbacks = []

    @property
    def name(self):
        """Gets the name of the event.

        *Returns:* string

        """
        return self._name

    @name.setter
    def name(self, eventName):
        """Assigns a name to the event.
        
        The event name is printed in the trace report every time the event occurs.
        It should be less than 15 characters.
        
        *Arguments*
            eventName (string):
                The eventName should be short.
        """
        self._name = eventName

    @property
    def model(self):
        """ Gets the model that conatains the event.
        
        *Returns:* despy.Model object.
    
        """
        return self._model

    @property
    def description(self):
        """Gets the description of the event.
        
        The description explains what the event does and it's purpose.
        
        *Returns:* string
        
        """
        return self._description

    @description.setter
    def description(self, eventDescription):
        """Sets the event's description. The description is typically
        a short paragraph consisting of several sentences.
        
        *Arguments*
            eventDescription (string):
                A short paragraph that describes the purpose of the
                event and what it does.
        
        """
        self._description = eventDescription
        
    @property
    def priority(self):
        """Gets the priority of the event.
        
        *Returns:* An integer representing the priority of the event.
            * PRIORITY_EARLY = -1
            * PRIORITY_STANDARD = 0
            * PRIORITY_LATE = 1
        """
        return self._priority

    def appendcallback(self, callback):
        """Appends a function to the event's callback list.
        
        The function will be called when the event is removed from the
        FEL and executed.
        
        *Arguments*
            callback (function):
                A variable that represents a class method or function.
        
        """
        self._callbacks.append(callback)

    def doEvent(self):
        """Executes the callback functions that are on the event's
        callback list. _doEvent() is called by the environment's step
        method.
        
        """
        if len(self._callbacks)==0:
            return None
        else:
            for callback in self._callbacks:
                callback()
            return True

    def printEvent(self, returnString = False):
        """ Prints the time and name of the event or returns the time
        and event name as a string.
        
        *Arguments*
            returnString (Boolean):
                If set to true, printEvent will return the time and
                event name as a formatted string, instead of writing
                the data to the standard output (i.e., console).
        
        """
        output = str(self.model.environment.now).rjust(8) + ':   ' + self.name
        if returnString:
            return output
        else:
            print(str(output))

class NoEventsRemaining(Exception):
    pass


