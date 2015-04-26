#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
..  module:: despy.core.component

:class:`.component`
    A portion of a Despy model. Components represent an element of the
    system that is being simulated.
"""
from itertools import count

from despy.base.named_object import NamedObject
from despy.base.named_object_types import is_model

class Component(NamedObject):
    """A base class that provides object counters and other attributes.

    Models consist of several components, such as queues, processes, and
    entities. Components generally represent an element of the system
    that is being simulated.  The `Component` class is the base class
    for the model's components. It maintains a counter, which uniquely
    identifies components, and has attributes for access the model and
    simulation objects. Users can create their own model elements by
    inheriting from the Component class.
    
    Subclasses should include a call to the :meth:`.__init()__``
    method in the subclass :meth:`__init__` method.
    
    **Attributes**

      * :attr:`.model`: The :class:`despy.core.model.Model` object that
        the component belongs to.
      * :attr:`.sim`: The :class:`despy.core.simulation.Simulation` 
        object that the component's model belongs to.
      * :attr:`.number`: A unique integer that is assigned to each
        instance of a component.  The first component instantiated by
        the model will be assigned number 1, followed by number 2 for
        the next component, and so on.
      * :attr:`.id`: A string that uniquely identifies the component
        instance.

    **Methods**
      * :meth:`.initialize`: Subclasses should override this method to
        initialize the component prior to running the simulation.
      * :meth:`.finalize`: Subclasses should override this method to
        delete unneeded objects or execute other post-simulation code.
      * :meth:`.get_data`: Subclasses should override this method to
        provide output data to the simulation report.
      * :meth:`__str__`: Returns a string that uniquely identifies the
        component.
      * :meth:`.set_counter`: A class method that resets the internal
        number counter to 1.
      * :meth:`._get_next_number`: A private class method that gets the
        next unused number from the number counter.
    
    **Inherits**
        * :class:`despy.core.base.NamedObject`
        
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
        
        **Arguments**
          * *model:* The model that contains the component. Required.
            Type: :class:`despy.core.model.Model`
          * *name:* The str that will be assigned to the component's
            name attribute (inherited from
            :class:`despy.base.named_object.NamedObject`). Required.
            Type: str.
          * *description:* The str that will be assigned to the
            component's description attribute (inherited from
            :class:`despy.base.named_object.NamedObject`). Required.
            Type: str.
        
        **Raises**
            *TypeError:* if name is not a string, or if
            model is not a :class:`despy.core.model.Model`
        """
        super().__init__(name, description)
        
        if is_model(model):
            self._model = model
        else:
            message = "{0} passed to model ".format(model.__class__) + \
                    "argument. Should be a despy.core.model.Model " + \
                    "or subclass"
            raise TypeError(message)
        self._sim = model.sim
        
        # Assigns an unused counter if this is the first component
        # instance.
        if not hasattr(self, "_count"):
            self.set_counter()
        self._number = self._get_next_number()
        
        # Adds the component to the model's internal dictionary of
        # member components
        model[self.id] = self
    
    @property
    def sim(self):
        """A link to the model's simulation attribute.
        
        This read-only attribute is provided for convenience.
        
        *Returns:* :class:`despy.core.simulation.Simulation`
        """
        return self._sim
    
    @property
    def model(self):
        """A link to the component's model object.
        
        This read-only attribute is set by the :meth:`.__init__`
        method.
        
        *Returns* :class:`despy.core.model.Model`
        """
        return self._model
    
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
        "<model.slug>.<component.slug>.<component.number>". The
        :meth:`.slug` attribute is inherited from
        :class:`despy.base.named_object.NamedObject`. The slug is the
        name attribute with spaces and characters that are not allowed
        in Windows replaced by underscores. The *id* attribute is
        suitable for creating file names.
        """
        return "{0}.{1}.{2}".format(self.model.slug, self.slug, self.number)
    
    @classmethod
    def set_counter(cls):
        """A class method that resets the *Component's* or subclass's
        number counter back to 1.
        
        By default, the *Component* class and all subclasses of
        *Component* use the same static number counter. For example,
        the first *Component* to be instantiated is number 1, regardless
        of whether it's type *Component* or a subclass like *Event* or
        *Queue*. The __init__ method assigns number 2 to the second
        instantiated *Component* or subclass, regardless of type, and
        so on.
        
        The simulation designer can assign a separate static counter
        object to a subclass of *Component* by calling the static
        method *set_counter()* on a subclass. The subclass's number
        attributes will be the unbroken sequence 1, 2, 3, ...
        """
        cls._count = count(1)
    
    @classmethod
    def _get_next_number(cls):
        """A private method called from the *__init__()* method that
        gets the next unused number.
        
        *Returns* integer
        """
        return next(cls._count)
    
    def __str__(self):
        """Returns a string that uniquely identifies every *Component*
        instance.
        
        The format of the return value is
        <model.name>:<component.name>#<component.number>
        
        *Returns* str
        """
        return "{0}:{1}#{2}".format(self.model, self.name, self.number)
    
    def initialize(self):
        """Subclasses should override this method with initialization
        code that will be executed prior to any events on the future
        event list (FEL).
        """
        pass
    
    def finalize(self):
        """Subclasses should override this method with cleanup or other
        code that will be executed after all events on the FEL.
        """
        pass
    
    def get_data(self, folder):
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
