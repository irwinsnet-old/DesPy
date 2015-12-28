..  currentmodule:: despy.simulation

###########################
despy.simulation.Simulation
###########################

*****************
Class Description
*****************

..  autoclass:: Simulation

**********
Properties
**********
..  autoattribute:: Simulation.session
..  autoattribute:: Simulation.config
..  autoattribute:: Simulation.model
..  autoattribute:: Simulation.rep
..  autoattribute:: Simulation.now
..  autoattribute:: Simulation.event
..  autoattribute:: Simulation.pri
..  autoattribute:: Simulation.triggers
..  autoattribute:: Simulation.run_start_time
..  autoattribute:: Simulation.run_stop_time

********************
Public Methods
********************
..  automethod:: Simulation.__init__
..  automethod:: Simulation.reset
..  automethod:: Simulation.add_trigger
..  automethod:: Simulation.initialize
..  automethod:: Simulation.finalize
..  automethod:: Simulation.peek
..  automethod:: Simulation.schedule
..  automethod:: Simulation.run
..  automethod:: Simulation.irun
..  automethod:: Simulation.irunf
..  automethod:: Simulation.runf
..  automethod:: Simulation.add_message
..  automethod:: Simulation.get_data

***************
Private Methods
***************
..  automethod:: Simulation._setup
..  automethod:: Simulation._teardown
..  automethod:: Simulation._set_triggers
..  automethod:: Simulation._step
..  automethod:: Simulation._check_triggers