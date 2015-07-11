#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.core.timer
****************
"""
import scipy.stats as stats
from despy.core.component import Component
from despy.core.event import Event
from despy.core.simulation import FelItem


class RandomTimer(Component):
    def __init__(self, model, name, distribution, callback,
                 immediate = False,
                 priority = FelItem.PRIORITY_STANDARD,
                 description = None):
        
        # Set some attributes
        super().__init__(model, name, description = description)
        self._immediate = immediate
        self.priority = priority
        self.callback = callback
        self._current_interval = 0
        
        # Set distribution attribute
        if isinstance(distribution,stats.distributions.rv_frozen) or \
                        isinstance(distribution,
                        stats._distn_infrastructure.rv_discrete):
            self._distribution = distribution
        else:
            raise TypeError("distribution parameter must be "
                            "type stats.rv_discrete")

        # Schedule first event
        evt = TimerEvent(name, self)
        if immediate:
            self.model.sim.schedule(evt, priority = self.priority)
        else:
            self._current_interval = self.distribution.rvs()
            self.model.sim.schedule(evt, self.current_interval,
                                    priority = self.priority)
        
    @property
    def distribution(self):
        return self._distribution

    @property
    def callback(self):
        return self._callback
    
    @callback.setter
    def callback(self, callback):
        if callable(callback):
            self._callback = callback
        else:
            raise TypeError

    @property
    def immediate(self):
        return self._immediate
    
    @property
    def current_interval(self):
        return self._current_interval
    
    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, priority):
        self._priority = priority
    
        
class TimerEvent(Event):
    def __init__(self, name, timer):
        super().__init__(timer.model, name)
        self.timer = timer
        self.append_callback(timer.callback)
        self.append_callback(self.reschedule)
    
    def reschedule(self):
        self.timer._current_interval = self.timer.distribution.rvs()
        self.sim.schedule(self, self.timer.current_interval,
                          self.timer.priority)
        
    def _update_trace_record(self, trace_record):
        """Adds the entity name and service time to the trace report.
        """
        trace_record['interval'] = self.timer.current_interval
        return trace_record
