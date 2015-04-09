#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2014, Stacy Irwin
"""
..  module:: despy.core.simulation

**Simulation**
    The *Simulation* class maintains and executes the future event list
    (FEL).
**FelItem**
    A *FelItem* is a named tuple that represents a scheduled event. The
    FEL is a binary heap of *FelItems*.
**NoEventsRemaining**
    The *Simulation* instance raises this subclass of Exception when
    there are no more events on the FEL.
"""

from heapq import heappush, heappop
from itertools import count
from collections import namedtuple
import datetime
import numpy as np
from despy.output.results import Output
from despy.output.report import Datatype
from despy.base.named_object import NamedObject

class FelItem(namedtuple('FelItemTuple',
                         ['time_fld', 'event_fld', 'priority_fld'])):
    """A named tuple that represents a scheduled event.
    
    **Attributes**
    
      * :attr:`time_fld`: The time that the event is scheduled for
        execution. Type: a non-negative integer.
      * :attr:`event_fld`: An instance of
        :class:`despy.core.event.Event`.
      * :attr:`priority_fld`: A priority constant from the 
        :module:`despy.base.named_object` module, or an integer between
        -4 and +4, inclusive.
        
    **Priority Constants**
        The despy.base package includes three constants that are used to
        prioritize events that are scheduled to occur a the same time.
        Events assigned a higher priority will occur before events that
        are assigned lower priorities.
        
        *PRIORITY_STANDARD*
            Despy uses PRIORITY_STANDARD as the default priority when no
            other priority is specified.
            
        *PRIORITY_EARLY*
            Events assigned PRIORITY_EARLY will be executed before
            PRIORITY_STANDARD and PRIORITY_LATE events.
            
        *PRIORITY_LATE*
            Events assigned PRIORITY_LATE will be executed after
            PRIORITY_EARLY and PRIORITY_STANDARD events.
            
        Events scheduled to occur at the same time with the same
        priority may be executed in any order.
        
        The priority integer value is added to the scheduled event time.
        Internally, Despy multiplies the scheduled time by 10. This
        means that events scheduled to occur at time 1 are internally
        scheduled for time 10, time 12 would occur at internal time
        120, etc. This scheduling mechanism allows priorities as high
        as 4 and as low as -4. A model that requires more than three
        different priorities probably needs to be redesigned, therefore,
        Despy only provides named constants for priorities from -1 to 1.
    
    """

    PRIORITY_EARLY = -1
    PRIORITY_STANDARD = 0
    PRIORITY_LATE = 1

class Simulation(NamedObject):
    """ Schedules events and manages the future event list (FEL).
    
    Every model is assigned to one (and only one) Simulation object.
    A Simulation object may contain one or more models.
    
    **Attributes**

      * :attr:`name`: Simulation object's name. Inherited from
        :class:`despy.base.named_object.NamedObject`. Type: string.
      * :attr:`.description`: One or more paragraphs that describes the
        simulation. Inherited from
        :class:`despy.base.named_object.NamedObject` Type: string.
      * :attr:`.models`: A list of all :class:`.Model` objects that
        have been assigned to the simulation.
      * :attr:`.seed`: The np.random.seed method will be seeded with
        this integer prior to running the simulation.
      * :attr:`.now`: An integer representing the current simulation
        time. Type: integer (non-negative).
      * :attr:`evt`: Returns the :class:`despy.core.event.Event` object
        that is currently being executed. If no event is being executed,
        returns `None`. Read-only.
      * :attr:`.run_start_time`: The real-world start time for the
        simulation. Type: datetime.datetime, or `None` if the simulation
        has not yet been run. Read-only.
      * :attr:`run_stop_time`: The real-world stop time for the
        simulation. Type: datetime.datetime, or `None` if the simulation
        has not yet been run. Read-only.
      * :attr:`.console_output`: If True, the trace record for each
        event will be sent to the standard output. The default value
        is True. Type: Boolean.
      * :attr:`.output_folder`: If NONE (the default value), the
        simulation will not generate any output or trace files.
      * :attr:`out`: A :class:`despy.output.results` object that will
        generate all output files.


    **Methods**

      * :meth:`.append_model`: Appends a :class:`despy.core.model.Model`
        object to the Simulation object. A Despy simulation can run
        multiple models simultaneously.
      * :meth:`.schedule`: Schedules an event on the FEL.
      * :meth:`.peek`: Gets the time of the next scheduled event, but
        leaves the event on the FEL.
      * :meth:`.step`: Executes the next event on the FEL.
      * :meth:`.run`: Executes the remaining events on the FEL in order,
        until no events remain, or until the time specified in the
        until parameter is reached.
      * :meth:`.get_output`: Gets a Python list that contains 
        simulation parameters, such as name, run time, etc.
      * :meth:`.reset`: Resets the simulation time to the beginning of
        the simulation and resets the model and its components to their
        initial state.
      * :meth:`._initialize_models`: Calls the
        :meth:`despy.core.model.Model.initialize` method for every model
        assigned to the Simulation object. This method is marked as
        private and is not intended to be called by the DES designer
        or user. The Simulation calls this object before executing any
        events from the FEL.
        
    **Inherits**
      * :class:`despy.core.base.NamedObject`
      
    """

    def __init__(self, initial_time=0, name = "Simulation",
                 description = None):
        """Creates and initializes the Simulation object.
        
        The Simulation object contains and manages the future event
        list (FEL).
        
        **Arguments**
            * *initial_time:* Optional. A non-negative integer that
              specifies the initial simulation time. Defaults to 0.
            * *name:* Optional. A word or short phrase that describes
              the simulation. Type: string. Defaults to "Simulation".
            * *description:* Optional. A sentence or short paragraph
              that describes the simulation in more detail than the
              name attribute. Type: string or type None. Defaults to
              type None.
        """
        super().__init__(name, description)
        self._models = []
        self._seed = None
        self._evt = None
        self._run_start_time = None
        self._run_stop_time = None
        self.console_output = True
        self._output_folder = None
        self._out = Output(self)
        
        self.reset(initial_time)

    @property
    def models(self):
        """Get a list of all models attached to the simulation.
        
        *Returns:* A list of despy.model.Model objects.
        """
        return self._models
    
    @property
    def seed(self):
        return self._seed
    
    @seed.setter
    def seed(self, seed):
        self._seed = seed
        np.random.seed(seed)

    @property
    def now(self):
        """The current time of the simulation. The time is a unit-less
        integer."""
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10

    @property
    def evt(self):
        return self._evt
        
    @property
    def run_start_time(self):
        return self._run_start_time
    
    @property
    def run_stop_time(self):
        return self._run_stop_time

    @property
    def console_output(self):
        return self._console_output
    
    @console_output.setter
    def console_output(self, output):
        self._console_output = output
        
    @property
    def output_folder(self):
        return self._output_folder
    
    @output_folder.setter
    def output_folder(self, folder):
        self._output_folder = folder
        
    @property
    def out(self):
        return self._out
    
    @out.setter
    def out(self, output):
        self._out = output
    
    def append_model(self, model):
        """ Append a model object to the simulation.
        
        *Arguments*
            model:
                A despy.model.Model object.
        """
        self._models.append(model)

    def schedule(self, event, delay=0, priority=FelItem.PRIORITY_STANDARD):
        """ Add an event to the FEL.

        *Arguments*
            event (despy.Event):
                An instance or subclass of the despy.Event class.
            delay (integer):
                A non-negative integer that defaults to zero, meaning
                the event will be scheduled to occur mmediately.

        """
        # Ensures delay value is always an integer.
        delay = round(delay)

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
        
    def _initialize_models(self):
        for model in self._models:
            if not model.initial_events_scheduled:
                model.initialize()
                model.initial_events_scheduled = True

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

        # Run event
        self._evt = fel_item.event_fld
        fel_item.event_fld.do_event()
        self._evt = None

        # Record event in trace report        
        self.out.trace.add_event(self.now, fel_item.priority_fld,
                                 fel_item.event_fld)
        
        # Reset the event in case it is called again.
        fel_item.event_fld.reset()
        
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
        self._run_start_time = datetime.datetime.today()
        self._initialize_models()
        
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
        self._run_stop_time = datetime.datetime.today()
        if self.output_folder is not None:
            self.out.write_files(self.output_folder)
            
    def get_output(self):
        elapsed_time = self.run_stop_time - self.run_start_time
        
        output = [(Datatype.title, "Simulation: " + self.name),
                  (Datatype.paragraph, self.description),
                  (Datatype.param_list,
                    [('Output Folder', self.output_folder),
                     ('Seed', self.seed),
                     ('Start Time', self.run_start_time),
                     ('Stop Time', self.run_stop_time),
                     ('Elapsed Time', elapsed_time)])
                  ]
        return output

    def reset(self, initial_time=0):
        """Reset the simulation time to zero so the simulation can be
        rerun.
        """
        self._now = initial_time * 10
        self._futureEventList = []
        self._run_start_time = None
        self._run_stop_time = None
        #  Each event gets a unique integer ID, starting with 0 for the first
        # event.
        self._counter = count()
        self.out.trace.clear()
        #self.out = Output(self) #Removed because created problems with trace
        # start and stop times following a simulation reset. Not quite sure
        # why it was here in first place.
        for model in self.models:
            model.initial_events_scheduled = False

class NoEventsRemainingError(Exception):
    pass



