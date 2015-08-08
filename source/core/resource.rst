..  currentmodule:: despy.core.resource

############################
despy.core.resource.Resource
############################

*****************
Class Description
*****************
..  autoclass:: Resource

********
__init__
********
..  automethod:: Resource.__init__

**********
Attributes
**********
..  autoinstanceattribute:: Resource.capacity
..  autoattribute:: Resource.res_queue
..  autoattribute:: Resource.service_time
..  autoattribute:: Resource.Station_tuple
..  autoattribute:: Resource.stations

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
..  automethod:: Resource.__str__
..  automethod:: Resource.__getitem__
..  automethod:: Resource.__setitem__
..  automethod:: Resource.get_available_station
..  automethod:: Resource.request
..  automethod:: Resource.get_service_time
..  automethod:: Resource.start_service
..  automethod:: Resource.finish_service
..  automethod:: Resource.remove_entity

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
