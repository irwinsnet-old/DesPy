#!/usr/bin/env python3

from itertools import count
from despy.core.simulation import Simulation
from despy.core.base import _NamedObject, PRIORITY_STANDARD

class Model(_NamedObject):

    """Contains the logical elements of the simulation, such as
    servers, entities, processes, and queues.

    *Constructor Arguments*
        name (string):
            A short string that will be displayed in trace reports
            and other outputs.
        name (string):
            A short name for the model. The model name is displayed
            in output reports.
        simulation (despy.Simulation) (Optional):
            The model object must be attached to an simulation
            object, which will run the model's events on the FEL.
            If the simulation argument is omitted, the constructor
            will create and assign a default enviroment object to
            the model. A different simulation can be assigned later
            using the model object's simulation property.

    """

    def __init__(self, name, sim = None):
        """Create a model object."""
        self._name = name
        self.initial_events_scheduled = False
        self._components = []
        
        # Create a default simulation if no simulation is provided
        # to the constructor.
        if sim == None:
            exp = Simulation()
            exp.name = "{0} Default Simulation".format(name)
            self._sim = exp
        else:
            self._sim = sim
            
        #Create link to model in simulation object
        self._sim.append_model(self)
        self._initialize = None
        
    def add_component(self, component):
        self._components.append(component)

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
    def sim(self):
        """Gets the simulation object.
        
        *Returns:* (despby.Simulation)
        """
        return self._sim
    
    @sim.setter
    def sim(self, sim):
        """Assigns the model to a new simulation.
        
        *Arguments*
            simulation (despy.Simulation):
                An simulation object that will run the simulation
                and execute the model's events.
        
        """
        self._sim = sim
        
    def set_initialize_method(self, initialize_method):
        self._initialize = initialize_method

    def initialize(self):
        try:
            self._initialize(self)
        except:
            return
    
    def getCounter(self, start = 1):
        return count(start)

    def schedule(self, event, delay = 0,
                 priority = PRIORITY_STANDARD):
        """A convenience method that calls the Simulation object's
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
        self.sim.schedule(event, delay, priority)
