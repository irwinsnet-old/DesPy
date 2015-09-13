#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
from test.test_smtplib import sim_auth
"""
********************
despy.core.component
********************

..  autosummary::

    Component
    
..  todo

    Rename model attribute to "mod" because it's used so often.
    
    
"""
from itertools import count

from despy.base.named_object import NamedObject
from despy.core.model import Model

class Component(NamedObject):
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
    
    
    **Members**

    ..  autosummary::
        
        mod
        sim
        number
        id
        initialize
        finalize
        get_data
        __str__
        set_counter
        _get_next_number
        
    
    **Inherits**
        * :class:`despy.base.named_object.NamedObject`
        
    **Superclass**
        * :class:`despy.core.entity.Entity`
        * :class:`despy.core.event.Event`
        * :class:`despy.core.process.Process`
        * :class:`despy.core.queue.Queue`
        * :class:`despy.core.resource.Resource`
    """
    
    
    def __init__(self, model, name, description = None):
        """Creates an instance of a *Component* object.
        
        Except for the simulation and model classes, all members of the
        despy.core package inherit from the *Component* class.
        
        *Arguments*
            ``model`` (:class:`despy.core.model.Model`)
                The model that represents the system that the component
                belongs to.
            ``name`` (String)
                A descriptive short name that will appear in the trace
                and output reports.
            ``description`` (String)
                A descriptive paragraph. Optional.
        
        *Raises*
            ``TypeError:`` if model is not an instance of
            :class:`despy.core.model.Model`
        """
        super().__init__(name, description)
        
        # Assigns an unused counter if this is the first component
        # instance.
        if not hasattr(self, "_count"):
            self.set_counter()
        self._number = self._get_next_number()

        if isinstance(model, Model):
            self._mod = model
            self.sim = model.sim
            model[self.id] = self
        else:
                raise TypeError("Object passed to model argument " +\
                    "must be instance of despy.core.model.Model")

        self._statistics = {}
        
    @property
    def sim(self):
        """A link to the model's simulation attribute.
        
        This read-only attribute is provided for convenience.
        
        *Returns:* :class:`despy.core.simulation.Simulation`
        """
        return self._sim
    
    @sim.setter
    def sim(self, sim):
        self._sim = sim
    
    @property
    def mod(self):
        """A link to the component's model object.
        
        This read-only attribute is set by the ``Model.__init__``
        method.
        
        *Returns* :class:`despy.core.model.Model`
        """
        return self._mod
    
    @property
    def number(self):
        """An integer that uniquely identifies the *Component* instance.
        
        This attribute is read only.
        
        *Returns* integer
        """
        return self._number
    
    @property
    def id(self):
        """A string that uniquely identifies the component instance.
        
        The id attribute is of the format
        "<model.slug>.<component.slug>.<component._number>". The
        :meth:`.slug` attribute is inherited from
        :class:`despy.base.named_object.NamedObject`. The slug is the
        name attribute with spaces and characters that are not allowed
        in Windows replaced by underscores. The *id* attribute is
        suitable for creating file names.
        """
        return "{0}.{1}.{2}".format(self.mod.slug, self.slug,
                                    self._number)
    
    def add_stat(self, key, stat):
        self._statistics[key] = stat
        
    def get_stat(self, key):
        return self._statistics[key]
    
    @property
    def statistics(self):
        return self._statistics
    
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
        """A private method called from the *__init__()* method that
        gets the next unused _number.
        
        *Returns* integer
        """
        return next(cls._count)
    
    def __str__(self):
        """Returns a string that uniquely identifies every *Component*
        instance.
        
        The format of the return value is
        <model.name>:<component.name>#<component._number>
        
        *Returns* str
        """
        return "{0}:{1}#{2}".format(self.mod, self.name, self._number)
    
    def dp_initialize(self):
        self.initialize()
        
    def initialize(self):
        """Subclasses should override this method with initialization
        code that will be executed prior to any events on the future
        event list (FEL).
        """
        pass
    
    def finalize(self):
        pass
    
    def dp_finalize(self):
        """The Simulation calls finalize methods after final event.
        """
        for _ , stat in self.statistics.items():
            stat.finalize()
    
    def get_data(self):
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
        :class:`despy.core.queue.Queue` class: ::
        
          output = [(Datatype.title, "Queue Results: {0}".format(self.name)),
                     (Datatype.paragraph, self.description.__str__()),
                     (Datatype.param_list,
                        [('Maximum Time in Queue', np.amax(qtimes)),
                         ('Minimum Time in Queue', np.amin(qtimes)),
                         ('Mean Time in Queue', np.mean(qtimes))]),
                     (Datatype.image, qtime_filename)]
        """
        return None
