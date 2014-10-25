#!/usr/bin/env python3

from despy.core.base import Component
from collections import deque, namedtuple
import numpy as np
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt

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
    
    def get_report(self, folder):
        times = np.array(self.times_in_queue)
        max_time = np.amax(times)
        min_time = np.amin(times)
        mean_time = np.mean(times)
         
        doc = ET.Element('html')
        ET.SubElement(doc, 'head')
        doc_body = ET.SubElement(doc, 'body')
        tag = ET.SubElement(doc_body, 'h1')
        tag.text = "Queue Wait Times"
        ET.SubElement(doc_body, 'img', {'src': 'queue.png'})
        docTree = ET.ElementTree(doc)
        docTree.write(folder + '/report.html', method = 'html')
        
        plt.clf()
        plt.hist(times, [0, 1, 2, 3, 4, 5, 6])
        plt.title(self.name)
        plt.xlabel("Time in Queue")
        plt.ylabel("Frequency")
        plt.savefig(folder + '/queue.png')
    
        
