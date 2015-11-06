#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
******************
despy.core.process
******************
   
..  autosummary::

    Process
    
    
..  todo::

    Refactor processTuple. Make attribute names consistent with felItem
    class. Make a class attribute.

    Determine if check for function of method type on generator function
    is necessary. Will need to do test with independent generator
    function.

    Test sleep and wake methods.

    Have sleep method write a trace record.
    
    Refactor to use a Callback object.
"""

from collections import namedtuple
import types

from despy.core.component import Component
from despy.core.event import Event
from despy.base.utilities import Priority

class Process(Component):
    """Portion of a real-world system, including events and parameters.
        
    The Process class supports process style simulations. It allows the
    designer to implement a generator function that adds events to the
    FEL that represent a sequence of real-world activities. The
    generator function has parameters that are maintained between
    events. Designers can use processes to simulate the entire lifetime
    of an entity or portion of the system.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
    
    **Members**
    
    .. autosummary::
    
        awake
        generator
        start
        call
        schedule_timeout
        sleep
        wake
        reset_process

    """

    def __init__(self, name, generator_function = None):
        """Creates a process object.
        
        Designers should either pass a generator function object into
        the __init__ method when instantiating the process class, or
        should set the Process.generator attribute in the __init__
        method of a class that inherits from the Process class.
        Subclass __init__ methods should call the Process.__init__
        method.
        
        *Arguments*
            ``model`` (despy.model.Model
                A despy.Model object that contains the process object.
            ``name`` (String):
                A short string that will be displayed in trace reports
                and other outputs.
            ``generator_function`` (Python function object)
                Function object that uses the Python ``yield`` statement
                to pause until some time in the future. Optional.
        """
        super().__init__(name)
        
        self.processTuple = namedtuple('processTuple', ['event_',
                                                        'delay_',
                                                        'priority_'])
        self._awake = False
        
        if generator_function != None:
            self._generator = generator_function
            
        if isinstance(self.generator, types.FunctionType):
            self._iterator = self.generator(self)
        elif isinstance(self.generator, types.MethodType):
            self._iterator = self.generator()
        else:
            raise TypeError(\
                "generator_method must be a function or class method")
            
    @property
    def awake(self):
        """True if process is active, False otherwise. Read only.
        
        *Type:* (Boolean)
        """
        return self._awake
    
    @property
    def generator(self):
        """The generator function that defines the process.
        
        Note that the generator function returns an iterator object,
        which in turn executes the code contained in the generator
        function. The generator function is called once, during
        initialization of the simulation. During execution, the
        simulation calls the self._iterator object that is created by
        the generator.
        
        *Type:* Python function object.
    """
        return self._generator
    
    @generator.setter
    def generator(self, generator_function):
        self._generator = generator_function
        
    def start(self, delay = 0, priority = Priority.STANDARD):
        """Schedules a process start event on the FEL.
        
        *Arguments*
            ``delay`` (Integer)
                Defaults to zero, meaning the process start event will
                occur at the current time. Otherwise process start is
                delayed by *delay* time units.
            ``priority``
                Priority of the process start event. Defaults to
                Priority.STANDARD.
        """
        self.sim.schedule(ProcessTimeOutEvent(self,
                            "Start " + self.name), delay, priority)
        self._awake = True

    def call(self):
        """Calls the iterator and schedules resulting event on FEL.
        """
        scheduled_event = next(self._iterator)
        if scheduled_event != None:
            if self.awake:
                self.sim.schedule(scheduled_event.event_,
                                    scheduled_event.delay_,
                                    scheduled_event.priority_)
        
    def schedule_timeout(self, name, delay = 0,
                         priority = Priority.STANDARD,
                         trace_fields = None):
        """Returns a ProcessTimeOutEvent.
        
        Designers can use this method with the yield statement in the
        generator function to pause the process and resume at a
        specific future time.
        
        *Arguments*
            ``name`` (String)
                Name of the scheduled event.
            ``delay`` (Integer)
                Defaults to zero, meaning the process timeout event will
                occur at the current time. Otherwise process times out
                until *delay* time units have elapsed.
            ``trace_fields`` (Python dictionary object)
                Data in trace_fields dictionary will be added to the
                event's record in the trace report.
                
        *Returns:* Process.processTuple namedtuple.
        """
        event = ProcessTimeOutEvent(self, name, trace_fields)
        return self.processTuple(event_ = event,
                                 delay_ = delay,
                                 priority_ = priority)
        
    def sleep(self):
        """Stops the process and sets Process.awake attribute to False.
        """
        self._awake = False
    
    def wake(self, delay = 0, priority = Priority.STANDARD):
        """Restarts a sleeping processes.
        
        *Arguments*
            ``delay``
                Defaults to zero, meaning the process will wake at the
                current time. Otherwise process will not wake until
                *delay* time units have elapsed.
            ``priority``
                Priority for waking the process. Defaults to
                Priority.STANDARD.
        """
        if not self.awake:
            self.sim.schedule(ProcessTimeOutEvent(self,
                                "Wake " + self.name), delay, priority)
            self._awake = True

    def reset_process(self):
        """Returns process to initial conditions by replacing iterator.
        """
        self._iterator = self.generator
        
class ProcessTimeOutEvent(Event):
    """Restarts a process after a specified time interval has elapsed.
    
    The callback method for a ProcessTimeOutEvent calls the process
    object's iterator method.

    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      * :class:`despy.core.event.Event`
    
    **Attributes**
      * :attr:`ProcessTimeOutEvent.process`: The applicable Process
        object. Read only.
        
    **Methods**
      * :meth:`ProcessTimeOutEvent.process_callback`: Calls process
        iterator when event is executed by FEL.
      * :meth:`ProcessTimeOutEvent.dp_update_trace_record`: Can be
        sub-classed to modify event trace record.
    """
    
    def __init__(self, process, name, trace_fields = None):
        self._process = process
        super().__init__(name, trace_fields)
        
    @property
    def process(self):
        """The applicable Process object. Read only.
        
        *Type*: :class:`despy.core.process.Process`
        """
        return self._process
    
    def do_event(self):
        """Calls process iterator when event is executed by FEL.
        """
        self.process.call()
        
    def dp_update_trace_record(self, trace_record):
        """Can be sub-classed to modify event trace record.
        
        *Arguments*
            ``trace_record`` (Python dictionary)
                The default trace record that is created by the trace
                object.
        """
        return super().dp_update_trace_record(trace_record)
