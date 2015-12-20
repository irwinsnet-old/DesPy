#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
********************
despy.base.utilities
********************

..  autosummary::

    Priority
"""

from despy.core.trigger import AbstractTrigger

class Priority():
    """Define priorities for ordering events scheduled at the same time.
    
    **Priority Levels**
        The Priority class defines three constants that are used to
        prioritize events that are scheduled to occur at the same time.
        Events assigned a higher priority will occur before events that
        are assigned lower priorities.
        
        *Priority.STANDARD*
            Despy uses Priority.STANDARD as the default priority when no
            other priority is specified.
            
        *Priority.EARLY*
            Events assigned Priority.EARLY will be executed before
            Priority.STANDARD and Priority.LATE events.
            
        *Priority.LATE*
            Events assigned Priority.LATE will be executed after
            Priority.EARLY and Priority.STANDARD events.
            
        Events scheduled to occur at the same time with the same
        priority may be executed in any order.
        
        The priority integer value is added to the scheduled event time.
        Internally, Despy multiplies the scheduled time by 10. This
        means that events scheduled to occur at time 1 are internally
        scheduled for time 10, time 12 events would occur at internal
        time 120, etc. This scheduling mechanism allows priorities as
        high as 4 and as low as -4. A model that requires more than
        three different priorities probably needs to be redesigned,
        therefore, Despy only provides named constants for priorities
        from -1 to 1.
    """
    EARLY = -1
    STANDARD = 0
    LATE = 1
    
def check_trigger(trigger):
    if isinstance(trigger, AbstractTrigger):
        return True
    else:
        return False
