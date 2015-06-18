#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin

"""
*******************
despy.output.report
*******************

:class:`HtmlReport`
    Renders an HTML report containing simulation results.

:class:`Datatype`
"""

from enum import Enum
import xml.etree.ElementTree as ET

class HtmlReport():
    """Renders an HTML report containing simulation results.
    
    **Attributes**
        * :attr:`HtmlReport.root`: The root <html> element of the
          HtmlReport. Read-only.
        * :attr:`HtmlReport.head`: The <head> element of the HtmlReport.
          Read-only.
        * :attr:`HtmlReport.body`: The <body> element of the HtmlReport.
          Read-only.
        * :attr:`HtmlReport.divisions`: Python list containing
          simulation output. Read-only.
          
    **Methods**
        * :meth:`HtmlReport.append_output`: Appends a section of output
          to the HtmlReport.divisions list.
        * :meth:`HtmlReport.write_report`: Write HTML report file based
          on data in HtmlReport.divisions.

    **Python Library Dependencies**
        * :mod:`xml.etree.ElementTree`

    """
    
    def __init__(self):
        """Constructs an HtmlReport object.
        """
        self._root = ET.Element('html')
        self._head = ET.SubElement(self.root, 'head')
        self._body = ET.SubElement(self.root, 'body')
        self._divisions = []
        
    @property
    def root(self):
        """The root <html> element of the HtmlReport. Read-only.
        
        *Type:* :class:`xml.etree.ElementTree.Element`
        """
        return self._root
    
    @property
    def head(self):
        """The <head> element of the HtmlReport. Read-only.
        
        *Type:* :class:`xml.etree.ElementTree.Element`
        
        """
        return self._head
    
    @property
    def body(self):
        """The <body> element of the HtmlReport. Read-only.
        
        *Type:* :class:`xml.etree.ElementTree.Element`
        """
        return self._body
    
    @property
    def divisions(self):
        """Python list containing simulation output. Read-only.
        
        Each section of simulation output will be rendered as an HTML
        <div> element. The list can be appended to or have items
        deleted from it. Because it is read-only, it cannot be replaced
        with another list.
        
        *Type:* Python List of Datatype formatted tuples.
        """
        return self._divisions
    
    def append_output(self, output):
        """Appends a section of output to the HtmlReport.divisions list.
        
        *Arguments*
            ``output`` (List of report.Datatype formatted tuples.)
                A section of output that will be rendered as it's own
                division in the HTML report.
        """
        self.divisions.append(output)

    def write_report(self, folder):
        """Write HTML report file based on data in HtmlReport.divisions.
        
        *Arguments*
            ``folder`` (String)
                Full path to folder where HTML report will be saved.
        """
        for div in self.divisions:
            div_elmt = ET.SubElement(self.body, 'div')
            for section in div:
                if section[0] == Datatype.title:
                    h2_elmt = ET.SubElement(div_elmt, 'h2')
                    h2_elmt.text = section[1]
                elif section[0] == Datatype.paragraph:
                    p_elmt = ET.SubElement(div_elmt, 'p')
                    p_elmt.text = section[1]
                elif section[0] == Datatype.param_list:
                    dl_elmt = ET.SubElement(div_elmt, 'dl')
                    for field in section[1]:
                        dt_elmt = ET.SubElement(dl_elmt, 'dt',
                                attrib={'style': 'font-weight: bold;'})
                        dt_elmt.text = field[0].__str__()
                        dl_elmt = ET.SubElement(dl_elmt, 'dd')
                        dl_elmt.text = field[1].__str__()
                elif section[0] == Datatype.image:
                    ET.SubElement(div_elmt, 'img', {'src': section[1]}) 
                    
        ET.ElementTree(self.root).write(folder + '/report.html',
                                        method = 'html')

class Datatype(Enum):
    """Enumeration that defines output data formats.
    
    Despy Model and Simulation objects, and every Despy Component can
    return a Python list with data that will be displayed in the output
    report. Each item in the list is a tuple, and the first item of the
    tuple will be a member of the Datatype enumeration, which
    identifies the format of the data contained in the remainder of the
    tuple.
    
    **Datatype.title** tuples contain two elements. The first element is
    the Datatype.title enumeration and the second is a string that will
    be rendered as a section title.
    
    **Datatype.paragraph** tuples contain two elements. The first
    element is the Datatype.paragraph enumeration and the second is a
    string that is rendered as standard text.
    
    **Datatype.param_list** tuples contain two elements. The first is
    the Datatype.param_list enumeration and the second is element is a
    list. The list contains two element tuples where the first element
    is the name of the parameter, and the second element is the actual
    parameter data.
    
    **Datatype.image** tuples contain two elements. The first is the
    Datatype.image enumeration and the second is a string containing the
    relative location and file name of the image.
    
    For example, a Simulation object returns the following output::
    
        output = [(Datatype.title, "Queue Results: {0}".format(self.name)),
                 (Datatype.paragraph, self.description.__str__()),
                 (Datatype.param_list,
                    [('Maximum Time in Queue', np.amax(qtimes)),
                     ('Minimum Time in Queue', np.amin(qtimes)),
                     ('Mean Time in Queue', np.mean(qtimes))]),
                 (Datatype.image, qtime_filename)]
                     
    Despy uses a simple Python list for output data because it's easy to
    read and write in the code files and is independent of the ultimate
    output format. Also, unlike a dictionary object, Python lists allow
    the designer to specify the order.
    """
    title = 1
    paragraph = 2
    param_list = 3
    image = 4

        
