#!/usr/bin/env python3

from despy.core.base import _ModelMember
from collections import deque, namedtuple

Queue_item = namedtuple('Queue_item', ['q_item', 'q_time_in'])

class Queue(_ModelMember):
    def __init__(self, model, name, max_length = None):
        self._model = model
        self._name = name
        if isinstance(max_length, int):
            self._queue = deque(max_length)
        else:
            self._queue = deque()

    def add(self, item):
        self._queue.append(Queue_item(q_item = item, \
                                      q_time_in = self.model.experiment.now))
    
    def remove(self):
        return self._queue.popleft().q_item
    
    @property
    def length(self):
        return len(self._queue)