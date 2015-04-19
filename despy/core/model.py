#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
..  module:: despy.core.model

**Model**
    * :class:`despy.core.Model.model`: The model represents the 
      real-world system that is being simulated. The user will generally
      build their model by sub-classing the `model` class.
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

    **Attributes**
      * :attr:`.name`: Model object's name. Inherited from
        :class:`despy.base.named_object.NamedObject`. Type: `string`.
      * :attr:`.description`: One or more paragraphs that describes the
        Model. Inherited from
        :class:`despy.base.named_object.NamedObject` Type: `string`.
      * :attr:`.initial_events_scheduled`: Returns `False` if the model
        and it's components have not yet been initialized. Otherwise
        returns true.
      * :attr:`.sim`: The corresponding instance of the
        :class:`despy.core.simulation.Simulation` class.
        
    **Methods**
      * :meth:`.__set_item__`: This Python magic method allows users to
        add components to the model using dictionary (i.e., '[]')
        notation.
      * :meth:`.__get_item__`: This Python magic method allows users to
        access model components using dictionary notation.
      * :meth:`.delete_component`: Remove a component from the model.
      * :meth:`.set_initialize_method` Set the model's initialize
        method to a function provided as a method argument.
        Not used if user includes a custom initialize method in a model
        subclass.
      * :meth:`.initialize`: The default initialize method. Calls the
        initialize method on all model components.
      * :meth:`.schedule`: A convenience method. Calls the
        :class:`despy.core.simulation.Simulation` class's `schedule`
        method.
        
    **Inherits**
      * :class:`despy.core.base.NamedObject`

    """

    def __init__(self, name, sim = None, description = None):
        """Create a model object.
        
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
        self.gen = self.sim.gen
        self.trace = self.sim.gen.trace

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
  
    def __setitem__(self, key, item):
        self.components[key] = item

    def __getitem__(self, key):
        return self.components[key]
        
    def delete_component(self, key):
        del self.components[key]
        
    def set_initialize_method(self, initialize_method):
        self._initialize = initialize_method

    def initialize(self):
        for _, component in self.components.items():
            component.initialize()
        
        try:
            self._initialize(self)
        except:
            return

    def schedule(self, event, delay = 0,
                 priority = fi.PRIORITY_STANDARD):
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
