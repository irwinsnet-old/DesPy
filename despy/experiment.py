
from heapq import heappush, heappop
from itertools import count
from collections import namedtuple

#TODO: Make ID an event attribute
#TODO: Remove delay as an event attribute.
#TODO: Move priority to felTuple from event attribute
#TODO: Subclass experiment to named item.

class FelItem(namedtuple('FelItem', ['fel_time', 'fel_event', 'fel_priority'])):
    
    PRIORITY_EARLY = -1
    PRIORITY_STANDARD = 0
    PRIORITY_LATE = 1

class Experiment(object):

    """ Schedule events and manage the future event list (FEL).

    *Constructor Arguments*
        initial_time (integer):
            A non-negative integer that defaults to zero.
    """

    def __init__(self, initial_time = 0):
        """Initialize the event object.
        """
        self.console_output = True
        self.traceTuple = namedtuple('traceTuple',
                                     ['time', 'evt_name'])
        self._models = []
        self.event_trace = []
        self.reset(initial_time)

    @property
    def now(self):
        """The current time of the experiment. The time is a unit-less
        integer."""
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10

    @property
    def name(self):
        """Gets the name of the experiment.
        
        *Returns:* A short string.
        
        """
        return self._name

    @name.setter
    def name(self, experimentName):
        """Sets the name of the experiment.
        
        *Arguments*
            modelName (string):
                A short string that describes the experiment.

        """
        self._name = experimentName

    @property
    def console_output(self):
        return self._console_output
    
    @console_output.setter
    def console_output(self, output):
        self._console_output = output
        
    @property
    def models(self):
        """Get a list of all models attached to the experiment.
        
        *Returns:* A list of despy.model.Model objects.
        """
        return self._models
    
    def append_model(self, model):
        """ Append a model object to the experiment.
        
        *Arguments*
            model:
                A despy.model.Model object.
        """
        self._models.append(model)

    def schedule(self, event, delay = 0, priority = FelItem.PRIORITY_STANDARD):
        """ Add an event to the FEL.

        *Arguments*
            event (despy.Event):
                An instance or subclass of the despy.Event class.
            delay (integer):
                A non-negative integer that defaults to zero, meaning
                the event will be scheduled to occur mmediately.

        """
        if event.delay != None:
            delay = event.delay
        
        # Places a tuple onto the FEL, consisting of the event time, ID,
        # and event object.
        scheduleTime = self._now + (delay * 10) + priority
        
        heappush(self._futureEventList,
                 FelItem(fel_time = scheduleTime, fel_event = event,
                         fel_priority = priority))

    def peek(self):
        """Return the time of the next scheduled event, or infinity if there
        is no remaining events.
        """
        try:
            return int((self._futureEventList[0].fel_time - \
                    self._futureEventList[0].fel_priority) / 10)
        except IndexError:
            return float('Infinity')
        
    def initialize_models(self):
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
            current_FEL_item = heappop(self._futureEventList)
        except IndexError:
            raise NoEventsRemainingError
        else:
            self.now = int((current_FEL_item.fel_time - \
                    current_FEL_item.fel_priority) / 10)

        #Run event
        current_FEL_item.fel_event.do_event()
        
        #Record event in trace report
        eventRecord = current_FEL_item.fel_event.get_event_record()
        self.event_trace.append(eventRecord)
        if self.console_output:
            consoleOutput = str(eventRecord.time).rjust(8) + \
                ':   ' + eventRecord.evt_name
            print(consoleOutput)
        
        return current_FEL_item

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

        self.initialize_models()
        
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

    def reset(self, initial_time = 0):
        """Reset the simulation time to zero so the simulation can be
        rerun.
        """
        self._now = initial_time * 10
        self._futureEventList = []
        #  Each event gets a unique integer ID, starting with 0 for the first
        #event.
        self._eventId = count()
        self.event_trace = []
        for model in self.models:
            model.initial_events_scheduled = False


class NoEventsRemainingError(Exception):
    pass