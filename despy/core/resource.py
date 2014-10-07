#!/usr/bin/env python3

from despy.core.base import _ModelComponent
from despy.core import Event

# TODO: Add different options for selection of empty resources, either
# prioritization by number, random selection, or equal loading.

class Resource(_ModelComponent):
    
    class Position():
        def __init__(self, index):
            self.name = "#{0}".format(index)
            self.user = None
            self.start_time = None
            
    def __init__(self, model, name, capacity):
        super().__init__(model, name)
        self.capacity = capacity

        self._positions = {index: Resource.Position(index) \
                           for index in range(1, self.capacity + 1)}

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

    def get_activity_time(self):
        if self.activity_time is None:
            raise NotImplementedError
        else:
            return self.activity_time()
    
    def get_empty_position(self):
        for index in range(1, self.capacity + 1):
            if self[index].user is None:
                return index
        return False
    
    def __getitem__(self, index):
        return self._positions[index]
    
    def __setitem__(self, index, item):
        self._positions[index] = item

    def request(self, user):
        index = self.get_empty_position()
        if index:
            self[index].user = user
            self[index].start_time = self.model.sim.now
            self.start_activity(index)
            return index
        else:
            if self.queue is not None:
                self.queue.add(user)
            return False
        
    def start_activity(self, index):
        trace = "Position {0} ".format(self[index].name)
        trace += "starting activity on {0}.".format(self[index].user)
        self.model.sim.trace.add_output(trace)
        
        service_time = self.get_activity_time()

        finish_event = ResourceFinishActivityEvent(\
            self, "Finished Service", index, service_time)
        self.model.schedule(finish_event, service_time)
        
    def finish_activity(self, index, service_time):
        trace = "Position {0} finished Activity ".format(self[index].name)
        trace += "on {0}.  ".format(self[index].user)
        trace += "Service time was {0} minutes.".format(service_time)
        self.model.sim.trace.add_output(trace)
        
        self.remove_user(index)
        if self.queue.length > 0:
            user = self.queue.remove()
            self.request(user)             
        
    def remove_user(self, index):
        user = self[index].user
        self[index].user = None
        self[index].start_time = None
        return user
    
class ResourceFinishActivityEvent(Event):
    def check_resource_queue(self):
        self._resource.finish_activity(self.index, self.service_time)
    
    def __init__(self, resource, name, index, service_time):
        self._resource = resource
        super().__init__(resource.model, name)
        self.append_callback(self.check_resource_queue)
        self.index = index
        self.service_time = service_time
        