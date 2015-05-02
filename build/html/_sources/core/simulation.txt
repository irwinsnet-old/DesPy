..  currentmodule:: despy.core.simulation

################################
despy.core.simulation.Simulation
################################

*****************
Class Description
*****************

..  autoclass:: Simulation

****************
Class Attributes
****************
..  autoattribute:: despy.base.named_object.NamedObject.name
    :noindex:
..  autoattribute:: despy.base.named_object.NamedObject.description
    :noindex:

..  autoattribute:: Simulation.models
..  autoattribute:: Simulation.seed
..  autoattribute:: Simulation.now
..  autoattribute:: Simulation.evt
..  autoattribute:: Simulation.run_start_time
..  autoattribute:: Simulation.run_stop_time
..  autoattribute:: Simulation.gen

*************
Class Methods
*************
..  automethod:: Simulation.__init__
..  automethod:: Simulation.append_model
..  automethod:: Simulation.schedule
..  automethod:: Simulation.peek
..  automethod:: Simulation.step
..  automethod:: Simulation.run
..  automethod:: Simulation.get_data
..  automethod:: Simulation.reset

**************************
Internal (Private) Methods
**************************
These methods are not intended to be called by the user. They
should be considered private.

..  automethod:: Simulation._initialize_models