#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.core.queue
****************
   
:class:`Queue`
    Represents a limited, real-world, entity that provides a service.
"""

#TODO: Refactor so folder parameter doesn't need to be passed to the
# get data method.
#TODO: Add property and output for total items entering the queue
#TODO: Add property and output for total items leaving the queue.
#TODO: Add properties and output for max and min items in queue.

from collections import deque, namedtuple
import numpy as np
from despy.core.component import Component
from despy.output.report import Datatype
import despy.output.plot as plot

class Queue(Component):
    """A component that represents a real world queue.
    
    A Queue object represents a real-world queue, such as a line of
    customers waiting for a server, or a line of products waiting for a
    machine.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      
    **Members**
    
    ..  autosummary::
    
        Item
        length
        times_in_queue
        add
        remove
        get_data
      
    """

    def __init__(self, model, name, max_length = None):
        """Create a Queue object.
        
        *Arguments*
            ``model`` (:class:`despy.core.model.Model`)
                The Queue must be assigned to a Model object.
            ``name`` (String)
                A short descriptive name for the Queue object.
            ``max_length`` (Integer)
                If ``None`` (default value), then the Queue length can
                grow indefinitely. If set to an integer, the Queue will
                be limited to ``max_length``.
        """
        
        super().__init__(model, name)
        if isinstance(max_length, int):
            self._queue = deque(max_length)
        else:
            self._queue = deque()
        self._times_in_queue = []
        
    Item = namedtuple('Item', ['item_fld', 'time_in_fld'])
    """(Class) A named tuple that contains an item added to the queue.
    
    *Attributes*
        ``item_fld``
            An object that is added to the queue.
        ``time_in_fld``
            The time the object was added to the queue.
    """

    @property
    def length(self):
        """The number of entities in the queue at the current time.
        
        *Type:* Integer, read-only.
        """
        return len(self._queue)

    @property
    def times_in_queue(self):
        """List of times (integers) that entities spent in the queue.
        
        *Type:* List of integers, read-only.
        
        The first element of the list is the time that the first entity
        to leave the queue spent in the queue, the second element is for
        the second entity to leave the queue, etc.
        """
        return self._times_in_queue

    def add(self, item):
        """Add an item to the end of the queue.
        
        *Arguments*
            ``item``
                The item that will be added to the queue.
        """
        self._queue.append(Queue.Item(item_fld = item, \
                                      time_in_fld = self._sim.now))
    
    def remove(self):
        """Remove an item from the beginning of the queue.
        
        *Arguments*
            ``item``
                The item that will be removed from the queue.
                
        *Returns:* The item that was removed from the queue.
        """
        item = self._queue.popleft()
        self.times_in_queue.append(self._sim.now - item.time_in_fld)
        return item.item_fld
    
    def get_data(self, folder):
        """Creates charts and adds data to final report.
        
        *Arguments*
            ``folder`` (String)
                All charts will be saved to the location denoted by
                'folder'.
                
        *Returns:* A despy.core.output.Datatype formatted list
        containing data for the final report.
        """
        # Create Time in Queue Histogram
        qtimes = np.array(self.times_in_queue, np.int32)
        qtime_filename = '{0}_time_in_q'.format(self.id)
        full_fname = plot.Histogram(self.times_in_queue, folder,
                       qtime_filename,
                       title = self.name,
                       x_label = "Time in Queue",
                       y_label = "Frequency")     
         
        # Create output
        output = [(Datatype.title, "Queue Results: {0}".format(self.name)),
                 (Datatype.paragraph, self.description.__str__()),
                 (Datatype.param_list,
                    [('Maximum Time in Queue', np.amax(qtimes)),
                     ('Minimum Time in Queue', np.amin(qtimes)),
                     ('Mean Time in Queue', np.mean(qtimes))]),
                 (Datatype.image, full_fname)]
     
        return output