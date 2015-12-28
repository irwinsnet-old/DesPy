#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
..  module:: despy.output.__init__
    :noindex:

The despy.ouput package contains classes and functions for creating
plots and reports that display the simulation results.


despy.output.trace
==================
..  automodule:: despy.output.trace
    :noindex:

despy.output.report
===================
..  automodule:: despy.output.report
    :noindex:
    
despy.output.plot
=================
..  automodule:: despy.output.plot
    :noindex:


"""

from despy.output.report import HtmlReport
from despy.output.results import Results
from despy.output.statistic import AbstractStatistic, DiscreteStatistic
from despy.output.statistic import TimeWeightedStatistic
from despy.output.trace import Trace, TraceRecord