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

from collections import OrderedDict, namedtuple
from scipy.stats import randint
from despy.core.component import Component
from despy.core.event import Event
from despy.core.queue import Queue

# TODO: Add different options for selection of empty resources, either
# prioritization by number, random selection, or equal loading.

class Resource(Component):
    def __init__(self, model, name, capacity = 1, time_function = None):
        super().__init__(model, name)
        self.capacity = capacity
        self.service_time = time_function
        self._res_queue = None

        self.Station_tuple = namedtuple('Station', ['user', 'start_time'])
        empty_station = self.Station_tuple(user = None, start_time = None)
        self.stations = [empty_station] * self.capacity
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
    
    def __str__(self):
        """Magic method that converts the resource object to a string.
        
        *Returns:* The name property of the resource object.
        """
        return self.name
    
    def __getitem__(self, index):
        return self.stations[index]
    
    def __setitem__(self, index, user):
        self.stations[index] = user
        

    def get_available_station(self, random = False):
        """Returns the index of an empty station.
        
        *Arguments*
            ``random`` (Boolean)
                If set to True, randomly chooses the index of an empty
                station. Otherwise, returns the index of the empty
                station with the lowest index value.
                
        *Returns:* A positive integer representing the index number of
        the station. ``None`` if no stations are empty.
        """
        empty_stations = []
        for index in range(self.capacity):
            if self.stations[index].user == None:
                empty_stations.append(index)
        
        if len(empty_stations) == 0:
            return None
        elif not random:
            return empty_stations[0]
        else:
            return empty_stations[randint(0, len(empty_stations) - 1)]        

    def request(self, user, random = False):
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
            
        index = self.get_available_station()

        if index is not None:
            #ResourceQueue position is available
            assert(self.stations[index].user == None) #Resource is open
            self.start_service(index, user)
            return index
        else:
            #Resources all busy
            if self.res_queue is not None:
                self.res_queue.queue.add(user)
            return False 

    def get_service_time(self, index):
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
        try:
            return self.service_time(index)
        except:
            if self.service_time is None:
                raise NotImplementedError  
        
#TODO: Fix bug with inherited service time functions.
    
    def start_service(self, index, user):
        """Commence servicing a user at the index position.
        
        *Arguments*
            ``index``
                The index number of the resource position that will
                be servicing the user.
        """

        #Assign user to station
        self.stations[index] = self.Station_tuple(user, self.sim.now)
        
        #Create trace record for starting the service.
        fields = OrderedDict()
        fields['Resource'] = self.name + '-' + str(index)
        fields['User'] = self.stations[index].user
        message = "Starting Service"
        self.sim.gen.trace.add_message(message, fields)
        
        #Get service time and schedule end of service on FEL.
        service_time = self.get_service_time(index)
        finish_event = ResourceFinishServiceEvent(\
            self, index, service_time)
        self.model.schedule(finish_event, service_time)
        
    def finish_service(self, index):
        self.stations[index] = self.Station_tuple(None, None)
        if self.res_queue:
            if self.res_queue.queue.length > 0:
                user = self.res_queue.queue.remove()
                self.start_service(index, user)   
    
    def remove_user(self, index):
        """Remove user from a resource station.
        
        *Arguments*
            ``index``
                The index number of the station from which the user will
                be removed.
        
        *Returns:* The user that was being serviced by the resource.
        """
        user = self.stations[index].user
        self.stations[index].user = None
        self.stations[index].start_time = None
        return user


class ResourceFinishServiceEvent(Event):
    def check_resource_queue(self):
        self.resource.finish_service(self.station_index)
    
    def __init__(self, resource, station_index, service_time):
        super().__init__(resource.model, "Finished Service")
        self.resource = resource
        self.station_index = station_index
        self.service_time = service_time
        self.append_callback(self.check_resource_queue)
        
    def _update_trace_record(self, trace_record):
        trace_record['entity'] = \
                self.resource.stations[self.station_index].user
        trace_record['duration_label'] = 'Service Time:'
        trace_record['duration_field'] = self.service_time
        return trace_record


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
    
    def __init__(self, model, name):
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
        """Append a resource to the resourceQueue object.
        
        *Arguments*
            ``resource``
                A :class:`despy.core.resource.Resource object that will
                be appended to the ResourceQueue object.
        """
        index = self.num_resources
        self[index] = resource
        resource._res_queue = self
    
    def get_available_resource(self, random = False):
        """Gets an available resource.
        
        *Arguments*
            ``random`` (Boolean)
                If set to True, randomly chooses the index of an
                available resource. Otherwise, returns the index of the
                available resource with the lowest index value.
                
        *Returns:* A positive integer representing the index number of
        the resource. ``None`` if all resources are busy.
        
        """
    
        empty_resources = []
        for index in range(self.num_resources):
            if self[index].get_available_station:
                empty_resources.append(index)
        
        if len(empty_resources) == 0:
            return None
        elif not random:
            return empty_resources[0]
        else:
            return empty_resources[randint(0, len(empty_resources) - 1)] 

    def request(self, user, random = False):
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
        
        index = self.get_available_resource(random)

        if index is not None:
            #ResourceQueue position is available
            self[index].request(user, random)
            return index
        else:
            #Resources all busy
            if self.queue is not None:
                self.queue.add(user)
            return False         
    

        