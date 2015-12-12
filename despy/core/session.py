#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
******************
despy.core.session
******************

..  autosummary::

    Session   
"""

from despy.output.results import Config

class Session:
    class __Session:
        def __init__(self):
            self._sim = None
            self.model = None
            self._ouput_config = Config()
            
        @property
        def sim(self):
            return self._sim
        
        @sim.setter
        def sim(self, sim):
            self._sim = sim
            
        @property
        def model(self):
            return self._model
        
        @model.setter
        def model(self, model):
            self._model = model
            
        @property
        def out(self):
            return self._ouput_config
        
        @out.setter
        def out(self, config):
            self._output_config = config
    
    _instance = None
    
    def __init__(self):
        if Session._instance is None:          
            Session._instance = Session.__Session()
    
    def __getattr__(self, name):
        return getattr(self._instance, name)
    
    def __setattr__(self, name, value):
        setattr(self._instance, name, value)