#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
..  module:: despy.base.named_object

A base class that provides name and description attributes to
subclasses.

**NamedObject**
    Inherited directly or indirectly by all Despy classes.
    :class:`.NamedObject` provides a name attribute, a description
    attribute, and other helper methods.
"""

import re

class NamedObject(object):
    """A base class that provides name and description fields.
    
    Subclasses should include a call to the
    :meth:`NamedObject.__init__` method in the subclass
    :meth:`__init__` method.
    
    **Attributes**
      * :attr:`.name`: Object name.
      * :attr:`.description`: One or more paragraphs that describes the
        object.
        
    **Methods**
      * :meth:`__str__` Returns the name attribute.
      * :meth:`.slug` Returns the name attribute, but replaces all
        characters that are not allowed in Windows file names with an
        underscore character.
      
    **Superclass**
      * :class:`despy.core.model.Model`
      * :class:`despy.core.simulation.Simulation`
    """
    
    
    def __init__(self, name, description = None):
        """Creates an instance of a NamedObject.
        
        All NamedObject instances and subclasses must have a name,
        therefore the constructor requires a name argument.
        
        **Arguments**
          * *name:* The value of the :attr:`.name` attribute. Required.
            Type: str.
          * *description:* The value of the :attr:`.description`
            attribute. Optional, default value is ``None``. Type: str.
          
        **Raises**
            *TypeError:* if name is not a string, or if
            description is neither a string or type ``None``.
        """
        self.name = name
        self.description = description

    @property
    def name(self):
        """The name of the object.
        
        A short phrase, such as "Customer" or "Server Queue" that
        identifies the object.  Using title case and spaces will result
        in pleasant formatting in output reports and trace files.
        
        *Returns:* str
        
        *Raises:*
            *TypeError* if name is not a string.
        
        """
        return self._name
    
    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self._name = name
        else:
            message = "{0} passed to name".format(name.__class__) + \
                    " argument. Should be a string."
            raise TypeError(message)    
    
    @property
    def description(self):
        """Gets a description of the model.
        
        One or more paragraphs that describes the purpose and behavior
        of the object.  The description will be included in output
        reports as html paragraphs (or equivalent for other output
        formats).
        
        *Returns:* str

        *Raises:* ``TypeError`` if description is not a string or type
        ``None``.
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

    def __str__(self):
        """Returns the name attribute.
        
        Unless overriden by the subclass, statements such as
        ``print(NamedObject_subclass)`` will display the name attribute.
        
        *Returns:* str
        """
        return self.name
    
    @property
    def slug(self):
        """Returns a modified version of the name attribute.
        
        Spaces and all characters not allowed in Windows filenames
        ([]<>\/\*?:\|#!") are replaced with underscores.
        
        *Returns:* str
        """
        return re.sub(r'[ <>/*?:|#!"\\]', '_', self._name)
        
    