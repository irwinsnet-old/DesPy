#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*********************
despy.model.simulation
*********************

..  autosummary::

    Simulation
    FutureEvent
    NoEventsRemainingError
    
..  todo

    Move reps property to config object.
    
    Modify run and resume methods to accept triggers as parameters.
    
    Update documentation to state that seed can raise a TypeError.
    
    Change seed property to a method to be consistent with numpy and
    random syntax
    
    Revise internal function names -- get rid of underscore prefix and
    replace with "dp_" prefix to indicate an internal framework
    method.
    
    Write test for resume_on_next_rep parameter.
"""

from heapq import heappush, heappop
from itertools import count
import datetime, random
from collections import namedtuple, OrderedDict

import numpy as np

from despy.session import Session
from despy.output.results import Results
from despy.output.report import Datatype
from despy.define import Priority
from despy.model.trigger import AbstractTrigger, TimeTrigger
from despy.output.trace import Trace


class NoEventsRemainingError(Exception):
    """Raised by despy.model.simulation's step method when FEL is empty.
    """
    pass


class Simulation():
    """Schedule events and manage the future event list (FEL).
    
    Every Despy simulation must have one instance of the
    ``Simulation`` class. The ``Simulation`` class initializes the
    top-level model and its components, manages the simulation
    clock and FEL, and executes events.
    
    **Members**
    
    ..  autosummary::
    
        model
        seed
        now
        pri
        evt
        run_start_time
        run_stop_time
        gen
        append_model
        schedule
        peek
        step
        run
        get_data
        initialize_rep
        _initialize_model
        
    **Inherits**
      * None
    """

    def __init__(self, model = None, config = None):
        """Creates a Simulation object.
        
        *Arguments*
            * ``model:`` Optional. Assigns a
            :class:`despy.model.component` to the simulation. If
            omitted, designer must assign the model using the
            'Simulation.model' property before running the simulation.
            * ``config:`` Optional. A :class:`despy.session.config
            object that contains numerous simulation parameters. If
            omitted, a config object is created automatically.
            Configuration options can be set or read via the
            'Simulation.config' or 'Session.config' properties.
        """    
        self._session = Session()
        self._session.sim = self
        if model is not None:
            self._session.model = model
        if config is not None:
            self._session.config = config
        self._rep = 0
        self._trace = Trace()
        
        self.reset()
        
    def reset(self):
        """Resets the simulation to it's initial state.
        
        Clears triggers, sets current rep to 0, sets time to the
        initial time, and clears the FEL and traces. Note that reset
        does not reset the model to its initial condition. 
        """
        self._triggers = OrderedDict()
        self._rep = 0
        self._setups = 0
        self._evt = None
        self._run_start_time = None
        self._run_stop_time = None
        self._now = self._session.config.initial_time * 10
        self._pri = 0
        self._futureEventList = []
        self._counter = count()
        self._trace.clear()
        
    @property
    def session(self):
        """Returns the current Session object. Read-only.
        
        *Type:* :class:`despy.session.Session`
        """
        return self._session
    
    @property
    def model(self):
        """The model that is assigned to the Simulation object.
        
        *Returns:* :class:`despy.model.component.Component`
        """
        return self._session.model
    
    @model.setter
    def model(self, model):
        self._session.model = model

    @property
    def config(self):
        """The assigned :class:`despy.session.Config object.
        """
        return self._session.config
    
    @config.setter
    def config(self, config):
        self._session.config = config
        
    @property
    def rep(self):
        return self._rep
                
    def initialize(self):
        self._now = self._session.config.initial_time * 10
        
        np.random.seed(self._session.config.seed)
        random.seed(self._session.config.seed)
        
        for cpt in self.model:
            cpt.dp_initialize()
    
    def setup(self):
        """Setup for the next replication.
        
        Sets the simulation time to zero. Also sets the model's
        initial_events_scheduled attribute to ``False``, which will cause
        the model's initialize_rep methods to be executed the next time the
        simulation is run. In addition:
        
            * Clears the FEL
            * Erases the run_start_time and run_stop_time properties
            * Resets the main simulation counter
        """
        if self.rep > 0:
            self._now = self._session.config.initial_time * 10
            self._pri = 0
            self._futureEventList = []
            self._counter = count()
        
        for cpt in self.model:
            cpt.dp_setup()
    
    def teardown(self):
        for cpt in self.model:
            cpt.dp_teardown(self.now)

    @property
    def now(self):
        """The current time of the simulation. The time is an integer.
        
        *Returns:* Integer
        
        By default, a simulation starts at time zero and continues
        until three are no events remaining on the FEL or until the
        simulation detects a stop condition. The unit of time
        represented by the integer value stored in the ``now`` property
        is defined by the simulation.
        
        Internally, Despy multiplies the time by a factor of ten and
        each step in the simulation is a multiple of ten. This allows
        assignment of priorities to each event. For example,
        ``Priority.EARLY`` events would be scheduled to run at time 39,
        ``Priority.DEFAULT`` events at time 40, and ``Priority.LATE``
        events at time 41. Despy would indicate that all of these events
        occurred at time = 4 in standard reports and output. This
        practice simplifies the routines that run the events because
        events are placed on the FEL in the order that they will
        actually be run, taking assigned priorities into account.
        """
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10
        
    @property
    def pri(self):
        """The priority of the current or most recently completed event.
        
        *Type:* Integer
        """
        return self._pri

    @property
    def evt(self):
        """The event that is currently being executed by the simulation
        at time = ``self.now`` (read only).
        
        *Returns:* :class: `despy.model.event.Event`
        
        """
        return self._evt
    
    @property
    def triggers(self):
        return self._triggers
        
    @property
    def run_start_time(self):
        """The real-world time (i.e., date, hours, minutes, etc.) at
        which the simulation starts (read only).
        
        *Returns:* ``None`` or :class: `datetime.datetime`
        
        Despy uses the run_start_time attribute to calculate the
        simulation's elapsed time. The attribute will return ``None``
        if the simulation has not yet been completed.
        """
        return self._run_start_time
    
    @property
    def run_stop_time(self):
        """The real-world stop time (i.e., date, hours, minutes, etc.)
        for the simulation (read only).
        
        *Returns:* ``None`` or :class: `datetime.datetime`
        
        Despy uses the ``run_stop_time`` attribute to calculate elapsed
        simulation time and to assign unique names to output files. The
        attribute will return ``None`` if the simulation has not yet been
        run.
        """
        return self._run_stop_time

    def schedule(self, event, delay=0, priority=Priority.STANDARD):
        """ Add an event to the FEL.

        *Arguments*
            event (:class:`despy.model.event.Event`):
                An instance or subclass of the ``Event`` class.
            delay (integer):
                A non-negative integer that defaults to zero. If zero,
                the event will be scheduled to occur immediately.
            priority (integer)
                An attribute of the
                :class:`despy.model.simulation.FutureEvent` enumeration, or
                an integer ranging from -5 to +5. The default is
                ``Priority.STANDARD``, which is equivalent to
                zero.
        """
        # Ensures delay value is always an integer.
        delay = round(delay)

        # Places a tuple onto the FEL, consisting of the event time, ID,
        # and event object.
        scheduleTime = self._now + (delay * 10) + priority
        
        heappush(self._futureEventList,
                 FutureEvent(time=scheduleTime, event=event,
                         priority=priority))

    def peek(self, prioritized=True):
        """Return the time of the next scheduled event.
        
        *Arguments*
            prioritized (Boolean):
                If ``True``, the time will reflect the event's priority.
                For example, for a ``Priority.EARLY`` event scheduled to
                run at time = 25, ``peek`` will return 24.9 if the
                ``prioritized`` attribute is set to ``True``. If
                ``False``, then our example would return 25, the nominal
                scheduled time. The default value is ``True``.
        
        *Returns*
            An integer or float value if the FEL contains events.
            Infinity if there are no remaining events.
        """
        try:
            if prioritized:
                return int((self._futureEventList[0].time - \
                        self._futureEventList[0].priority) / 10)
            else:
                return self._futureEventList[0].time / 10
        except IndexError:
            return float('Infinity')
        
    def step(self):
        """Advance simulation time and execute the next event.
        
        The ``step`` method will only execute one event. Users might
        call the ``step`` method for troubleshooting purposes or other
        special cases. Users will generally run their simulation by
        calling the :meth:`.run` method, which repeatedly calls the
        ``step`` method until reaching a stop condition or there are no
        remaining events on the FEL.

        *Raises*
            NoEventsRemaining:
                Occurs if no more events are scheduled on the FEL.
                
        *Returns*
            :class:`despy.model.simulation.FutureEvent`
        """

        # Get next event from FEL and advance current simulation time.
        try:
            fel_item = heappop(self._futureEventList)
        except IndexError:
            raise NoEventsRemainingError
        else:
            self.now = int((fel_item.time - \
                    fel_item.priority) / 10)
            self._pri = fel_item.priority

        # Record event in trace report        
#         self.gen.trace.add_event(self.rep, self.now, fel_item.priority,
#                                  fel_item.event)

        # Run event
        self._evt = fel_item.event
        fel_item.event.dp_do_event()
        self._evt = None
        
        return fel_item

    def run(self, until=None, resume_on_next_rep = False):
        """ Execute events on the FEL until reaching a stop condition.
        
        The ``run`` method will advance simulation time and execute events
        until the FEL is empty or until the time specified in the
        ``until`` parameter is reached.
        
        Before executing any events, ``run`` will ensure model are
        initialized by calling ``_initialize_model``.
        `_initialize_model` ensures model are only initialized one
        time, so users can call ``run`` multiple times and Despy will only
        initialize_rep the model on the first call to ``run`` (unless
        :meth:`.initialize_rep` is called, of course).

        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. Defaults to 'None',
                meaning the simulation will run until there are no
                remaining events on the FEL.  The events at the time
                specified in ``until`` will be executed. For example, if
                until = 100 and there are events scheduled at time
                100, those events will be executed, but events at time
                101 or later will not.
                
        """
        self._set_triggers(until)
        self._run_start_time = datetime.datetime.today()

        if resume_on_next_rep:
            self._rep += 1
        start_rep = self._rep            
        for rep in range(start_rep, self._session.config.reps):
            self._rep = rep
            if self._setups <= self._rep:
                self.setup()
                self._setups += 1

            # Step through events on FEL and check triggers.
            continue_rep = True
            while continue_rep:
                try:
                    self.step()
                except NoEventsRemainingError:
                    break
                continue_rep = self.dp_check_triggers()
        
            # Finalize model and setup for next replication
            self.teardown()
            
        self._run_stop_time = datetime.datetime.today()
        
    def finalize(self):
        for cpt in self.model:
            cpt.dp_finalize()
        self._results = Results(self, self._session.config)
        self._results._trace = self._trace
        return self._results
        
    def _set_triggers(self, until):
        if until is None:
            try:
                del self.triggers["dp_untilTrigger"]
            except KeyError:
                pass            
        elif (until > 0):
            self.add_trigger("dp_untilTrigger", TimeTrigger(until))
        else:
            raise AttributeError("Simulation.run() until argument "
                                 "should be None or integer > 0.  {} "
                                 "passed instead".format(until))
        
    def irun(self, until = None):
        self.initialize()
        self.run(until = until)
        
    def irunf(self, until = None):
        self.initialize()
        self.run(until = until)
        return self.finalize()
        
    def runf(self, until = None, resume_on_next_rep = False):
        self.run(until = until, resume_on_next_rep = resume_on_next_rep)
        return self.finalize()
        
    def dp_check_triggers(self):
        """Checks all simulation triggers, returning False ends rep.
        
        *Returns*
            Boolean. True if replication should continue, False
            otherwise.
        """
        continue_rep = True
        for _, trigger in self.triggers.items():
            if trigger.check():
                if not trigger.pull():
                    continue_rep = False
                    break
        return continue_rep
    
    def add_trigger(self, key, trigger):
        err_msg = ("{0} object provided to Simulation.add_trigger() "
                "method must be a subclass of "
                "despy.model.trigger.Trigger or registered as a "
                "subclass using the Trigger.register() method")
        
        if issubclass(trigger.__class__, AbstractTrigger):
            self.triggers[key] = trigger
        else:
            raise TypeError(err_msg.format(repr(trigger)))
            
    def add_message(self, message, fields):
        if self.evt is None:
            self._trace.add_message(message, fields)
        else:
            self.evt.add_message(message, fields)
    
    def get_data(self):
        """ Get a Python list with simulation parameters and results.
        
        The generator object calls the get_data method of the simulation
        and model objects and places the data in the simulation report.
        The generator object will also call the user-defined get_data
        methods from all of the model components.
        
        *Returns*
            A Python list of tuples. The first item of each tuple is
            a member of the :class:`despy.output.datatype.Datatype`
            enumeration, which describes the structure of the data
            item (e.g., paragraph, list, etc.).
            
        """
        elapsed_time = self.run_stop_time - self.run_start_time
        
        output = [(Datatype.title, "Simulation"),
                  (Datatype.param_list,
                    [('Generator Folder',
                        self._session.config.folder_basename),
                     ('Seed', self.config.seed),
                     ('Start Time', self.run_start_time),
                     ('Stop Time', self.run_stop_time),
                     ('Elapsed Time', elapsed_time)])
                  ]
        return output
            
class FutureEvent(namedtuple('FutureEventTuple',
                         ['time', 'event', 'priority'])):
    """A event that has been placed on the future event list (FEL).
    
    Every item on the FEL must be an instance of FutureEvent. A
    FutureEvent consists of the event, the scheduled time, and priority.
    
    **Attributes**
    
      * :attr:`time`: The time that the event is scheduled for
        execution. Type: a non-negative integer.
      * :attr:`event`: An instance of
        :class:`despy.model.event.Event`.
      * :attr:`priority`: A priority constant from the 
        :mod:`despy.base.named_object2` module, or an integer between
        -4 and +4, inclusive.
    
    """