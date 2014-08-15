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

#TODO: Test run() with 'until' set.
#TODO: Fully implement event trace. Use tuple instead of string as output.
#TODO: Figure out callback self issue.
#TODO: Make event ID an event attribute (removed from named tuple)
#TODO: Decide how DoInitialEvents method will be used.
#TODO: Move Environment class to separate module.

from collections import namedtuple
from despy.environment import Environment
from despy.root import _NamedObject, _ModelMember

class Model(_NamedObject):

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
        
        # Create a default environment if no environment is provided
        # to the constructor.
        if environment == None:
            env = Environment()
            env.name = "Default Environment"
            self._environment = env
        else:
            self._environment = environment

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

class Entity(_ModelMember):
    """Represents an item that is part of the model.
    """
    def __init__(self, model, entityName, entityNumber = None):
        """Creates an Entity object.
        
        *Arguments*
            model (despy.Model):
                The model object that contains the entity.
            entityName (string):
                The name of the entity.
            entityNumber (integer):
                An integer that distinguishes the entity from other
                entities. Defaults to None.
            model
        """
        self._name = entityName
        self._number = entityNumber
        self._model = model

    @property
    def number(self):
        """ Get the number of the entity.
        
        *Returns:* Integer
        """
        return self._number

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
