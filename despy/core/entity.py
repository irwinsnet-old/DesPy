from despy.core.root import _ModelMember

class Entity(_ModelMember):
    def __init__(self, model, name):
        self._model = model
        self._name = name