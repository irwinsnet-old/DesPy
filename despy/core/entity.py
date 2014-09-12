from despy.core.root import _ModelMember
from itertools import count

class Entity(_ModelMember):
    
    def __init__(self, model, name):
        self._model = model
        self._name = name
        
        if not hasattr(self, "count"):
            self.set_counter()
        self.number = self.get_id()
    
    @classmethod
    def set_counter(cls):
        cls.count = count(1)
    
    @classmethod
    def get_id(cls):
        return next(cls.count)
    
