#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
********
despy.dp
********

..  autosummary::

"""

EARLY = -1
STANDARD = 0
LATE = 1

class AbstractPackage():
    def __init__(self):
        import despy.abstract.model
        self.AbstractModel = despy.abstract.model.AbstractModel
        
abstract = AbstractPackage()
del AbstractPackage

class StatsPackage():
    def __init__(self):
        from despy.stats.random import get_empirical_pmf, get_poisson_pmf
        self.get_empirical_pmf = get_empirical_pmf
        self.get_poisson_pmf = get_poisson_pmf
        
stats = StatsPackage()
del StatsPackage

from despy.session import Session, Config  # @UnusedImport

class OutputPackage():
    def __init__(self):
        import despy.output.report
        self.HtmlReport = despy.output.report.HtmlReport
        self.Datatype = despy.output.report.Datatype
        
        import despy.output.results
            #IMPORTS despy.output.trace        
        self.results = despy.output.results.Results

        import despy.output.statistic
        self.AbstractStatistic = despy.output.statistic.AbstractStatistic
        self.DiscreteStatistic = despy.output.statistic.DiscreteStatistic
        self.TimeWeightedStatistic = (
                            despy.output.statistic.TimeWeightedStatistic)
        
        import despy.output.trace
        self.Trace = despy.output.trace.Trace
        self.TraceRecord = despy.output.trace.TraceRecord
        
        import despy.output.plot
        self.plot = despy.output.plot
        
        import despy.output.console
        self.console = despy.output.console
        
        import despy.output.counter
        self.Counter = despy.output.counter.Counter
        
output = OutputPackage()
del OutputPackage
        
class ModelPackage():
    def __init__(self):
        import despy.model.trigger
        self.AbstractTrigger = despy.model.trigger.AbstractTrigger
        self.TimeTrigger = despy.model.trigger.TimeTrigger
        
        import despy.model.component
        self.Component = despy.model.component.Component
        
        import despy.model.process
            #IMPORTS despy.fel.event
        self.Process = despy.model.process.Process
        self.ProcessTimeOutEvent = despy.model.process.ProcessTimeOutEvent
        
        import despy.model.queue
        self.Queue = despy.model.queue.Queue
        
        import despy.model.entity
        self.Entity = despy.model.entity.Entity
        
        import despy.model.resource
        self.Resource = despy.model.resource.Resource
        self.ResourceQueue = despy.model.resource.ResourceQueue
        self.ResourceFinishEvent = despy.model.resource.ResourceFinishServiceEvent
        
        import despy.model.timer
        self.RandomTimer = despy.model.timer.RandomTimer
        self.TimerEvent = despy.model.timer.TimerEvent
        
model = ModelPackage()
del ModelPackage

class FelPackage():
    def __init__(self):
        import despy.fel.event
        self.Event = despy.fel.event.Event
        
fel = FelPackage()
del FelPackage

from despy.simulation import Simulation  # @UnusedImport
