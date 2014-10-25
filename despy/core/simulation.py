#!/usr/bin/env python3

from heapq import heappush, heappop
from itertools import count
from collections import namedtuple
import datetime
import numpy as np
from despy.output.results import Results

from despy.core.base import _NamedObject, PRIORITY_STANDARD

FelItem = namedtuple('FelItem', ['time_fld', 'event_fld', 'priority_fld'])

class Simulation(_NamedObject):

    """ Schedule events and manage the future event list (FEL).

    *Constructor Arguments*
        initial_time (integer):
            A non-negative integer that defaults to zero.
    """

    def __init__(self, initial_time=0, name = None):
        """Initialize the event object.
        """
        self.console_output = True
        self._models = []
        self.out = Results(self)
        self.reset(initial_time)
        self.output_folder = None
        self.run_start_time = None
        self.run_stop_time = None
        self._seed = None

    @property
    def now(self):
        """The current time of the simulation. The time is a unit-less
        integer."""
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10
        
    @property
    def seed(self):
        return self._seed
    
    @seed.setter
    def seed(self, seed):
        self._seed = seed
        np.random.seed(seed)

    @property
    def console_output(self):
        return self._console_output
    
    @console_output.setter
    def console_output(self, output):
        self._console_output = output
        
    @property
    def models(self):
        """Get a list of all models attached to the simulation.
        
        *Returns:* A list of despy.model.Model objects.
        """
        return self._models
    
    def append_model(self, model):
        """ Append a model object to the simulation.
        
        *Arguments*
            model:
                A despy.model.Model object.
        """
        self._models.append(model)

    def schedule(self, event, delay=0, priority=PRIORITY_STANDARD):
        """ Add an event to the FEL.

        *Arguments*
            event (despy.Event):
                An instance or subclass of the despy.Event class.
            delay (integer):
                A non-negative integer that defaults to zero, meaning
                the event will be scheduled to occur mmediately.

        """

        # Places a tuple onto the FEL, consisting of the event time, ID,
        # and event object.
        scheduleTime = self._now + (delay * 10) + priority
        
        heappush(self._futureEventList,
                 FelItem(time_fld=scheduleTime, event_fld=event,
                         priority_fld=priority))

    def peek(self, prioritized=True):
        """Return the time of the next scheduled event, or infinity if there
        is no remaining events.
        """
        try:
            if prioritized:
                return int((self._futureEventList[0].time_fld - \
                        self._futureEventList[0].priority_fld) / 10)
            else:
                return self._futureEventList[0].time_fld / 10
        except IndexError:
            return float('Infinity')
        
    def initialize_models(self):
        for model in self._models:
            if not model.initial_events_scheduled:
                model.initialize()
                model.initial_events_scheduled = True
    
    def get_unique_id(self):
        return self._counter.__next__()

    def step(self):
        """Advance simulation time to the next time on the FEL and
        executes the next event.

        *Raises*
            NoEventsRemaining:
                Occurs if no more events are scheduled on the FEL.
        """

        # Get next event from FEL and advance current simulation time.
        try:
            fel_item = heappop(self._futureEventList)
        except IndexError:
            raise NoEventsRemainingError
        else:
            self.now = int((fel_item.time_fld - \
                    fel_item.priority_fld) / 10)
            
        # Record event in trace report
        self.out.trace.add_event(self.now, fel_item.priority_fld,
                                 fel_item.event_fld.name)

        # Run event
        fel_item.event_fld.do_event()
        

        return fel_item

    def run(self, until=None):
        """ Continue to advance simulation time and execute events on the FEL
        until there are no more events or until the time specified in the
        "until" parameter is reached.

        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. Defaults to 'None',
                meaining the simulation will run until there are no
                remaining events on the FEL.  The events at the time
                specified in 'until' will be executed. For example, if
                until = 100 and there are events scheduled at time
                100, those events will be executed, but events at time
                101 or later will not.
                
        """

        # Initialize models and components
        self.run_start_time = datetime.datetime.today()
        self.initialize_models()
        
        # Step through events on FEL
        if isinstance(until, int):
            stopTime = until
            while self.peek() <= stopTime:
                try:
                    self.step()
                except NoEventsRemainingError:
                    break
        else:
            while True:
                try:
                    self.step()
                except NoEventsRemainingError:
                    break
        
        # Record stop time and write output files
        self.run_stop_time = datetime.datetime.today()
        
        if self.output_folder is not None:
            self.out.write_files(self.output_folder)
            
#         for mod in self.models:
#             for key, comp in mod.components.items():  # @UnusedVariable
#                 comp.get_report()

    def reset(self, initial_time=0):
        """Reset the simulation time to zero so the simulation can be
        rerun.
        """
        self._now = initial_time * 10
        self._futureEventList = []
        #  Each event gets a unique integer ID, starting with 0 for the first
        # event.
        self._counter = count()
        self.out.trace.clear()
        for model in self.models:
            model.initial_events_scheduled = False

class NoEventsRemainingError(Exception):
    pass



