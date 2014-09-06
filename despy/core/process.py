from despy.core.root import _ModelMember, PRIORITY_STANDARD
from despy.core.event import Event
from collections import namedtuple

#TODO: Refactor processTuple. Make attribute names consistent with
#felItem class.
#TODO: change root module to root
#TODO: write test for queue.
#TODO: finish CSV trace.

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
        
    def schedule_timeout(self, name, delay, priority = PRIORITY_STANDARD):
        event = ProcessTimeOutEvent(self, name, priority)
        return self.processTuple(event_ = event, delay_ = delay)

    def call_process(self):
        scheduled_event = next(self._generator)
        self.model.schedule(scheduled_event.event_, scheduled_event.delay_)
        
    def reset_process(self):
        self.generator = self._generator()
        
    def start(self, delay = 0, priority = PRIORITY_STANDARD):
        self.model.schedule(ProcessTimeOutEvent(self, "Start " + self.name),
                            delay)
        
class ProcessTimeOutEvent(Event):
    def process_callback(self):
        self._process.call_process()
    
    def __init__(self, process, name, 
                 priority = PRIORITY_STANDARD):
        self._process = process
        super().__init__(process.model, name, priority)
        self.append_callback(self.process_callback)
