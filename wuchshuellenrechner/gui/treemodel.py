"""
treemodel.py - 

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


import logging
from numbers import Number
from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt5.QtGui import QKeySequence, QStandardItemModel, QIcon, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QVariant, QSize, QLocale
from PyQt5.QtCore import pyqtSignal
from lib.variants import Plant, Fence, Tube, VariantItem, Project
from lib.xml import XMLFileWriter, XMLFileReader
from lib import cost as library
from PyQt5 import QtCore


class TreeModel(QAbstractItemModel):
    # Funktion hasChildren?
    
    # signals
    statusChanged = pyqtSignal(QModelIndex)
    speciesChanged = pyqtSignal(QModelIndex, int, int)
    calculated = pyqtSignal()
    
    itemsInserted = pyqtSignal(bool)
    itemsAboutToBeCalculated = pyqtSignal(bool)
    allItemsRemoved = pyqtSignal(bool)

    # class constants
    ItemRole = Qt.UserRole + 1
    StatusRole = Qt.UserRole + 2
    ColorRole = Qt.UserRole + 3
    TypeRole = Qt.UserRole + 4
    NameRole = Qt.UserRole + 5
    ResultRole = Qt.UserRole + 6
    PlantRole = Qt.UserRole + 7
    ProtectionRole = Qt.UserRole + 8
    SpeciesRole = Qt.UserRole + 9
    TypeRole = Qt.UserRole + 10
    IdentificationRole = Qt.UserRole + 11
    LengthRole = Qt.UserRole + 12
    CountRole = Qt.UserRole + 13
    _roles = {ItemRole : "item",
              StatusRole : "status",
              ColorRole : "color",
              TypeRole : "type",
              NameRole : "name",
              ResultRole : "result",
              PlantRole : "plant",
              ProtectionRole : "protection",
              IdentificationRole : "identification",
              LengthRole : "length",
              CountRole : "count"}

    TYPE, IDENTIFICATION, SPECIES, NAME = range(4)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = VariantItem("root item")
        
        # species registry
        self.species = {}
        self.variants = 0

        # initialize class attributes
        self._TABLE_HEADER_LABELS = (QtCore.QT_TRANSLATE_NOOP("TreeModel", "Protection type"),
                                     QtCore.QT_TRANSLATE_NOOP("TreeModel", "Name"),
                                     QtCore.QT_TRANSLATE_NOOP("TreeModel", "Tree species"),
                                     QtCore.QT_TRANSLATE_NOOP("TreeModel", "Description of protection"))
        
        # project settings
        self.project = Project()
        
        self.rowsInserted.connect(self.updateSpecies)
        self.speciesChanged.connect(self.moveItem)
        self.statusChanged.connect(self.updateStatus)
        
        self.new = True
        self.changed = False
        self.filename = ""
        self.file = False
        self.read = False
        
        self.last = QModelIndex()
        self.current = -1
        
        self.count = 0          # temoporary plant count for calculation help
        self.length = 0         # temoporary fence length for calculation help
    
    def columnCount(self, parent):
        return len(self._TABLE_HEADER_LABELS)
        
    def roleNames(self):
        return self._roles
    
    def projectData(self, key):
        return getattr(self.project, key)
        
    def setProjectData(self, key, value):
        setattr(self.project, key, value)
        self.changed = True
    
    def itemData(self, index):
        if not index.isValid():
            return None
        
        item = self.getItem(index)
        
        # create the QMap as python dict
        data = {
            self.NameRole : item.name,
            self.ColorRole : item.color,
            self.StatusRole : item.status,
            self.PlantRole : item.plant,
            self.ProtectionRole : item.protection
        }
        
        return data
    
    def setItemData(self, index, roles):
        if not index.isValid():
            return False
        
        item = self.getItem(index)
        oldSpecies = item.plant.species
        newSpecies = roles[self.PlantRole].species
        
        # if the species has changed, the item have to move
        # a fence item doesn't have already known species
        if not newSpecies == oldSpecies:
            if item.type == Fence.TYPE and newSpecies in self.species:
                return False
            
            self.speciesChanged.emit(index, oldSpecies, newSpecies)
        
        # update the item
        for role in roles:
            if not role in self._roles:
                return False
            
            attribute = self._roles[role]
            setattr(item, attribute, roles[role])
        
        # update model's change status
        self.dataChanged.emit(index, index)
        self.changed = True
        
        return True
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        item = index.internalPointer()
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == TreeModel.TYPE:
                return QApplication.translate("VariantItem", item.protection.TYPE_DESCRIPTION)
            elif column == TreeModel.NAME:
                return item.name
            elif column == TreeModel.SPECIES:
                return library.TREESPECIES_ABBREVIATION[item.plant.species]
            elif column == TreeModel.IDENTIFICATION:
                return "{protection}{identification}".format(
                        protection=QApplication.translate("VariantItem", item.protection.TYPE_SHORT),
                        identification=item.identification + 1)
        elif role == Qt.CheckStateRole:
            if column == TreeModel.TYPE:
                if item.status:
                    if item.type == Fence.TYPE:
                        checked = True
                        for child in item.children:
                            if not child.status:
                                checked = False
                        if checked:
                            return Qt.Checked
                        else:
                            return Qt.PartiallyChecked
                    else:
                        return Qt.Checked
                else:
                    return Qt.Unchecked
        elif role == self.IdentificationRole:
            return "{protection}{identification}".format(
                    protection=QApplication.translate("VariantItem", item.protection.TYPE_SHORT),
                    identification=item.identification + 1)
        elif role == self.LengthRole:
            return self.project.length
        elif role == self.CountRole:
            return self.project.count
        elif role == self.TypeRole:
            return item.type
        elif role == self.NameRole:
            return item.name
        elif role == self.SpeciesRole:
            return item.plant.species
        elif role == self.ColorRole:
            return QColor(item.color)
        elif role == self.StatusRole:
            return item.status
        elif role == self.ResultRole:
            return item.result
        else:
            return None
    
    def setData(self, index, value, role=Qt.EditRole):
        item = index.internalPointer()

        if role == Qt.CheckStateRole:
            if value in (Qt.Checked, Qt.PartiallyChecked):
                item.status = True
            else:
                item.status = False
            
            self.dataChanged.emit(index, index)
            #self.statusChanged.emit(index)
                
            if item.type == Fence.TYPE:
                for child in item.children:
                    child.status = item.status
                    childIndex = self.createIndex(child.childNumber(), self.TYPE, child)
                    self.dataChanged.emit(childIndex, childIndex)
            if item.type > Fence.TYPE:
                parent = item.parent
                status = False
                for child in parent.children:
                    if child.status:
                        status = True
            
                parent.status = status
                
                self.dataChanged.emit(index.parent(), index.parent())
            
            return True
            
            return True
        elif role == self.ResultRole:
            item.result = value
            self.dataChanged.emit(index, index)

            return True
        elif role == self.ColorRole:
            item.color = value
            self.dataChanged.emit(index, index)
            
            return True
        else:
            return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        column = index.column()
        if column == TreeModel.TYPE:
            if index.data() == Fence.TYPE_DESCRIPTION:
                return flags | Qt.ItemIsUserCheckable | 64
            else:
                return flags | Qt.ItemIsUserCheckable
        else:
            return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QApplication.translate("TreeModel", self._TABLE_HEADER_LABELS[section])
        
        return None
    
    def index(self, row, column, parent=QModelIndex()):     # kann Fehler verursachen!
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
            
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()
            
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        child = self.getItem(index)
        parent = child.parent
        
        if parent == self.root:
            return QModelIndex()
        
        return self.createIndex(parent.childNumber(), 0, parent)
    
    def rowCount(self, parent=QModelIndex()):
        #if parent.column() > 0:
        #    return 0
        
        #if not parent.isValid():
        #    parent_item = self.root
        #else:
        #    parent_item = parent.internalPointer()
        
        #return parent_item.childCount()
        
        item = self.getItem(parent)
        
        return item.childCount()
    
    def evaluate(self):
        evaluation = False

        # if there is a fence item with at least 
        # one children, enable the calculation button
        items = self.match(self.index(0, 0),
                self.TypeRole, Tube.TYPE, -1, Qt.MatchRecursive)

        for item in items:
            if item.parent().isValid():
                # the calculation button should be enabled
                evaluation = True
                break
        
        self.itemsAboutToBeCalculated.emit(evaluation)
        
        # automatic protection type
        # self.last contains an index value
        if not self.last.parent().isValid() and self.current == -1:
            if self.last.data(self.TypeRole) == Fence.TYPE:
                self.current = Tube.TYPE
            elif self.last.data(self.TypeRole) == Tube.TYPE:
                self.current = Fence.TYPE
            else:
                self.current = -1
        else:
            self.current = -1
        
        return evaluation
    
    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        
        return self.root
    
    def insertItem(self, item):
        return self.insertItems([item])
    
    def insertItems(self, items):
        if not items:
            return False

        # extract items with type = 0 as top level items
        toplevel = []
        species = []
        for item in items[:]:
            # update the identification
            item.identification = self.variants
            self.variants = self.variants + 1
        
            if item.type == 0:
                if not item.plant.species in self.species:
                    toplevel.append(item)
                    species.append(item.plant.species)
                    items.remove(item)
                else:
                    return False
            elif item.type > 0:
                if item.plant.species in self.species:
                    parent = self.root.child(self.species[item.plant.species])
                    index = self.createIndex(parent.childCount(), 0, parent)
                    self.insertRow(parent.childCount(), item, index)
                    items.remove(item)
            else:
                return False
        
        # extract current top level items with type > 0 from root
        if toplevel:
            current = []
            for child in self.root.children[:]:
                if child.plant.species in species:
                    current.append(child)
                    self.removeRow(child.childNumber())

            items.extend(current)
            for item in toplevel:
                for child in items[:]:
                    if child.plant.species == item.plant.species:
                        item.insertChildren(item.childCount(), [child])
                        items.remove(child)
            toplevel.extend(items)
        else:
            toplevel = items
        
        # insert the new rows and emit the signal to enable the view
        # also do an evaluation
        if toplevel:
            self.insertRows(self.root.childCount(), toplevel)
        
        # always evaluate
        self.itemsInserted.emit(True)
        self.evaluate()

        return True

    def insertRow(self, row, item, parent=QModelIndex()):
        return self.insertRows(row, [item], parent)
    
    def insertRows(self, row, items, parent=QModelIndex()):
        item = self.getItem(parent)
        
        self.beginInsertRows(parent, row, row + len(items) - 1)
        item.insertChildren(row, items)
        self.endInsertRows()
        
        # get the index of the last item
        if not self.read:
            self.last = self.index(row + len(items) -1, 0, parent)
        
        # update model's change status
        self.new = False
        self.changed = True
        
        return True
    
    def updateStatus(self, index):
        # möglicherweise sollte diese Funktion in die Delegate
        #if not index.parent().isValid():    # item.type = Fence.TYPE
        item = self.getItem(index)
        
        if item.type == Fence.TYPE:
            for child in item.children:
                child.status = item.status
                childIndex = self.createIndex(child.childNumber(), self.TYPE, child)
                self.dataChanged.emit(childIndex, childIndex)
        if item.type > Fence.TYPE:
            parent = item.parent
            status = False
            for child in parent.children:
                if child.status:
                    status = True
            
            parent.status = status
            self.dataChanged.emit(index.parent(), index.parent())
    
    def updateSpecies(self, parent, first, last):
        if not parent.isValid():
            item = self.getItem(parent)
            for row in range(first, last + 1):
                child = item.child(row)
                if child.type == Fence.TYPE:
                    self.species[child.plant.species] = row
    
    def removeItem(self, position, parent=QModelIndex()):
        return self.removeItems(position, 1, parent)
            
    def removeItems(self, position, rows, parent=QModelIndex()):
        item = self.getItem(parent)
        if position < 0 or position + rows - 1 > item.childCount():
            return False
        
        # first it's necessary to remove the species entry
        for row in range(position, position + rows):
            child = item.child(row)
            if child.type == Fence.TYPE:
                del self.species[child.plant.species]
        
        # now the child items can be removed
        # and do an evaluation
        self.removeRows(position, rows, parent)
        self.evaluate()
        
        # if the model is empty, emit the signal
        # to disable the view
        if not self.rowCount():
            self.allItemsRemoved.emit(True)
        
        return True
    
    def removeRow(self, row, parent=QModelIndex()):
        return self.removeRows(row, 1, parent)
    
    def removeRows(self, row, count, parent=QModelIndex()):
        item = self.getItem(parent)
        
        self.beginRemoveRows(parent, row, row + count -1)
        item.removeChildren(row, count)
        self.endRemoveRows()
        
        # get the index of the last item
        self.last = QModelIndex()
        
        # update model's change status
        self.changed = True
        
        return True
    
    def moveItem(self, index, oldSpecies, newSpecies):
        # item.type durch index.parent is valid ersetzen?!
        item = self.getItem(index)
        parent = item.parent
        
        if item.type == Fence.TYPE:
            # first update the species registry
            del self.species[oldSpecies]
            self.species[newSpecies] = index.row()
            
            # simply clear item's internal list and
            # move child item's to tree root
            if item.hasChildren():
                count = item.childCount()
                child = parent.childCount()
                self.moveRows(index, 0, count, index.parent(), child)
            
            # if there are any child items with the same species
            # within tree root, add them to the current item
            for child in parent.children[:]:
                if child.type > Fence.TYPE and child.plant.species == newSpecies:
                    count = item.childCount()
                    row = child.childNumber()
                    self.moveRow(index.parent(), row, index, count)
        
        elif item.type > Fence.TYPE:
            if newSpecies in self.species:
                newParent = self.root.child(self.species[newSpecies])
                newIndex = self.createIndex(newParent.childNumber(), 0, newParent)
                child = newParent.childCount()
                self.moveRow(index.parent(), index.row(), newIndex, child)
            elif index.parent().isValid():
                # only if the parent is valid, the item
                # can be moved to the tree root
                child = self.root.childCount()
                self.moveRow(index.parent(), index.row(), QModelIndex(), child)
        
        # after moving items do an evaluation
        #self.evaluate()
    
    def moveRow(self, source, row, destination, child):
        return self.moveRows(source, row, 1, destination, child)
    
    def moveRows(self, source, row, count, destination, child):
        sourceParent = self.getItem(source)
        destinationParent = self.getItem(destination)
        
        self.beginMoveRows(source, row, row + count - 1, destination, child)
        destinationParent.insertChildren(child, sourceParent.children[row:row+count])
        sourceParent.removeChildren(row, count)
        self.endMoveRows()
        
        # update model's change status
        self.changed = True
        
        return True
    
    def saveFile(self, xmlfile=""):
        if xmlfile:
            self.filename = xmlfile
            self.file = True
        elif self.file:
            xmlfile = self.filename
        else:
            return False
    
        writer = XMLFileWriter()
        success = writer.writeXMLFile(self.project.__dict__, self.root, xmlfile)
        
        # update model's change status
        if success:
            self.changed = False
        
        return success
    
    def readFile(self, xmlfile):
        if xmlfile:
            self.filename = xmlfile
            self.file = True
        else:
            return False
        
        # wichtig, um keine Vorauswahl zu haben
        self.read = True
        reader = XMLFileReader()
        success = reader.readXMLFile(xmlfile)
        
        if success:
            if not self.project.update(reader.getProject()):
                success = False
            if not self.insertItems(reader.getItems()):
                success = False
            
            # TODO
            self.dataChanged.emit(QModelIndex(), QModelIndex())

            # update model's change status and clear model if necessary
            self.new = False
            self.changed = success
            self.read = False
            
            if not success:
                self.clear()
        
        return success
    
    def clear(self):
        # first call beginResetModel()
        self.beginResetModel()
        
        # now clear all model data
        self.project = Project()
        self.root = VariantItem("root item")
        self.species = {}
        self.variants = 0
        self.new = True
        self.changed = False
        self.filename = ""
        self.file = False
        self.read = False
        
        self.last = QModelIndex()
        self.current = -1
        
        self.count = 0
        self.length = 0
        
        # it's necessary to call endResetModel()
        self.endResetModel()
    
    def calculate(self):
        shelters = []
        for child in self.root.children:
            if child.type == Fence.TYPE and child.hasChildren():
                # fence result is set to fence length
                #child.result = child.protection.length
                
                for shelter in child.children:
                    # the following operations are based on the example calculation
                    # of Dr. Anton Hammer <hammer.anton@gmail.com>
                    slope = shelter.sumCosts() * (1 - shelter.plant.mortality) - child.sumCosts()
                    result = child.protection.installation / slope
                    
                    # update result in model's item
                    index = self.createIndex(shelter.childNumber(), 0, shelter)
                    self.setData(index, result, TreeModel.ResultRole)
            else:
                shelters.append(child.name)
        
        # an empty list means that the calculation was successful
        if not shelters:
            self.calculated.emit()
        
        return shelters


class TreeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if index.column() == TreeModel.TYPE:
            width = 50
        
            return QSize(fm.width(index.data()) + width, 24)
        else:
            return super().sizeHint(option, index)
