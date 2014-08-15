
from heapq import heappush, heappop
from itertools import count
from collections import namedtuple

class Environment(object):

    """ Schedule events and manage the future event list (FEL).

    *Constructor Arguments*
        initial_time (integer):
            A non-negative integer that defaults to zero.
    """

    def __init__(self, initial_time = 0):
        """Initialize the event object.
        """
        self._now = initial_time * 10
        self._futureEventList = []
        #  Each event gets a unique integer ID, starting with 0 for the first
        #event.
        self._eventId = count()
        self.console_output = True
        self.felTuple = namedtuple('felTuple', ['time', 'id', 'evt'])
        self.eventTrace = []
        self.traceTuple = namedtuple('traceTuple',
                                     ['time', 'evt_name'])

    @property
    def now(self):
        """The current time of the environment. The time is a unit-less
        integer."""
        return int(self._now / 10)
    
    @now.setter
    def now(self, time):
        self._now = time * 10

    @property
    def name(self):
        """Gets the name of the environment.
        
        *Returns:* A short string.
        
        """
        return self._name

    @name.setter
    def name(self, environmentName):
        """Sets the name of the environment.
        
        *Arguments*
            modelName (string):
                A short string that describes the environment.

        """
        self._name = environmentName

    @property
    def console_output(self):
        return self._console_output
    
    @console_output.setter
    def console_output(self, output):
        self._console_output = output

    def schedule(self, event, delay = 0):
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
        scheduleTime = self._now + (delay * 10) + event.priority
        
        
        heappush(self._futureEventList,
                 self.felTuple(time = scheduleTime, id = next(self._eventId),
                          evt = event))

    def peek(self):
        """Return the time of the next scheduled event, or infinity if there
        is no remaining events.
        """
        try:
            return int((self._futureEventList[0].time - \
                    self._futureEventList[0].evt.priority) / 10)
        except IndexError:
            return float('Infinity')

    def step(self):
        """Advance simulation time to the next time on the FEL and
        executes the next event.

        *Raises*
            NoEventsRemaining:
                Occurs if no more events are scheduled on the FEL.
        """

        # FEL items are tuples in format (eventTime, event ID, event)
        try:
            current_FEL_item = heappop(self._futureEventList)
        except IndexError:
            raise NoEventsRemaining
        else:
            self.now = int((current_FEL_item.time - \
                    current_FEL_item.evt.priority) / 10)

        #Run event
        current_FEL_item.evt.doEvent()
        
        #Record event in trace report
        eventRecord = current_FEL_item.evt.getEventRecord()
        self.eventTrace.append(eventRecord)
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

        if isinstance(until, int):
            stopTime = until
            while self.now <= stopTime:
                try:
                    self.step()
                except NoEventsRemaining:
                    break

        else:
            while True:
                try:
                    self.step()
                except NoEventsRemaining:
                    break

class NoEventsRemaining(Exception):
    pass