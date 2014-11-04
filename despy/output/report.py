#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from enum import Enum

class Datatype(Enum):
    title = 1
    paragraph = 2
    param_list = 3
    image = 4

class HtmlReport():
    
    def __init__(self):
        self.root = ET.Element('html')
        self.head = ET.SubElement(self.root, 'head')
        self.body = ET.SubElement(self.root, 'body')
        self.divisions = []
    
    def append_output(self, output):
        self.divisions.append(output)
        
    def render_report(self):
        for div in self.divisions:
            div_elmt = ET.SubElement(self.body, 'div')
            for section in div:
                self.render_section(div_elmt, section)
    
    def render_section(self, div_elmt, section):
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
                
    def write_report(self, folder):
        self.render_report()
        ET.ElementTree(self.root).write(folder + '/report.html',
                                        method = 'html')
        
