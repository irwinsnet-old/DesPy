from despy.core.root import _ModelMember
from despy.core import Event
from collections import namedtuple

ResourceUser = namedtuple('ResourceUser', ['item_fld', 'start_time_fld'])

class Resource(_ModelMember):
    def __init__(self, model, name, capacity):
        self._model = model
        self._name = name
        self.capacity = capacity
        self._positions = {index + 1: None for index in range(self.capacity)}
        self._queue = None
        self._activity_time = None
    
    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, queue):
        self._queue = queue
        
    @property
    def activity_time(self):
        return self._activity_time
    
    @activity_time.setter
    def activity_time(self, time_function):
        self._activity_time = time_function
    
    def get_empty_position(self):
        for index in range(self.capacity):
            if self._positions[index + 1] is None:
                return index + 1
        return False
    
    def __getitem__(self, index):
        return self._positions[index]
    
    def __setitem__(self, index, item):
        self._positions[index] = item
        
    def get_activity_time(self):
        if self.activity_time is None:
            raise NotImplementedError
        else:
            return self.activity_time()

    def request(self, user):
        index = self.get_empty_position()
        if index:
            resource_user = ResourceUser(item_fld = user,
                                start_time_fld = self.model.experiment.now)
            self._positions[index] = resource_user
            self.start_activity(resource_user)
            return index
        else:
            if self.queue is not None:
                self.queue.add(user)
            return False
    
    def start_activity(self, resource_user):
        self.model.experiment.trace.add_output("Trace: Starting activity")
        self.model.schedule(Event(self.model, "Finished Activity"),
                            self.get_activity_time())