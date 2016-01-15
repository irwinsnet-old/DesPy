#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
********************
despy.output.console
********************

..  autosummary::

    
..  todo::

"""
from IPython.display import display_html

from despy.session import Config

def test_table():
    raw_html = """<table>
                    <tr><td>Cell 1</td><td>Cell 2</td></tr>
                    <tr><td>Cell 3</td><td>Cell 4</td></tr>
                </table"""
                
    display_html(raw_html, raw = True)
    
class Console():
    def init(self, config):
        if isinstance(config, Config):
            self._config = config
        else:
            raise TypeError("Object passed to Console.__init__() must "
                            "be type despy.session.Config. Type {} "
                            "was passed instead".format(type(config)))
            
    @property
    def config(self):
        return self._config
    
    def print_trace_table(self):
        pass