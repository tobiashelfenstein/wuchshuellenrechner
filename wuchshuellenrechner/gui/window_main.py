"""
window_main.py -

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


from PyQt5.QtWidgets import QMainWindow, QGroupBox, QVBoxLayout, QWidget,\
    QGridLayout, QLabel, QLineEdit, QTableView, QDialogButtonBox,\
    QPushButton, QSpacerItem, QAbstractItemView, QSplitter, QToolBar, QFrame,\
    QDialog, QHeaderView, QFileDialog, QHBoxLayout, QSpinBox, QCheckBox, QMenu
from PyQt5.QtWidgets import QSizePolicy, QToolTip
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QWizard
from PyQt5.QtGui import QKeySequence, QStandardItemModel, QIcon, QColor, QPainter, QPen, QImage, QFontMetrics, QPixmap
from PyQt5.QtCore import Qt, QLocale

from gui.dialog_data import VariantDataDialog, VariantHintDialog
from gui.dialog_about import AboutDialog, ScientificBasisDialog
from gui.widget_plot import VariantPlotView
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, QItemSelectionModel
from lib.variants import Fence, Tube, VariantItem
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QHeaderView
from gui.treemodel import TreeModel
from gui.treemodel import TreeDelegate
from gui.widgets import ToolTipLabel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QDoubleSpinBox
import os.path
import sys
import subprocess
from PyQt5.QtCore import QLocale, QEvent
from PyQt5.QtCore import QTranslator
from PyQt5.QtCore import QModelIndex


__version__ = "1.0.0"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # initialize class attributes
        self._INPUTS_FIXED_WIDTH = 180
        self._BUTTON_MIN_WIDTH = 80
        self._OXYGEN_PATH_32 = os.path.join("resources", "icons", "oxygen", "32")

        # locale and language settings
        self.language = self.locale().name()[:2]
        self.qtTl = QTranslator()
        self.appTl = QTranslator()
        self.switchTranslator(self.qtTl, "qtbase", self.language)
        self.switchTranslator(self.appTl, "wuchshuellenrechner", self.language)

        # TODO(th)
        self.model = TreeModel()

        # setup gui
        self.setMinimumSize(1200, 760)

        self.createActions()
        self.createMainMenu()

        # plot widget
        self.plotWidget = VariantPlotView()
        self.plotWidget.setModel(self.model)

        # create vertical splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.setContentsMargins(11, 11, 11, 11)
        splitter.addWidget(self.createEditBox())
        splitter.addWidget(self.plotWidget)

        self.setCentralWidget(splitter)

        self.dataWidget.setModel(self.model)

        selectionModel = QItemSelectionModel(self.model)
        self.dataWidget.setSelectionModel(selectionModel)
        self.plotWidget.setSelectionModel(selectionModel)

        self.retranslateUi()


        self.model.dataChanged.connect(self.updateInputs)
        self.model.itemsInserted.connect(self.taxInput.setDisabled)
        self.model.allItemsRemoved.connect(self.taxInput.setEnabled)
        self.operationInput.textChanged.connect(self.updateOperation)
        self.districtInput.textChanged.connect(self.updateDistrict)
        self.managerInput.textChanged.connect(self.updateManager)
        self.locationInput.textChanged.connect(self.updateLocation)
        self.taxInput.stateChanged.connect(self.updateTax)

    def updateOperation(self, value):
        self.model.setProjectData("operation", value)

    def updateDistrict(self, value):
        self.model.setProjectData("district", value)

    def updateManager(self, value):
        self.model.setProjectData("manager", value)

    def updateLocation(self, value):
        self.model.setProjectData("location", value)

    def updateTax(self):
        self.model.setProjectData("tax", self.taxInput.isChecked())
        self.dataWidget.tax = self.taxInput.isChecked()

    def updateInputs(self):
        self.operationInput.setText(self.model.projectData("operation"))
        self.districtInput.setText(self.model.projectData("district"))
        self.managerInput.setText(self.model.projectData("manager"))
        self.locationInput.setText(self.model.projectData("location"))

        self.taxInput.setChecked(self.model.projectData("tax"))

    def loadLanguage(self, language):
        if not self.language == language:
            self.language = language

            locale = QLocale(language)
            QLocale.setDefault(locale)

            self.switchTranslator(self.qtTl, "qtbase", language)
            self.switchTranslator(self.appTl, "wuchshuellenrechner", language)

            # update gui
            self.retranslateUi()
            self.dataWidget.retranslateUi()

    def switchTranslator(self, translator, filename, language):
        app = QApplication.instance()

        # remove the old translator and
        # try to load a new language file
        app.removeTranslator(translator)
        if translator.load(QLocale(), filename, "_", "language"):
            app.installTranslator(translator)

    def setTaxEnabled(self, enable):
        # enable buttons and the view element
        self.removeButton.setEnabled(enable)
        self.modifyButton.setEnabled(enable)
        self.view.setEnabled(enable)

    def setDisabled(self, disable):
        # internaly call the setEnabled function
        # therefore negate the boolean value
        self.setEnabled(not disable)

    def aboutAction(self):
        aboutDialog = AboutDialog()
        aboutDialog.exec()

    def clear(self):
        # first clear the model
        self.model.clear()

        # update fields with model's default values
        self.operationInput.setText(self.model.projectData("operation"))
        self.districtInput.setText(self.model.projectData("district"))
        self.managerInput.setText(self.model.projectData("manager"))
        self.locationInput.setText(self.model.projectData("location"))

        self.taxInput.setEnabled(True)
        self.taxInput.setChecked(self.model.projectData("tax"))

        # reset the tree view
        self.dataWidget.clear()

        # reset the chart and result view
        # actually this is necassary
        self.plotWidget.clear()

    def closeAction(self):
        if self.model.changed:
            question = QMessageBox()
            question.setIcon(QMessageBox.Question)
            question.setWindowTitle("Berechnung speichern? - Wuchshüllenrechner")
            question.setText("Möchten Sie die Änderungen an dieser Berechnung speichern?")
            question.setInformativeText("Die Änderungen gehen verloren, wenn Sie nicht speichern.")
            question.setStandardButtons(QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
            question.setDefaultButton(QMessageBox.Save)
            reply = question.exec()

            if not reply == QMessageBox.Cancel:
                if reply == QMessageBox.Save:
                    if self.saveAction():
                        self.close()
                else:
                    self.close()
        else:
            self.close()

    def newAction(self):
        if self.model.changed:
            question = QMessageBox()
            question.setIcon(QMessageBox.Question)
            question.setWindowTitle("Berechnung speichern? - Wuchshüllenrechner")
            question.setText("Möchten Sie die Änderungen an dieser Berechnung speichern?")
            question.setInformativeText("Die Änderungen gehen verloren, wenn Sie nicht speichern.")
            question.setStandardButtons(QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
            question.setDefaultButton(QMessageBox.Save)
            reply = question.exec()

            if not reply == QMessageBox.Cancel:
                if reply == QMessageBox.Save:
                    if self.saveAction():
                        # clear all
                        self.clear()
                else:
                    # clear all
                    self.clear()

    def checkSaveState(self):
        if self.model.changed:
            question = QMessageBox(self)
            question.setWindowModality(Qt.WindowModal)  # check for mac only
            question.setIcon(QMessageBox.Warning)
            question.setStandardButtons(QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
            question.setDefaultButton(QMessageBox.Save)
            question.setWindowTitle(QApplication.translate("MainWindow", "Wuchshüllenrechner"))
            question.setText("<b>" + QApplication.translate("MainWindow",
                    "Do you want to save the changes you made<br>"
                    "to the current calculation?") + "</b>")
            question.setInformativeText(QApplication.translate("MainWindow",
                    "Your changes will be lost if you don't save them."))

            reply = question.exec()
            if reply == QMessageBox.Save:
                if self.saveAction():
                    #self.model.clear()
                    self.clear()
                    return True
                else:
                    return False
            elif reply == QMessageBox.Discard:
                #self.model.clear()
                self.clear()
                return True
            else:
                return False

        # always clear
        self.clear()

        return True

    def loadExample(self, example=""):
        # create the path
        exampleFile = os.path.join("examples", example.strip() + ".xml")

         # if all is save, open the example file
        if self.checkSaveState():
            self.model.readFile(exampleFile)

    def mapleAction(self):
        self.loadExample("great_maple")

    def douglasAction(self):
        self.loadExample("douglas_fir")

    def openAction(self):
        # first check save state of the current calculation
        if self.checkSaveState():
            dialog = QFileDialog(self)
            dialog.setWindowModality(Qt.WindowModal)    # check for mac only
            dialog.setWindowTitle(QApplication.translate("MainWindow", "Open Calculation"))
            dialog.setDirectory(os.path.expanduser("~"))
            dialog.setNameFilter(QApplication.translate("MainWindow",
                    "XML files (*.xml);;All Files (*)"))

            dialog.exec()
            filename = dialog.selectedFiles()
            if filename:
                self.model.readFile(filename.pop())

    def saveAction(self):
        if self.model.file:
            return self.model.saveFile()
        else:
            return self.saveAsAction()

    def saveAsAction(self):
        dialog = QFileDialog(self)
        dialog.setWindowModality(Qt.WindowModal)    # check for mac only
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle(QApplication.translate("MainWindow", "Save Calculation"))
        dialog.setDirectory(os.path.expanduser("~"))
        dialog.setNameFilter(QApplication.translate("MainWindow",
                "XML files (*.xml);;All Files (*)"))

        dialog.exec()
        filename = dialog.selectedFiles()
        if filename:
            self.model.saveFile(filename.pop())
            return True
        else:
            return False

    def exportAction(self):
        dialog = QFileDialog(self)
        dialog.setWindowModality(Qt.WindowModal)    # check for mac only
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle(QApplication.translate("MainWindow", "Export Calculation"))
        dialog.setDirectory(os.path.expanduser("~"))
        dialog.setNameFilter(QApplication.translate("MainWindow",
                "PNG files (*.png);;JPG files (*.jpg);;TIFF files (*.tif)"))

        if dialog.exec():
            filename = dialog.selectedFiles()
            self.plotWidget.plotWidget.plotWidget.export(filename.pop())

    def helpAction(self):
        # create the documentation path with
        # the current locale settings
        docFile = os.path.join("doc", "documentation_" + self.language + ".pdf")

        # on every platfrom a different
        # start operation is needed
        if sys.platform == "win32":
            os.startfile(docFile)
        elif sys.platform == "darwin":
            subprocess.call(("open", docFile))
        elif sys.platform.startswith("linux"):
            subprocess.call(("xdg-open", docFile))

    def scientificAction(self):
        scientificDialog = ScientificBasisDialog()
        scientificDialog.exec()

    def germanAction(self):
        # update language menu
        self.languageEnglish.setChecked(False)
        self.languageGerman.setChecked(True)

        # update gui
        self.loadLanguage("de")

    def englishAction(self):
        # update language menu
        self.languageGerman.setChecked(False)
        self.languageEnglish.setChecked(True)

        # update gui
        self.loadLanguage("en")

    def createActions(self):
        # all actions for the calculation menu
        # create the new calculation action
        self.calculationNew = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "document-new.png")),
                shortcut=QKeySequence.New, triggered=self.newAction)

        # create the open calculation action
        self.calculationOpen = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "document-open.png")),
                shortcut=QKeySequence.Open, triggered=self.openAction)

        # create the open calculation example actions
        # for great maple and douglas fir
        self.examplesMaple = QAction(self, triggered=self.mapleAction)
        self.examplesDouglas = QAction(self, triggered=self.douglasAction)

        # create the save calculation action
        self.calculationSave = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "document-save.png")),
                shortcut=QKeySequence.Save, triggered=self.saveAction)

        # create the save as action
        self.calculationSaveAs = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "document-save-as.png")),
                shortcut=QKeySequence.SaveAs, triggered=self.saveAsAction)

        # create the print calculation action
        #self.calculationPrint = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "document-print.png")),
        #        shortcut=QKeySequence.Print, triggered=self.printAction)

        # create the export calculation action
        self.calculationExport = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "document-export.png")),
                shortcut=QKeySequence(Qt.CTRL + Qt.Key_E), triggered=self.exportAction)

        # create the quit calculation action
        self.calculationQuit = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "application-exit.png")),
                shortcut=QKeySequence.Quit, triggered=self.closeAction)

        # all actions for the language menu
        # create the german and the english language actions
        self.languageGerman = QAction(self, checkable=True, triggered=self.germanAction)
        self.languageEnglish = QAction(self, checkable=True, triggered=self.englishAction)

        # update the language menu
        if self.language == "de":
            self.languageGerman.setChecked(True)
        elif self.language == "en":
            self.languageEnglish.setChecked(True)

        # create the help contents action
        self.helpContents = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "help-contents.png")),
                triggered=self.helpAction)

        # create the scientific basis action
        self.scientificBasis = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "applications-science.png")),
                triggered=self.scientificAction)

        # create the help about action
        self.helpAbout = QAction(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "dialog-information.png")),
                triggered=self.aboutAction)

    def createMainMenu(self):
        # create main menu bar
        self.menu = self.menuBar()

        # create file menu
        self.calculationMenu = QMenu(self)
        self.calculationMenu.addAction(self.calculationNew)
        self.calculationMenu.addAction(self.calculationOpen)

        self.examplesMenu = QMenu(self, icon=QIcon(os.path.join(self._OXYGEN_PATH_32, "folder-documents.png")))
        self.examplesMenu.addAction(self.examplesMaple)
        self.examplesMenu.addAction(self.examplesDouglas)
        self.calculationMenu.addMenu(self.examplesMenu)
        self.calculationMenu.addSeparator()

        self.calculationMenu.addAction(self.calculationSave)
        self.calculationMenu.addAction(self.calculationSaveAs)
        self.calculationMenu.addAction(self.calculationExport)
        self.calculationMenu.addSeparator()

        #self.calculationMenu.addAction(self.calculationPrint)
        #self.calculationMenu.addSeparator()

        self.calculationMenu.addAction(self.calculationQuit)

        self.menu.addMenu(self.calculationMenu)

        # create language menu
        self.languageMenu = QMenu(self)
        self.languageMenu.addAction(self.languageGerman)
        self.languageMenu.addAction(self.languageEnglish)
        self.menu.addMenu(self.languageMenu)

        # create help menu
        self.helpMenu = QMenu(self)
        self.helpMenu.addAction(self.helpContents)
        self.helpMenu.addAction(self.scientificBasis)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.helpAbout)
        self.menu.addMenu(self.helpMenu)

    def createEditBox(self):
        # create group box
        self.editBox = QGroupBox()
        self.editBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        gridLayout = QGridLayout(self.editBox)

        # create input fields
        self.operationInput = QLineEdit(self.model.projectData("operation"))
        self.operationInput.setFixedWidth(self._INPUTS_FIXED_WIDTH)
        self.operationInput.setClearButtonEnabled(True)
        self.operationLabel = QLabel()
        self.operationLabel.setBuddy(self.operationInput)
        gridLayout.addWidget(self.operationLabel, 0, 0)
        gridLayout.addWidget(self.operationInput, 0, 1)

        self.districtInput = QLineEdit(self.model.projectData("district"))
        self.districtInput.setFixedWidth(self._INPUTS_FIXED_WIDTH)
        self.districtInput.setClearButtonEnabled(True)
        self.districtLabel = QLabel()
        self.districtLabel.setBuddy(self.districtInput)
        gridLayout.addWidget(self.districtLabel, 0, 2)
        gridLayout.addWidget(self.districtInput, 0, 3)

        self.managerInput = QLineEdit(self.model.projectData("manager"))
        self.managerInput.setFixedWidth(self._INPUTS_FIXED_WIDTH)
        self.managerInput.setClearButtonEnabled(True)
        self.managerLabel = QLabel()
        self.managerLabel.setBuddy(self.managerInput)
        gridLayout.addWidget(self.managerLabel, 1, 0)
        gridLayout.addWidget(self.managerInput, 1, 1)

        self.locationInput = QLineEdit(self.model.projectData("location"))
        self.locationInput.setFixedWidth(self._INPUTS_FIXED_WIDTH)
        self.locationInput.setClearButtonEnabled(True)
        self.locationLabel = QLabel()
        self.locationLabel.setBuddy(self.locationInput)
        gridLayout.addWidget(self.locationLabel, 1, 2)
        gridLayout.addWidget(self.locationInput, 1, 3)

        lineFrame = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.VLine)
        gridLayout.addWidget(lineFrame, 0, 4, 2, 1)

        self.taxInput = QCheckBox()
        self.taxInput.setChecked(self.model.projectData("tax"))
        self.taxLabel = QLabel()
        self.taxLabel.setBuddy(self.taxInput)
        self.taxHint = ToolTipLabel()
        gridLayout.addWidget(self.taxLabel, 0, 5)
        gridLayout.addWidget(self.taxInput, 0, 6)
        gridLayout.addWidget(self.taxHint, 0, 7, Qt.AlignRight)
        gridLayout.setColumnMinimumWidth(7, 40)

        rightSpacer = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        gridLayout.addItem(rightSpacer, 0, 8, 2, 1)

        self.dataWidget = EnhancedTreeWidget()
        gridLayout.addWidget(self.dataWidget, 2, 0, 1, 9)

        return self.editBox

    def retranslateUi(self):
        # main window title
        self.setWindowTitle(QApplication.translate("MainWindow", "Wuchshüllenrechner"))     # Wuchshüllenrechner

        # all menu actions
        # first the calculation menu
        self.calculationMenu.setTitle(QApplication.translate("MainWindow", "&Calculation"))     # Kalkulation
        self.calculationNew.setText(QApplication.translate("MainWindow", "&New"))               # &Neu
        self.calculationOpen.setText(QApplication.translate("MainWindow", "&Open"))             # Ö&ffnen
        self.calculationSave.setText(QApplication.translate("MainWindow", "&Save"))             # &Speichern
        self.calculationSaveAs.setText(QApplication.translate("MainWindow", "&Save as"))        # &Speichern unter
        #self.calculationPrint.setText(QApplication.translate("MainWindow", "&Print"))           # &Drucken
        self.calculationExport.setText(QApplication.translate("MainWindow", "&Export"))         # &Exportieren
        self.calculationQuit.setText(QApplication.translate("MainWindow", "E&xit"))             # &Beenden

        # now the examples menu
        self.examplesMenu.setTitle(QApplication.translate("MainWindow", "E&xamples"))           # &Beispiele
        self.examplesMaple.setText(QApplication.translate("MainWindow",
                "&Calculation example for great &maple"))                                       # Berechnungsbeispiel für Berg-&Ahorn
        self.examplesDouglas.setText(QApplication.translate("MainWindow",
                "&Calculation example for &douglas fir"))                                       # Berechnungsbeispiel für Küsten-Douglasie

        # the language menu
        self.languageMenu.setTitle(QApplication.translate("MainWindow", "&Language"))           # &Sprache
        self.languageGerman.setText(QApplication.translate("MainWindow", "&German"))            # &Deutsch
        self.languageEnglish.setText(QApplication.translate("MainWindow", "&English"))          # &Englisch

        # the help menu
        self.helpMenu.setTitle(QApplication.translate("MainWindow", "&Help"))                   # &Hilfe
        self.helpContents.setText(QApplication.translate("MainWindow", "Help &Contents"))       # &Hilfe anzeigen
        self.scientificBasis.setText(QApplication.translate("MainWindow", "Specialist &articles")) # &Fachbeiträge
        self.helpAbout.setText(QApplication.translate("MainWindow",
                "&About Wuchshüllenrechner"))                                                   # Über &Wuchshüllenrechner

        # the edit box for data collection
        self.editBox.setTitle(QApplication.translate("MainWindow", "Data collection"))          # Datenerfassung
        self.operationLabel.setText(QApplication.translate("MainWindow",
                "Forestry &operation") + ":")                                                   # Forst&betrieb
        self.districtLabel.setText(QApplication.translate("MainWindow",
                "Forest &district") + ":")                                                      # Forst&revier
        self.managerLabel.setText(QApplication.translate("MainWindow",
                "&District manager") + ":")                                                     # &Revierleiter
        self.locationLabel.setText(QApplication.translate("MainWindow",
                "&Location") + ":")                                                             # &Waldort
        self.taxLabel.setText(QApplication.translate("MainWindow",
                "&Sales tax") + ":")                                                            # Mehrwert&steuer
        self.taxHint.setToolTip(QApplication.translate("MainWindow",
                "Wirkt sich auf Vorgabewerte aus und kann nach\nAnlegen einer "
                "Variante nicht geändert werden."))

        # update the data widget
        self.dataWidget.retranslateUi()

        # update the chart and result view
        self.plotWidget.retranslateUi()


class EnhancedTreeWidget(QWidget):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self):
        super().__init__()

        # things
        self.model = None
        self.tax = True
        self.setContentsMargins(0, 0, 0, 0)

        # create tree view
        self.view = EnhancedTreeView()
        self.view.setUniformRowHeights(True)
        self.view.setItemDelegate(TreeDelegate())
        self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # create buttons
        self.addButton = QPushButton()
        self.addButton.setMinimumWidth(140)
        self.removeButton = QPushButton()
        self.removeButton.setEnabled(False)
        self.modifyButton = QPushButton()
        self.modifyButton.setEnabled(False)
        self.calcButton = QPushButton()
        self.calcButton.setEnabled(False)

        # create button box layout
        buttonBox = QVBoxLayout()
        buttonBox.setContentsMargins(0, 0, 0, 0)
        buttonBox.addWidget(self.addButton)
        buttonBox.addWidget(self.removeButton)
        buttonBox.addWidget(self.modifyButton)
        buttonBox.addSpacing(12)
        buttonBox.addWidget(self.calcButton)
        buttonBox.addStretch()

        # set up main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(buttonBox)
        layout.addWidget(self.view)

        # connect button actions
        self.addButton.clicked.connect(self.addAction)
        self.removeButton.clicked.connect(self.removeAction)
        self.modifyButton.clicked.connect(self.modifyAction)
        self.calcButton.clicked.connect(self.calcAction)
        self.view.doubleClicked.connect(self.modifyAction)

        # translage the gui
        self.retranslateUi()

    def retranslateUi(self):
        # translate the buttons
        self.addButton.setText(QApplication.translate("EnhancedTreeWidget", "Add protection type"))       # Schutz anlegen
        self.removeButton.setText(QApplication.translate("EnhancedTreeWidget", "Remove protection type"))    # Schutz Entfernen
        self.modifyButton.setText(QApplication.translate("EnhancedTreeWidget", "Modify Protection type"))    # Schutz Ändern
        self.calcButton.setText(QApplication.translate("EnhancedTreeWidget", "Calculate"))              # Berechnen

        # translate the view
        self.view.update()

    def setModel(self, model):
        self.model = model
        self.view.setModel(model)

        self.model.itemsInserted.connect(self.setEnabled)
        self.model.allItemsRemoved.connect(self.setDisabled)
        self.model.itemsAboutToBeCalculated.connect(self.setCalculationEnabled)

    def setSelectionModel(self, selectionModel):
        self.view.setSelectionModel(selectionModel)

    def setCalculationEnabled(self, enable):
        self.calcButton.setEnabled(enable)

        # update the view hint
        self.view.hint = not enable

    def setEnabled(self, enable):
        # expand all items
        self.view.expandAll()

        # enable buttons and the view element
        self.removeButton.setEnabled(enable)
        self.modifyButton.setEnabled(enable)
        self.view.setEnabled(enable)

    def clear(self):
        # reset the add button
        self.addButton.setText(QApplication.translate("EnhancedTreeWidget", "Add protection type"))   # Schutz anlegen

        # disable all buttons and the view
        self.removeButton.setEnabled(False)
        self.modifyButton.setEnabled(False)
        self.calcButton.setEnabled(False)

        self.view.hint = True
        self.view.setEnabled(False)

    def setDisabled(self, disable):
        # internaly call the setEnabled function
        # therefore negate the boolean value
        self.setEnabled(not disable)

    def addAction(self):
        # first show relevant information, if necessary
        if self.model.new:
            information = VariantHintDialog()
            information.exec()

        # TODO
        index = self.model.last if self.model.current > -1 else QModelIndex()
        last = self.model.current if self.model.current > -1 else Fence.TYPE
        length = self.model.length
        count = self.model.count

        dialog = VariantDataDialog(self.model.species, tax=self.tax, last=last, index=index, count=count, length=length)
        if dialog.exec() == QDialog.Accepted:
            values = dialog.value
            item = VariantItem(values[TreeModel.NameRole], values[TreeModel.ProtectionRole].TYPE)
            setattr(item, "color", values[TreeModel.ColorRole])
            setattr(item, "plant", values[TreeModel.PlantRole])
            setattr(item, "protection", values[TreeModel.ProtectionRole])
            self.model.insertItem(item)

            # TODO
            self.model.count = dialog.count
            self.model.length = dialog.length

        # modify the create button
        if self.model.current == -1:
            buttonText = QApplication.translate("EnhancedTreeWidget", "Add protection type")       # Schutz anlegen
        elif self.model.current == Fence.TYPE:
            buttonText = QApplication.translate("EnhancedTreeWidget", "Add Fence")             # Zaun anlegen
        else:
            buttonText = QApplication.translate("EnhancedTreeWidget", "Add Tree Shelter")     # Wuchshülle anlegen

        self.addButton.setText(buttonText)

    def modifyAction(self):
        index = self.view.selectionModel().currentIndex()
        item = self.model.itemData(index)
        if item:
            dialog = VariantDataDialog(self.model.species, item, self.tax)
            if dialog.exec() == QDialog.Accepted:
                self.model.setItemData(index, dialog.value)

    def removeAction(self):
        warning = QMessageBox(self)
        warning.setWindowModality(Qt.WindowModal)  # check for mac only
        warning.setIcon(QMessageBox.Warning)
        warning.setStandardButtons(QMessageBox.No|QMessageBox.Yes)
        warning.setDefaultButton(QMessageBox.No)
        warning.setWindowTitle(QApplication.translate("EnhancedTreeWidget", "Wuchshüllenrechner"))
        warning.setText("<b>" + QApplication.translate("EnhancedTreeWidget",
                "Möchten Sie die Schutzvariante wirklich entfernen?") + "</b>")
        warning.setInformativeText(QApplication.translate("VariantPlotWidget",
                "Die Schutzvariante wird endgültig entfernt und kann nicht "
                "mehr wiederhergestellt werden, falls Sie vorher nicht "
                "gespeichert haben."))

        reply = warning.exec()
        if reply == QMessageBox.Yes:
            index = self.view.selectionModel().currentIndex()
            self.model.removeItem(index.row(), index.parent())

            # modify the create button
            self.addButton.setText(QApplication.translate("EnhancedTreeWidget",
                        "Create Protection"))       # Schutz anlegen

    def calcAction(self):
        # an empty list means that the calculation was successful
        shelters = self.model.calculate()
        if shelters:
            notice = QMessageBox(self)
            notice.setWindowModality(Qt.WindowModal)  # check for mac only
            notice.setIcon(QMessageBox.Warning)
            notice.setWindowTitle(QApplication.translate("EnhancedTreeWidget", "Wuchshüllenrechner"))
            notice.setText("<b>" + QApplication.translate("EnhancedTreeWidget",
                    "Bei der Berechnung ist ein Fehler aufgetreten!") + "</b>")
            notice.setInformativeText(QApplication.translate("EnhancedTreeWidget",
                    "Es konnten nicht alle Varianten miteinander verglichen werden."))
            notice.setDetailedText("\n".join(shelters))

            notice.exec()


class EnhancedTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.hint = True

        self.setEnabled(False)
        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)

        self._OXYGEN_PATH_32 = os.path.join("resources", "icons", "oxygen", "32")

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.hint:
            painter = QPainter(self.viewport())
            hintText = QApplication.translate("EnhancedTreeView", "The list "
                    "must contain at least one protection from type\nfence and "
                    "from type tree shelter to complete a calculation!")

            fontMetrics = QFontMetrics(painter.font())
            textWidth = fontMetrics.width(hintText)
            topPosition = self.rect().height() / 2 - 16
            leftPosition = self.rect().width() / 2 - textWidth / 4 - 40

            painter.drawImage(leftPosition, topPosition, QImage(os.path.join(self._OXYGEN_PATH_32, "dialog-warning.png")))
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(self.rect(), Qt.AlignCenter, hintText)

    def mousePressEvent(self, event):
        self.clearSelection()
        super().mousePressEvent(event)
