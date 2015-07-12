#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
****************
despy.core.timer
****************

:class:`RandomTimer`
    Schedules an event to occur repeatedly at a random interval.
:class:`TimerEvent`
    Event that schedules itself to recur after an interval.

"""
import scipy.stats as stats
from despy.core.component import Component
from despy.core.event import Event
from despy.core.simulation import FelItem


class RandomTimer(Component):
    """Schedules an event to occur repeatedly at a random interval.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      
      **Members**
      
      ..  autosummary::
      
          distribution
          callback
          immediate
          current_interval
          priority
    """
    def __init__(self, model, name, distribution, callback,
                 immediate = False,
                 priority = FelItem.PRIORITY_STANDARD,
                 description = None):
        """ Instantiates a RandomTimer object.
        
        *Arguments*
            ``model`` (:class:`despy.core.model.Model`)
                The RandomTimer must be assigned to a Model object.
            ``name`` (String)
                A short descriptive name for the RandomTimer object.
            ``distribution`` A frozen scipy.stats discrete distribution.
                Random intervals will be generated from this
                distribution.
            ``callback`` Python function or method object
                Callback function will be executed at intervals
                generated by RandomTimer object.
            ``immediate`` Boolean
                Optional. If True, first RandomTimerEvent will occur
                immediately. If False (default), first event will occur
                after a random interval.
            ``priority`` Integer
                Optional. Default is FelItem.PRIORITY_STANDARD. 
                RandomTimerEvents will execute with this priority.
            ``description`` String
                Optional. Default is None. A paragraph that describes
                the RandomTimer object.
        """
        
        # Set some attributes
        super().__init__(model, name, description = description)
        self._immediate = immediate
        self.priority = priority
        self.callback = callback
        self._current_interval = 0
        
        # Set distribution attribute
        if isinstance(distribution, stats.distributions.rv_frozen) or \
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
        """Intervals are generated from this distribution. Read-only.
        
        *Type:* Scipy.stats frozen distribution object.
        """
        return self._distribution

    @property
    def callback(self):
        """TimerEvents include this callback function.
        
        *Type:* Python method or function object.
        """
        return self._callback
    
    @callback.setter
    def callback(self, callback):
        if callable(callback):
            self._callback = callback
        else:
            raise TypeError

    @property
    def immediate(self):
        """If true, first TimerEvent will occur immediately.
        
        *Type:* Boolean
        """
        return self._immediate
    
    @property
    def current_interval(self):
        """Interval between most recently completed and next event.
        
        *Type:* Integer
        """
        return self._current_interval
    
    @property
    def priority(self):
        """FelItem priority of TimerEvents.
        
        *Type:* Integer
        """
        return self._priority
    
    @priority.setter
    def priority(self, priority):
        self._priority = priority
    
        
class TimerEvent(Event):
    """Event that schedules itself to recur after an interval.
    
    **Inherited Classes**
      * :class:`despy.core.event.Event`
      
    **Members**
    
    ..  autosummary::
    
    reschedule
    _update_trace_record
    
    """
    def __init__(self, name, timer):
        """Create a TimerEvent.
        
        *Arguments*
            ``name`` String
                A short descriptive name for the TimerEvent.
            ``timer`` :class:`RandomTimer`
                The event recurs based on the parameters of the
                RandomTimer object passed via this argument.
        """
        super().__init__(timer.model, name)
        self.timer = timer
        self.append_callback(timer.callback)
        self.append_callback(self.reschedule)
    
    def reschedule(self):
        """Reschedules event based on the RandomTimer's distribution.
        """
        self.timer._current_interval = self.timer.distribution.rvs()
        self.sim.schedule(self, self.timer.current_interval,
                          self.timer.priority)
        
    def _update_trace_record(self, trace_record):
        """Adds the entity name and service time to the trace report.
        """
        trace_record['interval'] = self.timer.current_interval
        return trace_record
