#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
from despy.output.report import HtmlReport
"""
********************
despy.output.results
********************

..  autosummary::

    
..  todo::

    Pull title-ize feature (replace().title() out to static helper
    function.

"""
import os
from collections import OrderedDict, namedtuple

from despy.session import Session
from despy.model.abstract import AbstractModel
from despy.output.trace import Trace
# from despy.output.trace import Trace

class Values(namedtuple('Result', ['value', 'label', 'description'])):
    """Tuple containing a simulation result."""

class Results(object):
    def __init__(self, owner):
        if isinstance(owner, AbstractModel):
            self._owner = owner.name
            self._top = False
        elif hasattr(owner, "irunf"):
            self._owner = "Simulation"
            self._top = True
            self.trace = Trace()
        else:
            raise TypeError("Owner argument must be type despy.simulation."
                            "Simulation or despy.model.component.Component. "
                            "Type {} was passed instead.".format(type(owner)))
             
        self._session = Session()
        self._vals = OrderedDict()
        self.stats = OrderedDict()
        self.res = OrderedDict()

    def __iter__(self):
        for results in self.results:
            for res in results:
                yield res
        yield self
        
    def __getattr__(self, key):
        if key in self._vals.keys():
            return self._vals[key]
        elif key in self.res.keys():
            return self.res[key]
        elif key in self.stats.keys():
            return self.stats[key]
        else:
            raise AttributeError("{0} is not a property of {1} Results "
                                 "object.".format(key, self._owner))
            
    def __getitem__(self, key):
        if key in self._vals.keys():
            return self._vals[key]
        elif key in self.res.keys():
            return self.res[key]
        elif key in self.stats.keys():
            return self.stats[key]
        else:
            raise AttributeError("{0} is not a property of {1} Results "
                                 "object.".format(key, self._owner))

    @property
    def vals(self):
        return self._vals
    
    def set_value(self, key, value, label = None, overwrite = False):
        if not overwrite and ((key in self.res.keys()) or
                (key in self.stats.keys()) or (key in self._vals.keys())):
            raise KeyError("'{}' already exists in Results object"
                           ".".format(key))
        if label is None:
            label = key.replace('_', ' ').title()
        self._vals[key] = (label, value)
        return label
        
    @property
    def seed(self):
        """Random number generator seed used for simulation. Read-only
        
        *Type:* ``None`` or Integer
        """
        return self._seed
        
    @property
    def report(self):
        return self._report
    
    def __str__(self):
        output = "\n=====Simulation Results==========\n"
        
        for _, value in self._values.items():
            output += "{0}: {1}\n".format(value[0], value[1])

        return output
    
    def write_files(self):
        """Creates trace and HTML reports in folder_basename location.
        """
        self._report = HtmlReport()
        
        # Take no action if no output folder specified.
        if not self._session.config.write_files:
            return None
        if self._session.config.folder_basename is None:
            return None
        
        # Finalize model and components.
        
        # Write trace csv file.
        self.set_full_path()
        self._trace.write_csv(self._full_path)
        
        #Get data for all components and create HTML report.
        self.report.append_output(self._sim.get_data())
            
        for _, component in self._mod.components.items():
            output = component.get_data(self._full_path)
            if output is not None:
                self._report.append_output(output)
        
        self._report.write_report(self._full_path)
        
    def set_full_path(self):
        """Adds time-stamp to end of Generator.folder_basename.
        
        The time-stamp is the stop time for the simulation.
        """
        timestamp = \
                self._values["run_stop_time"][1].strftime('_%y_%j_%H_%M_%S')
        self._full_path = (self._session.config.folder_basename +
                           '/Run' + timestamp)
                
        if not os.path.exists(self._full_path):
            os.makedirs(self._full_path) 
            
    def get_data(self, full_path):
        """Subclasses should override this method to provide simulation
        output that will be included in the output report.
        
        The output is a Python list of two-element tuples. The first
        element of each tuple is a :class:`despy.output.report.DataType`
        enumeration that determines how the rest of the tuple will be
        presented in the output report:

          * *Datatype.title:* The first element is the *Datatype.title
            enumeration* value and the second element is a string that
            will be displayed as a heading element in the html output
            report, or equivalent formatting for other output report
            formats.
          * *Datatype.paragraph:* The first element is the
            *Datatype.paragraph* enumaration value and the second
            element is a string that will be displayed as a paragraph
            element in the html output report, or equivalent formatting
            for other output report formats.
          * *Datatype.param_list:* The first element is the
            *Datatype.param_list enumeration value and the second
            element is a list with one or more two-element sub-tuples.
            The first element of the sub-tuples is a string caption
            describing the parameter, and the second element is the
            parameter. The *Datatype.param_list* will be displayed in
            the output report as a list of parameters with descriptive
            captions.
          * *Datatype.image:* The first element is the *Datatype.image*
            enumeration value and the second element is the image
            filename. The image will be displayed in the output report.
            
        The order of the datatypes in the output report will be the
        same as the order in the Python list that is returned from this
        method. Here is an example of the output from the
        :class:`despy.model.queue.Queue` class: ::
        
          output = [(Datatype.title, "Queue Results: {0}".format(self.name)),
                     (Datatype.paragraph, self.description.__str__()),
                     (Datatype.param_list,
                        [('Maximum Time in Queue', np.amax(qtimes)),
                         ('Minimum Time in Queue', np.amin(qtimes)),
                         ('Mean Time in Queue', np.mean(qtimes))]),
                     (Datatype.image, qtime_filename)]
        """
        return None

