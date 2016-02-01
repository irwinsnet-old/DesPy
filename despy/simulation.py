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
    
    Modify run and resume methods to accept triggers as parameters.

    Have _set_triggers compare current time to until parameter.

    Update documentation to state that seed can raise a TypeError.
    
    Revise internal function names -- get rid of underscore prefix and
    replace with "dp_" prefix to indicate an internal framework
    method.
    
    Write test for resume_on_next_rep parameter.
    
    Change name of despy.stats.random to avoid clash with library module.
    
    Move statistic module to stats package?
    
    Add Simulation log that records time of initialization, setup,
    errors, etc.
"""

from heapq import heappush, heappop
from itertools import count
import datetime, random
from collections import namedtuple, OrderedDict

import numpy as np

from despy.session import Session
from despy.output.results import Results
from despy.output.report import Datatype
from despy.output.console import Console
from despy.fel.event import Priority
from despy.model.trigger import AbstractTrigger, TimeTrigger
from despy.output.counter import Counter


class NoEventsRemainingError(Exception):
    """Raised by despy.simulation._step() when FEL is empty.
    """
    pass


class FutureEvent(namedtuple('FutureEventTuple',
                         ['time', 'event', 'priority'])):
    """A event that has been placed on the future event list (FEL).
    
    Every item on the FEL must be an instance of FutureEvent. A
    FutureEvent consists of the event, the scheduled time, and priority.
    
    **Properties**
    
      * :attr:`time`: The time that the event is scheduled for
        execution. Type: a non-negative integer.
      * :attr:`event`: An instance of
        :class:`despy.model.event.Event`.
      * :attr:`priority`: A priority constant from the 
        :mod:`despy.base.named_object2` module, or an integer between
        -4 and +4, inclusive.
    
    """
    
    
class Dispatcher():
    def __init__(self):
        self._session = Session()
        self._con = Console()
        
    def send_data(self, key, data, label = None):
        processed_label = self._session.results.set_value(key, data, label)
        self._con.display(processed_label, data) 
        
    def announce_phase(self, phase):
        self._con.display_header(phase)
        
    def announce(self, message):
        self._con.display_message(message)
        
        
class Simulation():
    """Schedule events and manage the future event list (FEL).
    
    Every Despy simulation must have one instance of the
    ``Simulation`` class. The ``Simulation`` class initializes the
    top-level model and its components, manages the simulation
    clock and FEL, and executes events.
    
    **Properties**
    
    ..  autosummary::
    
        session
        config
        model
        rep
        now
        event
        pri
        triggers
        run_start_time
        run_stop_time
        
    **Public Methods**
    
    ..  autosummary::
    
        reset
        add_trigger
        initialize
        finalize
        peek
        schedule
        run
        irun
        irunf
        runf
        add_message
        get_data
        
    **Private Methods**
    
    ..  autosummary::

        _setup
        _teardown
        _set_triggers
        _step
        _check_triggers
    """

    def __init__(self, model = None, config = None):
        """Creates a Simulation object.
        
        *Arguments*
            ``model:`` (:class:`despy.model.component`)
                Optional. Assigns a model to the simulation. If omitted,
                designer must assign the model using the 'Simulation.model'
                property before initializing the simulation.
            ``config:`` (:class:`despy.session.config`)
                Optional. Config object contains numerous simulation parameters.
                If omitted, a config object is created automatically with
                default settings. Configuration options can be set or read via
                either the 'Simulation.config' or 'Session.config' properties.
        """    
        self._session = Session()
        self._session.sim = self
        if model is not None:
            self._session.model = model
        if config is not None:
            self._session.config = config
        self._rep = 0
        self.dispatcher = Dispatcher()
        
        self.reset()
        
    def reset(self):
        """Resets the simulation to its initial state.
        
        Clears triggers, sets current rep to 0, sets time to the
        initial time, and clears the FEL and traces. Note that reset
        does not reset the model to its initial condition. 
        """

        self._triggers = OrderedDict()
        self._rep = 0
        self._setups = 0
        self._evt = None
        self._now = self._session.config.initial_time * 10
        self._pri = 0
        self._futureEventList = []
        self._counter = count()
        self.results = Results(self)
        self.results.stats["event_counter"] = Counter("event_counter")
        
    @property
    def session(self):
        """Returns the current Session object. Read-only.
        
        *Type:* :class:`despy.session.Session`
        """
        return self._session

    @property
    def config(self):
        """The assigned :class:`despy.session.Config` object.
        """
        return self._session.config
    
    @config.setter
    def config(self, config):
        self._session.config = config

    @property
    def model(self):
        """The model that is assigned to the Simulation object.
        
        *Type:* :class:`despy.model.component.Component`
        """
        return self._session.model
    
    @model.setter
    def model(self, model):
        self._session.model = model

    @property
    def rep(self):
        """Integer representing the current replication. Read-only.
        
        Starts at zero, i.e., rep = 0 for the first replication.
        """
        return self._rep
                
    @property
    def now(self):
        """The current time for the current replication.
        
        *Type:* Integer
        
        By default, a simulation starts at time zero and continues until no
        events remain on the FEL or until the simulation detects a stop
        condition. The unit of time represented by this integer has no impact
        on the simulation.
        
        Internally, Despy multiplies the time by a factor of ten and
        each _step in the simulation is a multiple of ten. This allows
        assignment of priorities to each event. For example, for events
        scheduled to run at time now = 4 (internal time = 40), 
        ``Priority.EARLY`` events would be scheduled to run at time 39,
        ``Priority.DEFAULT`` events at time 40, and ``Priority.LATE``
        events at time 41. Despy would indicate that all of these events
        occurred at time = 4 in standard reports and output. This
        practice simplifies the run() method because
        events are placed on the FEL in the order that they will
        actually be run, taking priorities into account.
        """
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10

    @property
    def event(self):
        """The event that is currently being executed by the simulation.
        
        *Type:* :class:`despy.event.Event`
        
        The event property equals 'None' except when an event's do_event()
        method is executing (see Simulation._step() method).
        
        """
        return self._evt

    @property
    def pri(self):
        """The priority of the current or most recently completed event.
        
        *Type:* Integer
        """
        return self._pri
    
    @property
    def triggers(self):
        """Ordered Dictionary containing simulation triggers.
        
        *Type:* {:class:`despy.model.trigger.AbstractTrigger`}
        
        A trigger is a method that will run whenever certain conditions are met.
        The simulation checks triggers after every event to see if the
        trigger conditions (runs AbstractTrigger.check())are met and if so,
        executes the trigger (runs AbstractTrigger.pull().
        """
        return self._triggers
#     
#     def display(self, data):
#         self._con.display(data)

    def add_trigger(self, key, trigger):
        err_msg = ("{0} object provided to Simulation.add_trigger() "
                "method must be a subclass of "
                "despy.model.trigger.Trigger or registered as a "
                "subclass using the Trigger.register() method")
        
        if issubclass(trigger.__class__, AbstractTrigger):
            self.triggers[key] = trigger
        else:
            raise TypeError(err_msg.format(repr(trigger)))

    def initialize(self):
        """Initializes all model components and seeds random number generators.
        
        The designer calls the initialize() method once, prior to running the
        simulation, regardless of the number of simulation replications. Code
        for setting up initial conditions for each replication should be placed
        in the model or component's setup() method, which will be called
        automatically by the Simulation.run() method.
        
        Designers may explicitly call initialize() method, or implicitly by
        by calling Simulation.irun() or simulation.irunf().
        """
        self.dispatcher.announce_phase("Initializing")    
            
        np.random.seed(self._session.config.seed)
        random.seed(self._session.config.seed)
        self.dispatcher.send_data("seed", self.config.seed)
                
        self._now = self._session.config.initial_time * 10
        self.dispatcher.send_data("initial_time", self._now)      
        
        self.model.dp_initialize()
        self.dispatcher.announce("All Components Initialized.")          

    def _setup(self):
        """Resets simulation for the next rep and calls model setup() methods.

        Called automatically by Simulation.run() method at the beginning of
        each replication.
        * Clears the FEL
        * Resets counters.
        * Resets time to config.initial_time.
        * Calls every model component's setup() method.
        """
        self.dispatcher.announce_phase("Setup Rep #{} ".format(self.rep))
        if self.rep > 0:
            self._now = self._session.config.initial_time * 10
            self._pri = 0
            self._futureEventList = []
            self._counter = count()
            
        self._session.model.dp_setup()        
        for _, stat in self._statistics.items():
            stat.setup()
    
    def _teardown(self):
        """Calls all Component.teardown() methods at the end of each rep.
        """
        self.dispatcher.announce_phase("Teardown Rep #{} ".format(self.rep))
        self._session.model.dp_teardown(self.now)
        for _, stat in self._statistics.items():
            stat.teardown()

    def finalize(self):
        """Calls Component.finalize() methods, returns a results object.
        
        *Returns:* :class:`despy.output.results`
        
        The designer can call finalize() explicitly following the run() method,
        or the designer can call finalize implicitly by calling irunf() or
        runf().
        """
        self.dispatcher.announce_phase("Finalizing")
        self._session.model.dp_finalize()
        for _, stat in self._statistics.items():
            stat.finalize()
        return self.results

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
    
    def schedule(self, event, delay=0, priority=Priority.STANDARD):
        """ Add an event to the FEL.

        *Arguments*
            event (:class:`despy.event.Event`):
                An instance or subclass of the ``Event`` class.
            delay (integer):
                A non-negative integer that defaults to zero. If zero,
                the event will be scheduled to occur immediately.
            priority (integer)
                An attribute of the
                :class:`despy.event.Priority` enumeration, or
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

    def run(self, until=None, resume_on_next_rep = False):
        """ Execute events on the FEL until reaching a stop condition.
        
        The ``run`` method will advance simulation time and execute each
        replication until the FEL is empty or until the time specified
        in the ``until`` parameter is reached.

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
            resume_on_next_rep (Boolean):
                Default is false. When resuming a simulation, if
                resume_on_next_rep is 'True', the simulation will skip
                any remaining events in the current rep and skip to the
                next rep.                
        """
        self.dispatcher.announce_phase("Running")
        self._set_triggers(until)
        run_start_time = datetime.datetime.today()
        self.dispatcher.send_data("run_start_time", run_start_time)

        if resume_on_next_rep:
            self._rep += 1
        start_rep = self._rep            
        for rep in range(start_rep, self._session.config.reps):
            self._rep = rep
            if self._setups <= self._rep:
                self._setup()
                self._setups += 1

            # Step through events on FEL and check triggers.
            continue_rep = True
            while continue_rep:
                try:
                    self._step()
                except NoEventsRemainingError:
                    break
                continue_rep = self._check_triggers()
        
            # Finalize model and setup for next replication
            self._teardown()
        
        self.dispatcher.announce_phase("Simulation Completed")
        run_stop_time = datetime.datetime.today()
        self.dispatcher.send_data("run_stop_time", run_stop_time)
        self.dispatcher.send_data("elapsed_time",
                                  run_stop_time - run_start_time)

    def _set_triggers(self, until):
        """Sets a TimeTrigger that ends the simulation at time = until.
        
        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. If 'None', deletes
                any existing TimeTriggers.
        """
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

    def _step(self):
        """Advance simulation time and execute the next event.

        *Raises*
            NoEventsRemaining:
                Occurs if no more events are scheduled on the FEL.
                
        *Returns*
            :class:`despy.simulation.FutureEvent`
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

        # Run event
        self._evt = fel_item.event
        fel_item.event.dp_do_event()
        self._evt = None
        self._statistics["event_counter"].increment()
        return fel_item

    def _check_triggers(self):
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
    
    def irun(self, until = None):
        """Initializes and runs the simulation, but does not finalize.
        
        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. Defaults to 'None'.
                See Simulation.run() for additional information.
        """
        self.initialize()
        self.run(until = until)
        
    def irunf(self, until = None):
        """Initializes, runs, and finalizes the simulation.
                
        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. Defaults to 'None'.
                See Simulation.run() for additional information.
        """
        self.initialize()
        self.run(until = until)
        return self.finalize()
        
    def runf(self, until = None, resume_on_next_rep = False):
        """Runs and finalizes the simulation.
                
        *Arguments*
            until (integer):
                A non-negative integer specifying the simulation time
                at which the simulation will stop. Defaults to 'None'.
                See Simulation.run() for additional information.
        """
        self.run(until = until, resume_on_next_rep = resume_on_next_rep)
        return self.finalize()

    def add_message(self, message, fields):
        """Add a message to the trace report.
        
        *Arguments:*
            `message` (String)
                A short message that will be saved to the Trace.
            `fields` (Python dictionary)
                Custom fields that will be added to the TraceRecord.
                Optional. Defaults to None.
        """
        if self.event is None:
            self.results.trace.add_message(message, fields)
        else:
            self.event.add_message(message, fields)
    
    def get_data(self):
        """ Get a Python list with simulation parameters and results.
        
        The despy.output.results.write_files() method calls the get_data
        method of the simulation and model objects and places the data
        in the simulation report. The method will also call the user-
        defined get_data methods from all of the model components.
        
        *Returns*
            A Python list of tuples. The first item of each tuple is
            a member of the :class:`despy.output.datatype.Datatype`
            enumeration, which describes the structure of the data
            item (e.g., paragraph, list, etc.).
            
        """      
        output = [(Datatype.title, "Simulation"),
                  (Datatype.param_list,
                    [('Generator Folder',
                        self._session.config.folder_basename),
                     ('Seed', self.results.seed),
                     ('Start Time', self.results.run_start_time),
                     ('Stop Time', self.results.run_stop_time),
                     ('Elapsed Time', self.results.elapsed_time)])
                  ]
        return output