#!/usr/bin/env python3

from collections import OrderedDict

from despy.core.component import Component
from despy.core.event import Event

# TODO: Add different options for selection of empty resources, either
# prioritization by number, random selection, or equal loading.

class Resource(Component):
    """A resource is a component that represents a real-world resource.
    
    Generally an object or entity with limited availability that
    provides some kind of service.
    """
    
    class Position():
        def __init__(self, index, name):
            self.name = "{0} #{1}".format(name, index)
            self.user = None
            self.start_time = None
        
        def __str__(self):
            return self.name
            
    def __init__(self, model, name, capacity):
        super().__init__(model, name)
        self.capacity = capacity

        self._positions = {index: Resource.Position(index, name) \
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
            self[index].start_time = self.sim.now
            self.start_activity(index)
            return index
        else:
            if self.queue is not None:
                self.queue.add(user)
            return False
        
    def start_activity(self, index):
        fields = OrderedDict()
        fields['Server'] = self[index]
        fields['Customer'] = self[index].user
        message = "Starting Activity"
        self.sim.gen.trace.add_message(message, fields)
        
        service_time = self.get_activity_time()

        finish_event = ResourceFinishActivityEvent(\
            self, "Finished Activity", index, service_time)
        self.model.schedule(finish_event, service_time)
        
    def finish_activity(self, event, index, service_time):
        event.user = self.remove_user(index)
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
        self._resource.finish_activity(self, self.index, self.service_time)
    
    def __init__(self, resource, name, index, service_time):
        self._resource = resource
        super().__init__(resource.model, name)
        self.append_callback(self.check_resource_queue)
        self.index = index
        self.service_time = service_time
        self.user = None
        
    def _update_trace_record(self, trace_record):
        trace_record['entity'] = self.user
        trace_record['duration_label'] = 'Service Time:'
        trace_record['duration_field'] = self.service_time
        return trace_record
        