"""
variants.py - 

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


from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore


class Project(object):
    def __init__(self, operation="", district="", manager="", location="", tax=True, length=400, count=900, view=0):
        # initializes operation specific values as strings
        self.operation = operation
        self.district = district
        self.manager = manager
        self.location = location
        
        # initializes global sales tax as boolean
        self.tax = tax
        
        # initializes global planting specific values as integers
        self.length = length
        self.count = count
        
        # initializes chart specific values as integers
        self.view = view
    
    def update(self, dictionary):
        # this method is less efficient then updating the class dictionary
        # with self.__dict__update(dictionary), but it's more secure
        for key, value in dictionary.items():
            try:
                self.__dict__[key] = value
            except KeyError:
                return False
        
        return True


class Plant(object):
    def __init__(self, species=0, mortality=0.0, cost=0.0, preparation=0.0, planting=0.0, tending=0.0):
        # initializes plant specific values as integer
        self.species = species
        
        # initializes plant specific values as float
        self.mortality = mortality
        
        # initializes costs specific values as float
        self.cost = cost
        self.preparation = preparation
        self.planting = planting
        self.tending = tending
    
    def update(self, dictionary):
        # this method is less efficient then updating the class dictionary
        # with self.__dict__update(dictionary), but it's more secure
        for key, value in dictionary.items():
            try:
                self.__dict__[key] = value
            except KeyError:
                return False
        
        return True
    
    def sumCosts(self):
        return self.cost + self.preparation + self.planting + self.tending


class Fence(object):
    
    # class constants
    TYPE = 0
    TYPE_STRING = "fence"
    TYPE_SHORT = QtCore.QT_TRANSLATE_NOOP("VariantItem", "F")
    TYPE_DESCRIPTION = QtCore.QT_TRANSLATE_NOOP("VariantItem", "Fence")
    
    def __init__(self, model=0, installation=0.0):
        # initializes fence specific values as integers and floats
        self.model = model
        
        # initializes costs specific values as floats
        self.installation = installation
    
    def update(self, dictionary):
        # this method is less efficient then updating the class dictionary
        # with self.__dict__update(dictionary), but it's more secure
        for key, value in dictionary.items():
            try:
                self.__dict__[key] = value
            except KeyError:
                return False
        
        return True
    
    def sumCosts(self):
        return 0


class Tube(object):
    
    # class constants
    TYPE = 1
    TYPE_STRING = "tube"
    TYPE_SHORT = QtCore.QT_TRANSLATE_NOOP("VariantItem", "TS")
    TYPE_DESCRIPTION = QtCore.QT_TRANSLATE_NOOP("VariantItem", "Tree shelter")
    
    def __init__(self, model=0, count=0, cost=0.0, accessories=0.0, installation=0.0, maintenance=0.0, removal=0.0):
        # initializes fence specific values as integers and floats
        self.model = model
        
        # initializes costs specific values as floats
        self.cost = cost
        self.accessories = accessories
        self.installation = installation
        self.maintenance = maintenance
        self.removal = removal
    
    def update(self, dictionary):
        # this method is less efficient then updating the class dictionary
        # with self.__dict__update(dictionary), but it's more secure
        for key, value in dictionary.items():
            try:
                self.__dict__[key] = value
            except KeyError:
                return False
        
        return True
    
    def sumCosts(self):
        return self.cost + self.accessories + self.installation + self.maintenance + self.removal


class VariantItem(object):
    def __init__(self, name="unknown", protection=-1, parent=None):
        # item specific values
        self.name = name
        self.color = "#ffffff"
        self.status = True
        self.identification = 0
        
        # tree specific values
        self.parent = parent
        self.children = []
        
        # data items
        self.plant = Plant()
        self.protection = None
        self.result = None
        
        # initialize the protection
        if protection == Fence.TYPE:
            self.protection = Fence()
        elif protection == Tube.TYPE:
            self.protection = Tube()
    
    @property
    def type(self):
        if not self.protection:
            return -1
            
        return self.protection.TYPE
    
    def insertChildren(self, position, children):
        for row in range(len(children)):
            children[row].parent = self
            self.children.insert(position, children[row])
    
    #def data(self):
    #    # return self.name, self.color, self.status, self.plant
    #    # and self.protection as a packed tuple
    #    return self.name, self.color, self.status, self.plant, self.protection
    
    def setData(self, values):
        # use values as a packed tuple and unpack values
        # as name, color, status, plant, protection
        self.name, self.color, self.status, self.plant, self.protection = values
    
    def removeChildren(self, position, count):
        for row in range(count):
            child = self.children.pop(position)
    
    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)
    
    def hasChildren(self):
        if self.children:
            return True
        
        return False
    
    def childNumber(self):
        if self.parent:
            return self.parent.children.index(self)
        
        return 0
    
    def sumCosts(self):
        return self.plant.sumCosts() + self.protection.sumCosts()
    
    def prepareSerialization(self):
        item = {"type" : self.type,
                "name" : self.name,
                "color" : self.color,
                "status" : self.status}
        
        # return packed tuble (item, plant, protection)
        return item, self.plant.__dict__, self.protection.__dict__
    
    def deserialize(self, data):
        # unpack the tuple (item, plant, protection)
        item, plant, protection = data
        
        # first deserialize item's data
        self.name = item["name"]
        self.color = item["color"]
        self.status = item["status"]
        
        # update plant and protection
        self.plant.update(plant)
        self.protection.update(protection)
