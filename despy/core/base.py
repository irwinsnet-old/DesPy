#!/usr/bin/env python3
from itertools import count

PRIORITY_EARLY = -1
PRIORITY_STANDARD = 0
PRIORITY_LATE = 1

# TODO: Do something with the descriptions."

class _NamedObject(object):
    def __init__(self, name):
        self._name = name
    
    """Provides name and description properties to multiple despy
    classes.
    """
    @property
    def name(self):
        """Gets the name of the model.
        
        *Returns:* string
        
        """
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
    @property
    def description(self):
        """Gets a description of the model.
        
        *Returns:* A string that describes the purpose and components
        of the model. The description will be printed in simulation
        output reports.
        
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of the model.
        
        *Arguments*
            modelDescription (string):
                One or more paragraphs that describe the purpose and
                components of the model.
        """
        self._description = description
    
    def __str__(self):
        return self.name

class _ModelComponent(_NamedObject):
    def __init__(self, model, name):
        super().__init__(name)
        self._model = model
        model.add_component(self)
        
        if not hasattr(self, "count"):
            self.set_counter()
        self.number = self.get_id()
    
    @property
    def model(self):
        """ Get the entity's model.
        
        *Returns:* despy.model
        """
        return self._model
    
    @model.setter
    def model(self, model):
        self._model = model
    
    @classmethod
    def set_counter(cls):
        cls.count = count(1)
    
    @classmethod
    def get_id(cls):
        return next(cls.count)
    
    def __str__(self):
        return "{0}:{1} # {2}".format(self.model, self.name, self.get_id())