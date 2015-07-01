#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.core.model
****************

:class:`despy.core.model.Model`: 
    The model represents the real-world system that is being simulated.
    The user will generally build their model by sub-classing the
    ``Model`` class.
"""

from despy.core.simulation import Simulation, FelItem as fi
from despy.base.named_object import NamedObject

class Model(NamedObject):
    """Represents the logical elements of the real-world system.
    
    Contains the simulation elements that represent the logical
    elements of the real-world system, such as servers, entities,
    processes, and queues.
    
    For simple simulations, users can add components to the model
    using dictionary notation and rely on the model's default behavior.
    For more complex simulations, users will most likely create their
    own model class by sub-classing this class.

    **Members**
    
    ..  autosummary::
    
        name
        description
        initial_events_scheduled
        sim
        __setitem__
        __getitem__
        delete_component
        set_initialize_method
        initialize
        schedule
        
    **Inherits**
      * :class:`despy.base.named_object.NamedObject`

    """

    def __init__(self, name, sim = None, description = None):
        """Create a Model object.
        
        *Arguments*
            ``name`` (string):
                A short name for the model. The model name is displayed
                in output reports.
            ``sim`` (:class:`despy.core.simulation.Simulation`)
                (Optional): The model object must be attached to a
                simulation object, which will manage events and the FEL.
                If the simulation argument is omitted, the constructor
                will create and assign a default environment object to
                the model. A different simulation can be assigned later
                using the model object's simulation property.
            ``description`` (string):
                A brief description generally consisting of a few
                sentences.
        """
        super().__init__(name, description)
        self.initial_events_scheduled = False
        self.components = {}
        
        # Create a default simulation if no simulation is provided
        # to the constructor.
        if sim == None:
            simulation = Simulation()
            simulation.name = "{0}:Default Simulation".format(name)
            self._sim = simulation
        else:
            self._sim = sim
            
        #Create link to model in simulation object
        self._sim.append_model(self)
        self._initialize = None
        
        # Convenience Attributes
        self.gen = self._sim.gen
        self.trace = self._sim.gen.trace

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
        
        *Returns:* (:class:`despy.core.simulation.Simulation`)
        """
        return self._sim
    
    @sim.setter
    def sim(self, sim):
        """Assigns the model to a new simulation.
        
        *Arguments*
            simulation (:class:`despy.core.simulation.Simulation`):
                A simulation object that will run the simulation
                and execute the model's events.
        """
        self._sim = sim
  
    def __setitem__(self, key, item):
        """ Assign a component to the model using dictionary notation.
        
        *Arguments*
            ``key`` (String)
                The dictionary key that will be used to retrieve the
                component.
            ``item`` (:class:`despy.core.component.Component`)
                An instance of ``Component`` or one of it's sub-classes.
        """
        self.components[key] = item

    def __getitem__(self, key):
        """Access a component using a dictionary key.
        
        *Arguments*
            ``key`` (String)
                The dictionary key that will be used to retrieve the
                component.
            ``item`` (:class:`despy.core.component.Component`)
                An instance of ``Component`` or one of it's sub-classes.
        """
        return self.components[key]
        
    def delete_component(self, key):
        """Remove a component from the model.
        
        *Arguments*
            ``key`` (String)
                The dictionary key that will be used to identify the
                component that will be removed from the model.
        """
        del self.components[key]
        
    def set_initialize_method(self, initialize_method):
        """Assign an initialize method to the model.
        
        The initialize method is run once, when the simulation is run,
        before any events are executed. Initialize methods are often
        used to add the first events to the FEL.
        
        Users can pass an initialize method to the model with this
        method, or they can override the ``_initialize`` method in a
        model subclass.
        
        *Arguments*
            ``initialize_method`` (function)
                A Python function that will initialize the model.
        """
        self._initialize = initialize_method

    def initialize(self):
        """Initialize the model and all components.
        
        This default initialize method will first call all of the
        components' ``initialize`` methods, in no particular order.
        Next it will call whatever method was passed to
        ``set_initialize_method``.
        """
        # Initialize components that are attached to the model.
        for _, component in self.components.items():
            component.initialize()
        
        # Call the method passed to self.set_initialize_method.
        try:
            self._initialize(self)
        except:
            return

    def schedule(self, event, delay = 0,
                 priority = fi.PRIORITY_STANDARD):
        """Call the Simulation object's schedule() method.

        *Arguments*
            event (:class:`despy.core.event.Event`):
                The event that will be scheduled.
            delay (integer):
                A non-negative integer that specifies how much time
                will elapse before the event will be scheduled. The
                delay plus the current time equals the absolute time
                that the event will occur.

        """
        self._sim.schedule(event, delay, priority)
