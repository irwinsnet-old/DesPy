#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2014, Stacy Irwin

"""
..  module:: despy.base.named_object

Base classes for other Despy classes.

**NamedObject**
    Inherited directly or indirectly by all Despy classes.
    :class:`.NamedObject` provides a name attribute, a description
    attribute, and other helper methods.

**Component**
    A portion of a Despy model. Components generally represent an
    element of the system that is being simulated.
    
**Priority Constants**
    The despy.base package includes three constants that are used to
    prioritize events that are scheduled to occur a the same time.
    Events assigned a higher priority will occur before events that are
    assigned lower priorities.
    
    *PRIORITY_STANDARD*
        Despy uses PRIORITY_STANDARD as the default priority when no
        other priority is specified.
        
    *PRIORITY_EARLY*
        Events assigned PRIORITY_EARLY will be executed before
        PRIORITY_STANDARD and PRIORITY_LATE events.
        
    *PRIORITY_LATE*
        Events assigned PRIORITY_LATE will be executed after
        PRIORITY_EARLY and PRIORITY_STANDARD events.
        
    Events scheduled to occur at the same time with the same priority
    may be executed in any order.
"""

import re

PRIORITY_EARLY = -1
PRIORITY_STANDARD = 0
PRIORITY_LATE = 1

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
      * :meth:`.__str__` Returns the name attribute.
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
        
    