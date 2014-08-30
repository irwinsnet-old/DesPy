
PRIORITY_EARLY = -1
PRIORITY_STANDARD = 0
PRIORITY_LATE = 1

class _NamedObject(object):
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

class _ModelMember(_NamedObject):
    
    @property
    def model(self):
        """ Get the entity's model.
        
        *Returns:* despy.model
        """
        return self._model
    
    @model.setter
    def model(self, model):
        self._model = model