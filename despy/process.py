from despy.root import _ModelMember
from despy.event import Event
from collections import namedtuple

#TODO: Create method for process to initially schedule itself.

class Process(_ModelMember):
    """Represents a simulation process that periodically schedules events and
    maintains state (i.e., retains variable values) between events.
    """

    def __init__(self, model, name, generator_method):
        """Creates a process object.
        
        *Arguments*
            model (despy.model.Model
                A despy.Model object that contains the process object.
            name (String):
                A short string that will be displayed in trace reports
                and other outputs.
        """
        self._name = name
        self._model = model
        self._generator = generator_method(self)
        self.processTuple = namedtuple('processTuple', ['event_', 'delay_'])
        
    def schedule_timeout(self, name, delay, priority = Event.PRIORITY_STANDARD):
        event = ProcessTimeOutEvent(self, name, priority, delay)
        return self.processTuple(event_ = event, delay_ = delay)

    def call_process(self):
        scheduled_event = next(self._generator)
        self.model.schedule(scheduled_event.event_, scheduled_event.delay_)
        
    def reset_process(self):
        self.generator = self._generator()
        
    def start(self, delay = 0, priority = Event.PRIORITY_STANDARD):
        self.model.schedule(ProcessTimeOutEvent(self, "Start " + self.name),
                            delay)
        
class ProcessTimeOutEvent(Event):
    def process_callback(self):
        self._process.call_process()
    
    def __init__(self, process, name, 
                 priority = Event.PRIORITY_STANDARD, delay = None):
        self._process = process
        super().__init__(process.model, name, priority, delay)
        self.append_callback(self.process_callback)

    def do_event(self):
        """Executes the callback functions that are on the event's
        callback list. _do_event() is called by the environment's step
        method.
        
        """
        if len(self._callbacks)==0:
            return None
        else:
            for callback in self._callbacks:
                callback()
            return True
        

        