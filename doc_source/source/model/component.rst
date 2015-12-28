.. currentmodule:: despy.model.component

###############################
despy.model.component.Component
###############################

.. autoclass:: Component

**********
Properties
**********
..  autoattribute:: Component.name
..  autoattribute:: Component.slug
..  autoattribute:: Component.description
..  autoattribute:: Component.session
..  autoattribute:: Component.sim
..  autoattribute:: Component.model
..  autoattribute:: Component.owner
..  autoattribute:: Component.number
..  autoattribute:: Component.id
..  autoattribute:: Component.statistics
..  autoattribute:: Component.components

**************
Public Methods
**************

..  automethod:: Component.add_component
..  automethod:: Component.set_counter
..  automethod:: Component.initialize
..  automethod:: Component.setup
..  automethod:: Component.teardown
..  automethod:: Component.finalize
..  automethod:: Component.get_data

*************
Magic Methods
*************

..  automethod:: Component.__iter__
..  automethod:: Component.__str__

****************************
Private and Internal Methods
****************************

..  automethod:: Component._get_next_number
..  automethod:: Component._call_phase
..  automethod:: Component.dp_initialize
..  automethod:: Component.dp_setup
..  automethod:: Component.dp_teardown
..  automethod:: Component.dp_finalize