#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*******************
despy.core.resource
*******************

:class:`Resource`
    Represents a limited, real-world, entity that provides a service.
"""

from collections import OrderedDict
from despy.core.component import Component
from despy.core.event import Event
from despy.core.queue import Queue

# TODO: Add different options for selection of empty resources, either
# prioritization by number, random selection, or equal loading.

#TODO: Revise get activity time to allow parameters.

class Resource(Component):
    """Represents a limited, real-world entity that provides a service.
    
    Generally an object or entity with limited availability that
    provides some kind of service.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      
    **Attributes**
      * :attr:`Resource.capacity`: The number of entities that can be
        served simultaneously.
      * :attr:`Resource.activity_time`: A method that returns the time
        required by the resource.
        
    **Methods**
      * :meth:`Resource.get_activity_time`: Gets the time needed for a
        position to complete an activity.
      * :meth:`Resource.get_empty_position`: Gets the empty resource
        position with the lowest number.
      * :meth:`Resource.__getitem__`: Allows accessing resource
        positions with array brackets.
      * :meth:`Resource.__setitem__`: Allows setting resource positions
        with array brackets.
    """
    
    def __init__(self, model, name, capacity):
        super().__init__(model, name)
        self._capacity = capacity

        self._positions = {index: Resource.Position(index, name) \
                           for index in range(1, self.capacity + 1)}

        self._queue = Queue(model, name + "-Queue")
        self._activity_time = None
        
    @property
    def capacity(self):
        """The number of entities that can be served simultaneously.
        
        *Returns:* A positive integer.
        """
        return self._capacity
    
    @capacity.setter
    def capacity(self, capacity):
        """The number of entities that can be served simultaneously.
        
        *Arguments*
            ``capacity`` (Integer)
        """
        self._capacity = capacity
    
    @property
    def queue(self):
        """Entities wait in a queue when the resource is busy.
        
        An instance of :class:`despy.core.queue.Queue`, which is a
        first-in, first-out group. Users of the resource are placed in
        the queue when the all resource positions are busy serving other
        entities. The resource removes items from the queue when a
        resource position becomes available by finishing service on an
        entity.
        
        *Returns:* An instance of :class:`despy.core.queue.Queue`.
        """
        return self._queue

    @queue.setter
    def queue(self, queue):
        """Entities wait in a queue when the resource is busy.
         
        *Arguments*
            ``queue``
                *Returns:* An instance of
                :class:`despy.core.queue.Queue`.
        """
        self._queue = queue
        
    @property
    def activity_time(self):
        """A method that returns the time required by the resource.
        
        *Returns:* A Python method.
        """
        return self._activity_time
    
    @activity_time.setter
    def activity_time(self, time_function):
        """A method that returns the time required by the resource.
        
        *Arguments*
            ``time_function`` (Python function)
                Python function that returns the time required for a
                resource position to complete an activity.
        """
        self._activity_time = time_function

    def get_activity_time(self):
        """Gets the time needed for a position to complete an activity.
        
        *Arguments*
            None
            
        *Raises*
            ``NotImplementedError``: Raised if user has not set the
            ``Resource.activity_time`` property to a function.
        """
        if self.activity_time is None:
            raise NotImplementedError
        else:
            return self.activity_time()
    
    def get_empty_position(self):
        """Gets the empty resource position with the lowest number.
        
        *Returns:* An integer ranging from 1 to ``Resource.capacity``,
        or returns ``False`` if no positions are available.
        
        """
        for index in range(1, self.capacity + 1):
            if self[index].user is None:
                return index
        return False
    
    def __getitem__(self, index):
        """Allows accessing resource positions with array brackets.
        
        A Python magic method that makes a Resource object act like an
        array. It allows users to specify a resource position index in
        square brackets on a Resource object.
        
        *Returns*: :class:`despy.core.resource.Resource.Position`
        """
        return self._positions[index]
    
    def __setitem__(self, index, item):
        """Allows setting resource positions with array brackets.
        
        *Arguments*
            ``index``
                An integer ranging from 1 to ``Resource.capacity``.
                The ``index`` argument is specified inside square
                brackets.
            ``item``
                An instance of
                :class:`despy.core.resource.Resource.Position`. The
                ``item`` object is assigned with an equals sign::
                
                    Resource[index] = item
        
        """
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
    
    class Position():
        def __init__(self, index, name):
            self.name = "{0} #{1}".format(name, index)
            self.user = None
            self.start_time = None
        
        def __str__(self):
            return self.name
            
    
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
        