#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
********************
despy.output.counter
********************

..  autosummary::


..  todo::

    Finish class.

"""

from despy.output.statistic import AbstractStatistic

class Counter(AbstractStatistic):
    def __init__(self, name):
        super().__init__(name, 'u4')
        
        #### Readable Properties ####
        self._total_count = None
        self.properties.append(['total_count', 'reps', 'rep_counts'
                               'max_rep_count', 'min_rep_count'])
        
        #### Internal Details
        self._rep_counts = []
          
    def append(self, value = None, time = None):
        self.increment()
        
    def increment(self):
        self._rep_counts[-1] += 1
        
    def setup(self):
        self._rep_counts.append(0)
        
    def teardown(self):
        pass
    
    def finalize(self):
        pass
    
    @property
    def total_counts(self):
        return sum(self._rep_counts)
    
    @property
    def reps(self):
        return len(self._rep_counts)
    
    @property
    def rep_counts(self):
        return self._rep_counts
    
    @property
    def max_rep_count(self):
        return max(self._rep_counts)
    
    @property
    def min_rep_count(self):
        return min(self._rep_counts)
    
    
        
        
        

    
    
        