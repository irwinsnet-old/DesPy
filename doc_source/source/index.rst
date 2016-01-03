#######################################################
Despy - A Discrete Event Simulation Framework in Python
#######################################################

Full disclosure: I'm not a computer programmer. Despy is a hobby
project. My goals with this project are to improve my programming skills,
learn about discrete event simulation, and give myself something to do
on Sunday mornings besides read the comics. If someday this turns into
a functional framework for discrete event simulation, that's just icing.

*********
Resources
*********

Here are some resources for learning more about this framework:
  * :ref:`tutorial-toc`
  * :ref:`reference-toc`

**********
Background
**********

Despy is a discrete event simulation framework that is written in Python 3.5
and is heavily influenced by `DESMO-J <http://desmoj.sourceforge.net/>`_ and
`SimPy <https://simpy.readthedocs.org/en/latest/>`_. I wrote Despy primarily to
teach myself Python and to work through examples in the *Discrete Event
Simulation* text by Banks, Carson, Nelson, and Nicol.

I am concerned that as a scripted language, Python may be slow for
complex simulations, but so far I haven't had any speed issues.
Furthermore, for a hobby project like Despy, the benefits of the math,
statistics, and plotting packages that are available for Python
outweigh my speed concerns. If I run into problems in the future with
more complex simulations, then I'll have a follow-on hobby project:
teaching myself how to reprogram parts of the framework in C++.
 
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
* Eventually I would like to use Jinja or another template framework
  to give simulation designers the ability to generate custom reports.
  I also intend to set up the framework to allow Despy simulations to
  run within iPython. It will take a while (I have a day job) -- check
  back next year.
  
  
Despy is released under the
`MIT License <http://opensource.org/licenses/MIT>`_.

Copyright (c) 2015 Stacy Irwin  
   
**Conventions**
# Methods and attributes that begin with an underscore (_) are internal
methods. Internal methods are called by Despy classes, but are not
intended to be called by users who are building simulations. I've
included documentation for internal methods for developers who are
extending or revising this framework, and to help users understand
how Despy works.

*****************
Table of Contents
*****************
.. toctree::
   :maxdepth: 1

   toc

Links
=====
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

