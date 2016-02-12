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

    Add option to control level of output (i.e., verbose, quiet, etc.).
    
    Pull title-ize feature (replace().title() out to static helper
    function.
    
    Consider using colorama module for colored text.

"""
from IPython.display import display_html, HTML, display

from despy.session import Session

def display_header(header):
    print()
    print('=====', header.ljust(45, '='))
    
def display_message(message):
    print(message)
    
def display_dict(data):
    for _, value in data.items():
        print("{0}: {1}".format(value[0], value[1]))

class Console():
    def __init__(self):
        self._session = Session()
    
    def display(self, label, data):
        if isinstance(data, list):
            self.display_list(label, data)
        elif isinstance(data, dict):
            self.display_dict(label, data)
        else:
            self.display_value(label, data)


    def display_list(self, label, list_data):
        output = "{}: ".format(label)
        for value in list_data[0:-1]:
            output += "{}, ".format(value)
        output += list_data[-1]
        print(output)
        
    def display_value(self, label, data):
        print("{0}: {1}".format(label, data))

    def display_header(self, header):
        print()
        print("====={}==========".format(header))
        
    def display_trace(self, record):
        if Session().config.console_trace:
            print(record)
        

def test_table():
    ht = HTML("""<tr><td>Cell 1</td><td>Cell 2</td></tr>
                <tr><td colspan='2'>Cell B</tr>
                """)
                
    display(ht)
    