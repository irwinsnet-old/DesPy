#!/usr/bin/env python3

from collections import namedtuple
from despy.core.experiment import Experiment, FelItem
from despy.core.root import _NamedObject, _ModelMember,\
    PRIORITY_EARLY, PRIORITY_STANDARD, PRIORITY_LATE

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
        experiment (despy.Experiment) (Optional):
            The model object must be attached to an experiment
            object, which will run the model's events on the FEL.
            If the experiment argument is omitted, the constructor
            will create and assign a default enviroment object to
            the model. A different experiment can be assigned later
            using the model object's experiment property.

    """

    def __init__(self, modelName, experiment = None):
        """Create a model object."""
        self._name = modelName
        self.initial_events_scheduled = False
        
        # Create a default experiment if no experiment is provided
        # to the constructor.
        if experiment == None:
            exp = Experiment()
            exp.name = "Default Experiment"
            self._experiment = exp
        else:
            self._experiment = experiment
            
        #Create link to model in experiment object
        self._experiment.append_model(self)
        self._initialize = None

    @property
    def initial_events_scheduled(self):
        """Return True of the model's initialize method has
        been executed.
        
        *Returns:* (Boolean)
        """
        return self._initial_events_scheduled
    
    @initial_events_scheduled.setter
    def initial_events_scheduled(self, scheduled):
        """Set to True if the model's initialize method has been
        run.
        
        *Arguments*
            schedule (Boolean):
                Set to True if the model's initialize method has
                been run.
        """
        self._initial_events_scheduled = scheduled
    
    @property
    def experiment(self):
        """Gets the experiment object.
        
        *Returns:* (despby.Experiment)
        """
        return self._experiment
    
    @experiment.setter
    def experiment(self, experiment):
        """Assigns the model to a new experiment.
        
        *Arguments*
            experiment (despy.Experiment):
                An experiment object that will run the simulation
                and execute the model's events.
        
        """
        self._experiment = experiment
        
    def set_initialize_method(self, initialize_method):
        self._initialize = initialize_method

    def initialize(self):
        """Place initial events on the FEL and initiate processes.

        Model subclasses must implement this method, or the Model
        class will raise a NotImplementedError.
        """
        try:
            self._initialize(self)
        except:
            return

    def schedule(self, event, delay = None,
                 priority = PRIORITY_STANDARD):
        """A convenience method that calls the Experiment object's
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
        self.experiment.schedule(event, delay, priority)

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