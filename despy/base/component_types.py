from despy.core.event import Event

def is_event(obj):
    return isinstance(obj, Event)

# TODO: Consider getting rid of this module -- does not appear to be used.