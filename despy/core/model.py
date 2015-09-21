#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.core.model
****************

..  autosummary::

    Model
    
..  todo

    Refactor to use "_method_name" for callback methods and
    "method_name" for overridden names. With this structure, user won't
    have to remember when to call super().
"""
import types

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
        sim
        __setitem__
        __getitem__
        delete_component
        initialize
        schedule
        
    **Inherits**
      * :class:`despy.base.named_object.NamedObject`

    """

    def __init__(self, name, description = None):
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
        self._components = {}
        self._statistics = {}
        self._sim = None

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
        for _, component in self.components.items():
            component.sim = sim
            print("Set sim for {}".format(component.name))
        
    @property
    def components(self):
        return self._components
    
    @property
    def statistics(self):
        return self._statistics
  
    def __setitem__(self, key, item):
        """ Assign a component to the model using dictionary notation.
        
        *Arguments*
            ``key`` (String)
                The dictionary key that will be used to retrieve the
                component.
            ``item`` (:class:`despy.core.component.Component`)
                An instance of ``Component`` or one of it's sub-classes.
        """
        self._components[key] = item
        item.mod = self

    def __getitem__(self, key):
        """Access a component using a dictionary key.
        
        *Arguments*
            ``key`` (String)
                The dictionary key that will be used to retrieve the
                component.
            ``item`` (:class:`despy.core.component.Component`)
                An instance of ``Component`` or one of it's sub-classes.
        """
        return self._components[key]

    def initialize(self):
        pass
        
    def dp_initialize(self):
        """Initialize the model and all components.
        
        This default initialize method will first call all of the
        components' ``initialize`` methods, in no particular order.
        Next it will call Model.initialize().
        """
        if self.sim.is_rep_initialized():
            return

        for _, component in self.components.items():
            component.dp_initialize()
        
        if isinstance(self.initialize, types.FunctionType):
            self.initialize(self)
        else:
            self.initialize()
        
    def finalize(self):
        pass        
        
    def dp_finalize(self):
        for _, component in self.components.items():
            component.dp_finalize()

        self.finalize()

#     def schedule(self, event, delay = 0,
#                  priority = Priority.STANDARD):
#         """Call the Simulation object's schedule() method.
# 
#         *Arguments*
#             event (:class:`despy.core.event.Event`):
#                 The event that will be scheduled.
#             delay (integer):
#                 A non-negative integer that specifies how much time
#                 will elapse before the event will be scheduled. The
#                 delay plus the current time equals the absolute time
#                 that the event will occur.
# 
#         """
#         self._sim.schedule(event, delay, priority)