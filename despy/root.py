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
    
    @property
    def description(self):
        """Gets a description of the model.
        
        *Returns:* A string that describes the purpose and components
        of the model. The description will be printed in simulation
        output reports.
        
        """
        return self._description

    @description.setter
    def description(self, modelDescription):
        """Sets the description of the model.
        
        *Arguments*
            modelDescription (string):
                One or more paragraphs that describe the purpose and
                components of the model.
        """
        self._description = modelDescription

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