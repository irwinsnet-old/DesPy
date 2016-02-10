#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
********************
despy.abstract.model
********************

The Despy framework uses the abstract classes in this module for typ
checking.

..  autosummary::

    AbstractModel
    
..  todo
    
    Rename AbstractModel to AbstractComponent.
    
    
"""

from abc import ABCMeta, abstractmethod

class AbstractModel(metaclass = ABCMeta):
    """Model objects that are passed to a session or simulation
    object must be instances of AbstractModel. See
    :class:`despy.model.component` for detailed descriptions of each
    abstract method.
    """
    @property
    @abstractmethod
    def name(self):
        pass
    
    @name.setter
    @abstractmethod
    def name(self, name):
        pass

    @abstractmethod
    def dp_initialize(self):
        pass
    
    @abstractmethod
    def dp_setup(self):
        pass

    @abstractmethod
    def dp_teardown(self, time):
        pass
    
    @abstractmethod
    def dp_finalize(self):
        pass