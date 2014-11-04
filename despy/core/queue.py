#!/usr/bin/env python3

from despy.core.base import Component
from despy.output.report import Datatype
import despy.output.plot as plot
from collections import deque, namedtuple
import numpy as np

Queue_item = namedtuple('Queue_item', ['item_fld', 'time_in_fld'])

class Queue(Component):
    def __init__(self, model, name, max_length = None):
        super().__init__(model, name)
        if isinstance(max_length, int):
            self._queue = deque(max_length)
        else:
            self._queue = deque()
        self.times_in_queue = []

    def add(self, item):
        self._queue.append(Queue_item(item_fld = item, \
                                      time_in_fld = self.model.sim.now))
    
    def remove(self):
        item = self._queue.popleft()
        self.times_in_queue.append(self.model.sim.now - item.time_in_fld)
        return item.item_fld
    
    @property
    def length(self):
        return len(self._queue)
    
    def get_output(self, folder):
        # Create Time in Queue Histogram
        qtimes = np.array(self.times_in_queue, np.int32)
        qtime_filename = '{0}_time_in_q.png'.format(self.id)
        plot.histogram(self.times_in_queue, folder, qtime_filename,
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
                 (Datatype.image, qtime_filename)]
     
        return output
        

    
        
