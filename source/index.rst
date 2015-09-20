Despy
=====

**A Discrete Event Simulation Framework for Python**

Despy is a discrete event simulation framework that is written in Python 3.4
and is heavily influenced by `DESMO-J <http://desmoj.sourceforge.net/>`_ and
`SimPy <https://simpy.readthedocs.org/en/latest/>`_. I wrote Despy primarily to
teach myself Python and to work through examples in the *Discrete Event
Simulation* text by Banks, Carson, Nelson, and Nicol.

I am concerned that as a scripted language, Python may be slow for complex
simulations, but so far I haven't had any speed issues. Furthermore, for a
hobby project like Despy, the benefits of the math, statistics, and plotting
packages that are available for Python outweigh my speed concerns. If I run
into problems in the future with more complex simulations, I'll reprogram parts
of the framework in C++.

My goals for despy are to:

* Support both event and process world views.
* Provide typical simulation output parameters (queue length, system
  time, utilization) by default.
* Support a high level of customization, but set sensible defaults for
  simulation parameters to reduce the amount of code needed to run a
  simulation.
* Write the simulation using only the standard Python library or
  mainstream packages that are available in the `Anaconda Python stack
  <https://store.continuum.io/cshop/anaconda/>`_. Despy relies heavily on
  `Numpy <http://www.numpy.org/>`_ and `Matplotlib <http://matplotlib.org/>`_.
  
Despy design principles:

* Clarity over convenience: While convenience is important, it's not
  worth breaking encapsulation of components and overly complicating
  the simulation. For example, I'll try to use sensible defaults for
  method parameters so no complicated multi-line statements are
  necessary to complete simple tasks. But overall, Despy should only
  do what the designer tells it to do, when the designer says to do it.
  
  
Despy is released under the
`MIT License <http://opensource.org/licenses/MIT>`_.

Copyright (c) 2015 Stacy Irwin


Contents:

.. toctree::
   :maxdepth: 2
   
   packages
   modules
   classes
   todo
   
   
**Conventions**
# Methods and attributes that begin with an underscore (_) are internal
methods. Internal methods are called by Despy classes, but are not
intended to be called by users who are building simulations. I've
included documentation for internal methods for developers who are
extending or revising this framework, and to help users understand
how Despy works.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

