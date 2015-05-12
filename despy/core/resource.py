#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*******************
despy.core.resource
*******************

:class:`ResourceQueue`
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
#    def __init__(self, model, resource, index, name):
#        super().__init__(model, "{0} #{1}".format(name, index))
    def __init__(self, model, name, capacity = 1, time_function = None):
        super().__init__(model, name)
        self.capacity = capacity
        self.service_time = time_function
        self._res_Queue = None
        self.user = None
        self.start_time = None

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
    def res_queue(self):
        """The resourceQueue that contains the queue of incoming users.
        
        *Returns:* a :class:`despy.core.resource.ResourceQueue` object.
        """
        return self._res_queue
    
    def __str__(self):
        return self.name
    
    @property
    def service_time(self):
        """A method that returns the time required by the resource.
        
        *Returns:* A Python method.
        """
        return self._service_time
    
    @service_time.setter
    def service_time(self, time_function):
        """A method that returns the time required by the resource.
        
        *Arguments*
            ``time_function`` (Python function)
                Python function that returns the time required for a
                resource position to complete the service.
        """
        self._service_time = time_function

    def get_service_time(self, user = None, **arguments):
        """Gets the time needed for a position to complete an activity.
        
        *Arguments*
            ``user``
                The entity that is being serviced by the resource.
            ``arguments``
                All other arguments will be passed to the
                service_time function defined by the user.
            
        *Raises*
            ``NotImplementedError``: Raised if user has not set the
            ``ResourceQueue.service_time`` property to a function.
        """
        if self.service_time is None:
            raise NotImplementedError
        else:
            return self.service_time(user, *arguments)
    
    def start_service(self):
        """Commence servicing a user at the index position.
        
        *Arguments*
            ``index``
                The index number of the resource position that will
                be servicing the user.
        """
        #Create trace record for starting the service.
        fields = OrderedDict()
        fields['Server'] = self
        fields['Customer'] = self.user
        message = "Starting Service"
        self.sim.gen.trace.add_message(message, fields)
        
        #Get service time and schedule end of service on FEL.
        service_time = self.resource.get_service_time(self.user, self.index)
        finish_event = ResourceFinishServiceEvent(\
            self, "Finished Service", service_time)
        self.model.schedule(finish_event, service_time)
        
    def finish_service(self, event, service_time):
        event.user = self.remove_user()
        if self.resource.queue.length > 0:
            user = self.resource.queue.remove()
            self.resource.request(user)   
    
    def remove_user(self):
        user = self.user
        self.user = None
        self.start_time = None
        return user

class ResourceQueue(Component):
    """Represents a limited, real-world entity that provides a service.
    
    An object or entity with limited availability that provides some
    kind of service.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      
    **Attributes**
      * :attr:`ResourceQueue.capacity`: The number of entities that can be
        served simultaneously.
      * :attr:`ResourceQueue.service_time`: A method that returns the time
        required by the resource.
        
    **Methods**
      * :meth:`ResourceQueue.get_service_time`: Gets the time needed for a
        position to complete an activity.
      * :meth:`ResourceQueue.get_available_resource`: Gets the empty resource
        position with the lowest number.
      * :meth:`ResourceQueue.__getitem__`: Allows accessing resource
        positions with array brackets.
      * :meth:`ResourceQueue.__setitem__`: Allows setting resource positions
        with array brackets.
      * :meth:`ResourceQueue.request`: Request a resource for a user.
      * :meth:`ResourceQueue.start_service: Commence servicing a user at the
        index position.
    """
    
    def __init__(self, model, name, capacity):
        super().__init__(model, name)
        self._queue = Queue(model, name + "-Queue")
        self._resources = {}
    
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
    def num_resources(self):
        return len(self._resources)
    
    def __getitem__(self, index):
        """Allows accessing resource positions with array brackets.
        
        A Python magic method that makes a ResourceQueue object act like an
        array. It allows users to specify a resource position index in
        square brackets on a ResourceQueue object.
        
        *Returns*: :class:`despy.core.resource.ResourceQueue.Resource`
        """
        return self._resources[index]
    
    def __setitem__(self, index, item):
        """Allows setting resource positions with array brackets.
        
        *Arguments*
            ``index``
                An integer ranging from 1 to ``ResourceQueue.capacity``.
                The ``index`` argument is specified inside square
                brackets.
            ``item``
                An instance of
                :class:`despy.core.resource.ResourceQueue.Resource`. The
                ``item`` object is assigned with an equals sign::
                
                    ResourceQueue[index] = item
        
        """
        self._resources[index] = item
        
    def add_resource(self, resource):
        index = self.num_resources + 1
        self[index] = resource        
    
    def get_available_resource(self):
        """Gets the empty resource position with the lowest number.
        
        *Returns:* An integer ranging from 1 to ``ResourceQueue.capacity``,
        or returns ``False`` if no positions are available.
        
        """
        for index in range(1, self.capacity + 1):
            if self[index].user is None:
                return index
        return False

    def request(self, user):
        """Request a resource for a user.
        
        Checks if a resource position is available. If so, starts
        serving the user and returns the index of the resource position.
        Otherwise returns False and adds the user to the resource queue.
        
        *Arguments*
            ``user``
                The entity that will be serviced by the resource.
                
        *Returns:* If a resource position is available, returns the
        index value of the resource that will serve the user. Otherwise
        returns False.
        """
        index = self.get_available_resource()

        if index:
            #ResourceQueue position is available
            assert(self[index].user == None) #Resource is open
            self[index].user = user
            self[index].start_time = self.sim.now
            self[index].start_service()
            return index
        else:
            #Resources all busy
            if self.queue is not None:
                self.queue.add(user)
            return False         
    
class ResourceFinishServiceEvent(Event):
    def check_resource_queue(self):
        self.position.finish_service(self, self.service_time)
    
    def __init__(self, position, name, service_time):
        super().__init__(position.model, name)
        self.append_callback(self.check_resource_queue)
        self.position = position
        self.service_time = service_time
        self.user = None
        
    def _update_trace_record(self, trace_record):
        trace_record['entity'] = self.user
        trace_record['duration_label'] = 'Service Time:'
        trace_record['duration_field'] = self.service_time
        return trace_record
        