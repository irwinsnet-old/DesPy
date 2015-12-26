..  currentmodule:: despy.core.event

######################
despy.core.event.Event
######################

*****************
Class Description
*****************
..  autoclass:: Event

********
__init__
********
..  automethod:: Event.__init__

**********
Attributes
**********
..  autoattribute:: Event.trace_fields
..  autoattribute:: Event.trace_records

********************
Inherited Attributes
********************
..  autoattribute:: despy.base.named_object.NamedObject.name
    :noindex:
..  autoattribute:: despy.base.named_object.NamedObject.description
    :noindex:
..  autoattribute:: despy.base.named_object.NamedObject.slug
    :noindex:
..  autoattribute:: despy.core.component.Component.mod
    :noindex:
..  autoattribute:: despy.core.component.Component.sim
    :noindex:
..  autoattribute:: despy.core.component.Component.number
    :noindex:
..  autoattribute:: despy.core.component.Component.id
    :noindex:

*******
Methods
*******
..  automethod:: Event.append_callback
..  automethod:: Event.add_trace_field

*****************
Inherited Methods
*****************
..  automethod:: despy.core.component.Component.initialize
    :noindex:
..  automethod:: despy.core.component.Component.finalize
    :noindex:
..  automethod:: despy.core.component.Component.get_data
    :noindex:
..  automethod:: despy.core.component.Component.set_counter
    :noindex:

****************
Internal Methods
****************
..  automethod:: Event._do_event
..  automethod:: Event._update_trace_record
..  automethod:: Event._reset
..  automethod:: Event.__lt__
..  automethod:: Event.__gt__
