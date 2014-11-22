.. Despy documentation master file, created by
   sphinx-quickstart on Fri Nov 21 06:43:34 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Despy
=====

**A Discrete Event Simulation Framework for Python**

Despy is a discrete event simulation framework that is written in Python 3.4
and is heavily influenced by DESMO-J and SimPy. I wrote Despy primarily to
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
  mainstream packages that are available in the Anaconda Python stack.
  Despy relies heavily on Numpy and Matplotlib.

.. todo::

   Add hyperlinks to Anaconda, Numpy, DESMO-J, Simpy, Matplotlib, etc.

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

