Getting Started With Despy
==========================

Required Software
-----------------
1. Python version 3.4 or later. http://www.python.org/
2. The Despy package from Github.  http://github.com/irwinsnet/DesPy
3. The following SciPy extension modules, available from http://scipy.org/

   * `Numpy <http://docs.scipy.org/doc/numpy/>`_
   * `Scipy <http://docs.scipy.org/doc/scipy/reference/>`_
   * `Matplotlab <http://matplotlib.org/contents.html>`_
   * `IPython <http://ipython.org/ipython-doc/stable/index.html>`_

Installation
------------
1. Install Python and the SciPy extension modules. They can be
   installed separately, or installed together, using one of several free
   `Python distributions <https://wiki.python.org/moin/PythonDistributions>`_
   that are readily available . I used the
   `Anaconda distribution <https://ww w.continuum.io/downloads>`_ to
   develop and test Despy.
2. Obtain the Despy package from
   `Github <https://github.com/irwinsnet/DesPy>`_. Either download the
   package as a zip file, or use the
   `git <https://git-scm.com/>`_ version control system to create your own
   Despy repository. Refer to Github's
   `instructions <https://help.github.com/articles/fetching-a-remote/>`_ 
   on cloning github respositories for additional details.

Configuration
-------------
Ensure Python can locate and import Despy modules. I accomplished
this on Windows by setting the ``PYTHONPATH`` environmental variable to
the folder containing the Despy repository. Refer to
https://docs.python.org/3/tutorial/modules.html or
https://docs.python.org/3/reference/import.html for more details on
Python modules or the Python import system.