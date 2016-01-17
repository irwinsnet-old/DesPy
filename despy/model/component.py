#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*********************
despy.model.component
*********************

..  autosummary::

    Component
    
..  todo

    Create a new class for transient objects (entities and events) to
    inherit from.
    
    Add reset() method to model to reset model to initial condition.
    
    Rewrite counter logic so subclasses automatically get their own number
    sequence without calling set_counter().
    
"""

from itertools import count
import types

from despy.session import Session
from despy.model.abstract import AbstractModel

class Component(AbstractModel):
    """A base class that provides object counters and other attributes.

    Models consist of several components, such as queues, processes, and
    entities. Components generally represent an element of the system
    that is being simulated.  The ``Component`` class is the base class
    for the model's components. It maintains a counter, which uniquely
    identifies components, and has attributes for accessing the model
    and simulation objects. Users can create their own model elements by
    inheriting from the Component class.
    
    Subclasses should include a call to the :meth:`Component.__init()__`
    method in the subclass's ``__init__`` method.
    
    
    **Properties**

    ..  autosummary::
        
        name
        description
        session
        sim
        model
        owner
        number
        id
        statistics
        components
        
    **Public Methods**
    
    ..  autosummary::
    
        add_component
        set_counter
        initialize
        setup
        teardown
        finalize
        get_data
        
    **Magic Methods**
    
    ..  autosummary::
    
        __iter__
        __str__
        
    **Private and Internal Methods**
    
    ..  autosummary::
    
        _get_next_number
        _call_phase
        dp_initialize
        dp_setup
        dp_teardown
        dp_finalize
        
    **Superclass**
        * :class:`despy.model.entity.Entity`
        * :class:`despy.model.event.Event`
        * :class:`despy.model.process.Process`
        * :class:`despy.model.queue.Queue`
        * :class:`despy.model.resource.Resource`
    """
    
    
    def __init__(self, name, description = None):
        """Creates an instance of a *Component* object.
        
        *Arguments*
            ``name`` (String)
                A descriptive short name that will appear in the trace
                and output reports.
            ``description`` (String)
                A descriptive paragraph. Optional.
        """
        self.name = name
        self.description = description
        
        # Assigns an unused counter if this is the first component
        # instance.
        if not hasattr(self, "_count"):
            self.set_counter()
        self._number = self._get_next_number()

        self._components = {}
        self._statistics = {}

        self._owner = None
        self._session = Session()

    @property
    def name(self):
        """The name of the object. Must be valid Python identifier.
        
        A short phrase, such as "Customer" or "Server_Queue" that
        identifies the object.
        
        *Type:* String
        
        *Raises:*
            ``TypeError`` if set to a non-string.
            ``ValueError`` if string is not a valid Python identifier.
        
        """
        return self._name
    
    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("{} passed to name property. Component.name "
                            "requires a string that is a valid Python "
                            "identifier.".format(name.__class__))
        if not name.isidentifier():
            raise ValueError("'{}' passed to Component.name property is not "
                             "a valid Python identifier.".format(name))
        else:
            self._name = name

    @property
    def description(self):
        """Gets a description of the model.
        
        One or more paragraphs that describes the purpose and behavior
        of the object.  The description will be included in output
        reports.
        
        *Type:* string

        *Raises:* ``TypeError`` if set to type other than string or None.
        """
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, str) or description is None:
            self._description = description
        else:
            message = "{0} passed to name".format(description.__class__) + \
                    " argument. Should be a string or None."             
            raise TypeError(message)

    @property
    def session(self):
        """Returns the current Session object. Read-only.
        
        *Type:* :class:`despy.session.Session`
        """
        return self._session
    
    @property
    def sim(self):
        """Simulation object that is linked to the current session. Read-only.
        
        *Type:* :class:`despy.simulation.Simulation`
        """
        return self._session.sim
    
    @property
    def model(self):
        """Top component in model tree.
        
        *Type:* :class: `despy.model.component.Component`
        """
        cpt = self
        while cpt.owner is not None:
            cpt = self.owner
        return cpt

    @property
    def owner(self):
        """Link to the component's owner (i.e., parent in model tree structure).
        
        *Type* :class:`despy.model.component.Component`
        """
        return self._owner
    
    @owner.setter
    def owner(self, owner):
        self._owner = owner
            
    @property
    def number(self):
        """Integer that uniquely identifies the *Component* instance. Read-only.
        
        *Returns* integer
        """
        return self._number

    @property
    def id(self):
        """String that uniquely identifies the component instance. Read-only.
        
        The id property contains "<component.name>.<component._number>". The id
        attribute is suitable for creating unique file names.
        """
        return "{0}.{1}".format(self.name, self._number)
    
    @property
    def statistics(self):
        """Dictionary of component statistics.
        
        *Type:* {:class:`despy.output.statistic`}
        """
        return self._statistics
    
    @property
    def components(self):
        """Dictionary of child components that comprise a model.
        
        *Type:* {:class:`despy.model.component.Component`}
        """
        return self._components
    
    def add_component(self, item):
        """ Assign a component to the model.
        
        *Arguments*
            ``item`` (:class:`despy.model.component.Component`)
                An instance of ``Component`` or one of it's sub-classes.
        """
        if not hasattr(self, item.name):
            self._components[item.name] = item
            item.owner = self
            setattr(self, item.name, item)
        else:
            raise ValueError("Invalid key. Key must be a valid "
                             "Python identifier and cannot be the "
                             "same as an existing attribute or "
                             "reserved keyword.")
            
    def __iter__(self):
        """Enable post-order, depth-first iteration of Component tree.
        """
        for _, child in self.components.items():
            for component in child:
                yield component
        yield self

    def __str__(self):
        """Returns a string that uniquely identifies every *Component*
        instance.
        
        The format of the return value is
        <component.name>#<component._number>
        
        *Returns* string
        """
        return "{0}:{1}".format(self.name, self._number)

    @classmethod
    def set_counter(cls):
        """A class method that resets the *Component's* or subclass's
        _number counter back to 1.
        
        By default, the *Component* class and all subclasses of
        *Component* use the same static _number counter. For example,
        the first *Component* to be instantiated is _number 1, regardless
        of whether it's type *Component* or a subclass like *Event* or
        *Queue*. The __init__ method assigns _number 2 to the second
        instantiated *Component* or subclass, regardless of type, and
        so on.
        
        The simulation designer can assign a separate static counter
        object to a subclass of *Component* by calling the static
        method *set_counter()* on a subclass. The subclass's _number
        attributes will be the unbroken sequence 1, 2, 3, ...
        """
        cls._count = count(1)
    
    @classmethod
    def _get_next_number(cls):
        """Called by the *__init__()* method to get the next unused _number.
        
        *Returns* integer
        """
        return next(cls._count)
                
    def dp_initialize(self):
        """Internal despy method for initializing the model. Do not override.
        """
        init_cpts = []
        for cpt in self:
            cpt._call_phase(cpt.initialize)
            init_cpts.append(cpt.name)
        return init_cpts
    
    def initialize(self):
        """Initialization code that will run once, prior to any replications.
        """
        pass
    
    def dp_setup(self):
        """Internal despy method that sets up each replication. Do not override.
        """
        for cpt in self:
            for _, stat in cpt.statistics.items():
                stat.setup()
            cpt._call_phase(cpt.setup)
            
    def setup(self):
        """Runs prior to every replication to set up initial conditions.
        """
        pass

    def dp_teardown(self, time):
        """Internal despy method that runs after every rep. Do not override.
        """
        for cpt in self:
            for _, stat in cpt.statistics.items():
                stat.teardown(time)
            cpt._call_phase(cpt.teardown)
    
    def teardown(self):
        """Runs after every replication to clean up.
        """
        pass
    
    def dp_finalize(self):
        """Internal depsy method for finalizing the model. Do not override.
        """
        for cpt in self:
            cpt._call_phase(cpt.finalize)
            for _, stat in cpt.statistics.items():
                stat.finalize()
        
    def finalize(self):
        """Runs once, after all reps are complete, to finalize component.
        """
        pass
    
    def _call_phase(self, phase):
        """Allows using either method or function type objects as despy phases.
        """
        if isinstance(phase, types.FunctionType):
            phase(self)
        else:
            phase()
    
    def get_data(self, full_path):
        """Subclasses should override this method to provide simulation
        output that will be included in the output report.
        
        The output is a Python list of two-element tuples. The first
        element of each tuple is a :class:`despy.output.report.DataType`
        enumeration that determines how the rest of the tuple will be
        presented in the output report:

          * *Datatype.title:* The first element is the *Datatype.title
            enumeration* value and the second element is a string that
            will be displayed as a heading element in the html output
            report, or equivalent formatting for other output report
            formats.
          * *Datatype.paragraph:* The first element is the
            *Datatype.paragraph* enumaration value and the second
            element is a string that will be displayed as a paragraph
            element in the html output report, or equivalent formatting
            for other output report formats.
          * *Datatype.param_list:* The first element is the
            *Datatype.param_list enumeration value and the second
            element is a list with one or more two-element sub-tuples.
            The first element of the sub-tuples is a string caption
            describing the parameter, and the second element is the
            parameter. The *Datatype.param_list* will be displayed in
            the output report as a list of parameters with descriptive
            captions.
          * *Datatype.image:* The first element is the *Datatype.image*
            enumeration value and the second element is the image
            filename. The image will be displayed in the output report.
            
        The order of the datatypes in the output report will be the
        same as the order in the Python list that is returned from this
        method. Here is an example of the output from the
        :class:`despy.model.queue.Queue` class: ::
        
          output = [(Datatype.title, "Queue Results: {0}".format(self.name)),
                     (Datatype.paragraph, self.description.__str__()),
                     (Datatype.param_list,
                        [('Maximum Time in Queue', np.amax(qtimes)),
                         ('Minimum Time in Queue', np.amin(qtimes)),
                         ('Mean Time in Queue', np.mean(qtimes))]),
                     (Datatype.image, qtime_filename)]
        """
        return None
