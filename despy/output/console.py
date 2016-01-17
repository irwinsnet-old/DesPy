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
from IPython.display import display_html, HTML, display
#from colorama import Fore, Style, Back, init

from despy.session import Session

#init()

class Con():
    def init(self):
        self._session = Session()
    
    def display(self, data):
        if isinstance(data, dict):
            for lbl, value in data:
                print(lbl, ": ".format(value))
        print(data)
        
    def display_value(self, label, data):
        print("{0}: {1}".format(label, data))
        
    def display_list(self, label, list_data):
        output = "{}: ".format(label)
        for value in list_data[0:-1]:
            output += "{}, ".format(value)
        output += list_data[-1]
        print(output)
        
    def display_header(self, header):
        print("====={}==========".format(header))
        
    def display_trace(self, record):
        if Session().config.console_trace:
            print(record)
        


def test_table():
    ht = HTML("""<tr><td>Cell 1</td><td>Cell 2</td></tr>
                <tr><td colspan='2'>Cell B</tr>
                """)
                
    display(ht)
    