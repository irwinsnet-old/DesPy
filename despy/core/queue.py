#!/usr/bin/env python3

from despy.core.base import Component
from collections import deque, namedtuple

import matplotlib.pyplot as plt

Queue_item = namedtuple('Queue_item', ['item_fld', 'time_in_fld'])

class Queue(Component):
    def __init__(self, model, name, max_length = None):
        self._model = model
        self._name = name
        if isinstance(max_length, int):
            self._queue = deque(max_length)
        else:
            self._queue = deque()
        self.wait_times = []

    def add(self, item):
        self._queue.append(Queue_item(item_fld = item, \
                                      time_in_fld = self.model.sim.now))
    
    def remove(self):
        item = self._queue.popleft()
        self.wait_times.append(self.model.sim.now - item.time_in_fld)
        return item.item_fld
    
    @property
    def length(self):
        return len(self._queue)
    
    def get_report(self):
        plt.hist(self.wait_times)
        plt.savefig()