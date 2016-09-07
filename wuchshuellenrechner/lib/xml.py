"""
xml.py - 

Copyright (C) 2016 Tobias Helfenstein <tobias.helfenstein@mailbox.org>
Copyright (C) 2016 Anton Hammer <hammer.anton@gmail.com>
Copyright (C) 2016 Sebastian Hein <hein@hs-rottenburg.de>
Copyright (C) 2016 Hochschule für Forstwirtschaft Rottenburg <hfr@hs-rottenburg.de>

This file is part of Wuchshüllenrechner.

Wuchshüllenrechner is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Wuchshüllenrechner is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import xml.etree.ElementTree as ElementTree
import logging
import os
import lib.files as FileHandling
from lib.variants import Fence, Tube, VariantItem, Project


class XMLFileWriter():
    """
    Creates a simple about dialog.
    
    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.
    
    """
    
    def __init__(self):
        """The constructor initializes the class XMLFileWriter."""
        pass
    
    def writeXMLFile(self, project, items, xmlfile):
        # check, if the filename is valid
        if not FileHandling.filename_is_valid(xmlfile, "xml"):
            raise ValueError("file name not valid")
        newfile = xmlfile.strip()

        # temporarily add _tmp to the filename, if the file already exists
        exists = os.path.isfile(newfile)
        if exists:
            newfile = newfile.replace(".xml", "_tmp.xml", 1)

        # write all XML data to the file
        try:
            xml = self.createXMLData(project, items)
            xml.write(newfile, xml_declaration=True, encoding="utf-8")
            if exists:
                os.remove(xmlfile.strip())
                os.rename(newfile, xmlfile.strip())
        except OSError:
            return False
        
        return True
    
    def createXMLData(self, project, items):
        # create root element with its project information
        root = ElementTree.Element("project")
        header = ElementTree.SubElement(root, "header")
        for p in project:
            data = ElementTree.SubElement(header, p)
            data.text = str(project[p]).strip()
        
        # create item list with its entries
        dataset = ElementTree.SubElement(root, "data")
        self.writeItemTree(items, dataset)
        
        return ElementTree.ElementTree(root)
    
    def writeItemTree(self, tree, element):
        for child in tree.children:
            item, plant, protection = child.prepareSerialization()
            
            # first serialize item's general data without an own element
            variantEntry = self.writeTags(item, "variant")
            element.append(variantEntry)
            
            # serialize plant data with its own element
            plantElement = self.writeTags(plant, "plant")
            variantEntry.append(plantElement)
                
            # at last serialize protection data with its own element
            protectionElement = self.writeTags(protection, "protection")
            variantEntry.append(protectionElement)
            
            if child.hasChildren():
                childrenElement = ElementTree.SubElement(variantEntry, "children")
                self.writeItemTree(child, childrenElement)
    
    def writeTags(self, dictionary, name):
        # avoid side effects
        element = ElementTree.Element(name.strip())
        for key, value in dictionary.items():
            data = ElementTree.SubElement(element, key)
            data.text = str(value).strip()
        
        return element


class XMLFileReader():
    """Creates a simple about dialog.
    
    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.
    
    """
    
    def __init__(self):
        """The constructor initializes the class XMLFileReader."""
        self.root = None
    
    def readXMLFile(self, xmlfile):
        # check, if the filename is valid
        if not FileHandling.filename_is_valid(xmlfile, "xml"):
            raise ValueError("file name not valid")
        
        try:
            xml = ElementTree.parse(xmlfile)
            self.root = xml.getroot()
        except ElementTree.ParseError:
            return False
            
        return True
    
    def readItemTree(self, element):
        items = []
        for variantEntry in element:
            kind = int(variantEntry.findtext("type", "-1"))
            child = VariantItem(protection=kind)
            item, plant, protection = child.prepareSerialization()
                
            # first read item's general data
            item = self.readTags(item, variantEntry)
            
            # read plant data
            plantElement = variantEntry.find("plant")
            plant = self.readTags(plant, plantElement)
            
            # at last read protection data
            protectionElement = variantEntry.find("protection")
            protection = self.readTags(protection, protectionElement)
            
            # add item to list
            child.deserialize((item, plant, protection))
            items.append(child)
            
            childrenElement = variantEntry.find("children")
            if childrenElement:
                items.extend(self.readItemTree(childrenElement))
                
        return items
    
    def readTags(self, dictionary, element):
        # avoid side effects
        tags = {}
        for key in dictionary:
            kind = type(dictionary[key])
            data = element.findtext(key)
            if data:
                tags[key] = kind(data)
        
        return tags
    
    def getProject(self):
        if not self.root:
            return None
        
        project = Project()
        header = self.root.find("header")
        if None is not header:
            return self.readTags(project.__dict__, header)
        else:
            return None
    
    def getItems(self):
        if not self.root:
            return None
        
        dataset = self.root.find("data")
        try:
            items = self.readItemTree(dataset)
        except TypeError:
            return None
        
        return items
