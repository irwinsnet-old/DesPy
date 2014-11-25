from itertools import count

from despy.core.named_object import NamedObject
from despy.core.types import is_model

class Component(NamedObject):
    """A base class that provides object counters and other attributes.
    
    A component is a portion of a Despy model.  Components generally
    represent an element of the system that is being simulated.  Several
    Despy classes (e.g., Entity, Resource, Progress, Queue, Event)
    inherit from the Component class. Users can create their own model
    elements by inheriting from the Component class.
    
    Subclasses should include a call to the ``Component.__init()__``
    method in the subclass ``__init()__`` method.
    
    **Attributes**
      * :attr:`.model`: The :class:`despy.core.model.Model object that
        the component belongs to.
      * :attr:`sim`: The :class:`despy.core.simulation.Simulation 
        object that the component's model belongs to.


    **Methods**
    
    **Inherits**
        :class:`despy.core.base.NamedObject`
        
    **Superclass**
        :class:`despy.core.entity.Entity`
        :class:`despy.core.event.Event`
        :class:`despy.core.process.Process`
        :class:`despy.core.queue.Queue`
        :class:`despy.core.resource.Resource`
    
    """
    
    
    def __init__(self, model, name):
        super().__init__(name)
        
        if is_model(model):
            self._model = model
        else:
            message = "{0} passed to model ".format(model.__class__) + \
                    "argument. Should be a despy.core.model.Model " + \
                    "or subclass"
            raise TypeError(message)
        
        self._sim = model.sim
        
        if not hasattr(self, "count"):
            self.set_counter()
        self.number = self.get_next_number()
        
        model[self.id] = self
    
    @property
    def sim(self):
        return self._sim
    
    @property
    def model(self):
        return self._model
    
    @classmethod
    def set_counter(cls):
        cls.count = count(1)
    
    @classmethod
    def get_next_number(cls):
        return next(cls.count)
    
    def __str__(self):
        return "{0}:{1}#{2}".format(self.model, self.name, self.number)
    
    @property
    def id(self):
        return "{0}.{1}.{2}".format(self.model.slug, self.slug, self.number)
    
    def initialize(self):
        pass
    
    def finalize(self):
        pass
    
    def get_output(self, folder):
        return None
