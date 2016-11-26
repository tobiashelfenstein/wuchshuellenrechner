"""
dialog_data.py -

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


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
import random
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, pyqtProperty
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWizard
from PyQt5.QtWidgets import QWizardPage
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QModelIndex
from lib.variants import Plant, Fence, Tube
from lib import cost as library
from gui.treemodel import TreeModel
import os.path
import sys
import subprocess
from PyQt5.QtWidgets import QToolTip
from gui.widgets import ToolTipLabel
from PyQt5.QtCore import QModelIndex

__version__ = "1.0.0"


class VariantDataDialog(QDialog):
    def __init__(self, species=(), item=None, tax=True, last=0, index=QModelIndex(), count=0, length=0):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()
        self.item = item
        self.value = None
        self.speciesRegistry = species.keys()
        self.species = -1
        self.count = 0
        self.tax = tax
        self.index = index      # the last added index
        self.last = last
        self.count = count
        self.length = length


        self._OXYGEN_PATH_22 = os.path.join("resources", "icons", "oxygen", "22")
        self._LABEL_MIN_WIDTH = 240
        self._piece_unit = " St."
        self._currency_unit = " " + self.locale().currencySymbol(QLocale.CurrencyIsoCode)
        self._currency_unit_piece = self._currency_unit + "/" + self._piece_unit.strip()
        self._spinbox_step = 0.05


        self._COMBOBOX_ITEM_LIST = (QApplication.translate("VariantDataDialog", "Fence"),            # Zaun
                                    QApplication.translate("VariantDataDialog", "Tree shelter"))             # Wuchshülle

        # general things
        self.generalGroup = QGroupBox()

        self.variantInput = QComboBox()
        self.variantInput.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.variantInput.addItems(self._COMBOBOX_ITEM_LIST)
        self.variantLabel = QLabel()
        self.variantLabel.setMinimumWidth(self._LABEL_MIN_WIDTH)
        self.variantLabel.setBuddy(self.variantInput)
        self.variantHint = ToolTipLabel()

        self.descriptionInput = QLineEdit()
        self.descriptionLabel = QLabel()
        self.descriptionLabel.setBuddy(self.descriptionInput)
        self.descriptionHint = ToolTipLabel()

        # create the layout of the general group box
        generalLayout = QGridLayout(self.generalGroup)
        generalLayout.setVerticalSpacing(15)
        generalLayout.addWidget(self.variantLabel, 0, 0, Qt.AlignTop)
        generalLayout.addWidget(self.variantInput, 0, 1, Qt.AlignTop)
        generalLayout.addWidget(self.variantHint, 0, 2, Qt.AlignTop)
        generalLayout.addWidget(self.descriptionLabel, 1, 0, Qt.AlignTop)
        generalLayout.addWidget(self.descriptionInput, 1, 1, Qt.AlignTop)
        generalLayout.addWidget(self.descriptionHint, 1, 2, Qt.AlignTop)

        # plant specific input fields
        self.plantGroup = QGroupBox()

        self.speciesInput = QComboBox()
        self.speciesInput.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.speciesInput.addItems(library.TREESPECIES_DESCRIPTION)
        self.speciesLabel = QLabel()
        self.speciesLabel.setMinimumWidth(self._LABEL_MIN_WIDTH)
        self.speciesLabel.setBuddy(self.speciesInput)
        self.speciesHint = ToolTipLabel()
        self.speciesHint.hide()

        speciesSpacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.speciesWarningSymbol = QLabel(pixmap=QPixmap(os.path.join(self._OXYGEN_PATH_22, "dialog-warning.png")))
        self.speciesWarningSymbol.hide()
        self.speciesWarningText = QLabel(wordWrap=True)
        self.speciesWarningText.hide()
        warningLayout = QHBoxLayout()
        warningLayout.setContentsMargins(0, 0, 0, 0)
        warningLayout.addItem(speciesSpacer)
        warningLayout.addWidget(self.speciesWarningSymbol, alignment=Qt.AlignTop)
        warningLayout.addWidget(self.speciesWarningText, alignment=Qt.AlignTop)

        self.costInput = QDoubleSpinBox()
        self.costInput.setSuffix(self._currency_unit_piece)
        self.costInput.setSingleStep(self._spinbox_step)
        self.costLabel = QLabel()
        self.costLabel.setBuddy(self.costInput)
        self.costHint = ToolTipLabel()
        self.costHint.hide()
        self.costCalculator = QPushButton()

        self.preparationInput = QDoubleSpinBox()
        self.preparationInput.setSuffix(self._currency_unit_piece)
        self.preparationInput.setSingleStep(self._spinbox_step)
        self.preparationLabel = QLabel()
        self.preparationLabel.setBuddy(self.preparationInput)
        self.preparationHint = ToolTipLabel()
        self.preparationHint.hide()
        self.preparationCalculator = QPushButton()

        self.plantingInput = QDoubleSpinBox()
        self.plantingInput.setSuffix(self._currency_unit_piece)
        self.plantingInput.setSingleStep(self._spinbox_step)
        self.plantingLabel = QLabel()
        self.plantingLabel.setBuddy(self.plantingInput)
        self.plantingHint = ToolTipLabel()
        self.plantingHint.hide()
        self.plantingCalculator = QPushButton()

        self.tendingInput = QDoubleSpinBox()
        self.tendingInput.setSuffix(self._currency_unit_piece)
        self.tendingInput.setSingleStep(self._spinbox_step)
        self.tendingLabel = QLabel()
        self.tendingLabel.setBuddy(self.tendingInput)
        self.tendingHint = ToolTipLabel()
        self.tendingHint.hide()
        self.tendingCalculator = QPushButton()

        self.mortalityInput = QSpinBox()
        self.mortalityInput.setSuffix(" %")
        self.mortalityInput.setMaximum(100)
        self.mortalityInput.setValue(0)
        self.mortalityInput.setDisabled(True)
        self.mortalityLabel = QLabel()
        self.mortalityLabel.setBuddy(self.mortalityInput)
        self.mortalityHint = ToolTipLabel()
        self.mortalityHint.hide()

        # create the layout of the plant group box
        plantLayout = QGridLayout(self.plantGroup)
        plantLayout.addWidget(self.speciesLabel, 0, 0)
        plantLayout.addWidget(self.speciesInput, 0, 1)
        plantLayout.addWidget(self.speciesHint, 0, 2)
        plantLayout.addLayout(warningLayout, 1, 1)
        plantLayout.addWidget(self.costLabel, 2, 0)
        plantLayout.addWidget(self.costInput, 2, 1)
        plantLayout.addWidget(self.costHint, 2, 2)
        plantLayout.addWidget(self.costCalculator, 2, 3)
        plantLayout.addWidget(self.preparationLabel, 3, 0)
        plantLayout.addWidget(self.preparationInput, 3, 1)
        plantLayout.addWidget(self.preparationHint, 3, 2)
        plantLayout.addWidget(self.preparationCalculator, 3, 3)
        plantLayout.addWidget(self.plantingLabel, 4, 0)
        plantLayout.addWidget(self.plantingInput, 4, 1)
        plantLayout.addWidget(self.plantingHint, 4, 2)
        plantLayout.addWidget(self.plantingCalculator, 4, 3)
        plantLayout.addWidget(self.tendingLabel, 5, 0)
        plantLayout.addWidget(self.tendingInput, 5, 1)
        plantLayout.addWidget(self.tendingHint, 5, 2)
        plantLayout.addWidget(self.tendingCalculator, 5, 3)
        plantLayout.addWidget(self.mortalityLabel, 6, 0)
        plantLayout.addWidget(self.mortalityInput, 6, 1)
        plantLayout.addWidget(self.mortalityHint, 6, 2)

        # stacked widget for protection group
        self.fenceWidget = FenceInputWidget(self.tax)
        self.fenceWidget.length = self.length
        self.tubeWidget = TubeInputWidget(self.tax)

        self.protectionGroup = QStackedWidget()
        self.protectionGroup.addWidget(self.fenceWidget)
        self.protectionGroup.addWidget(self.tubeWidget)

        # sales tax hint
        taxLabel = QLabel("*) " + QApplication.translate("VariantDataDialog",                      # Bitte beachten Sie, dass Sie den Variantentyp später nicht mehr ändern können.
                "Keep in mind, that all values must contain uniformly "
                "the sales tax or not."),
                wordWrap=True)

        # create an ok button and abort button within a button box
        lineFrame = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.VLine)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel|QDialogButtonBox.Help,
                orientation=Qt.Vertical)

        # create main layout
        dataLayout = QVBoxLayout()
        dataLayout.addWidget(self.generalGroup)
        dataLayout.addWidget(self.plantGroup)
        dataLayout.addWidget(self.protectionGroup)
        dataLayout.addWidget(taxLabel)
        dataLayout.addStretch()

        layout = QHBoxLayout(self)
        layout.addLayout(dataLayout)
        layout.addWidget(lineFrame)
        layout.addWidget(self.buttonBox)

        # connect actions
        self.variantInput.currentIndexChanged.connect(self.variantChanged)

        self.speciesInput.currentIndexChanged.connect(self.checkSpecies)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.helpRequested.connect(self.help)

        self.costCalculator.clicked.connect(self.costCalculation)
        self.preparationCalculator.clicked.connect(self.preparationCalculation)
        self.plantingCalculator.clicked.connect(self.plantingCalculation)
        self.tendingCalculator.clicked.connect(self.tendingCalculation)

        self.tubeWidget.countChanged.connect(self.updateCount)
        self.fenceWidget.lengthChanged.connect(self.updateLength)

        # update input fields
        if self.item:
            plant = self.item[TreeModel.PlantRole]
            protection = self.item[TreeModel.ProtectionRole]

            self.species = plant.species

            # update input fields
            self.variantInput.setCurrentIndex(protection.TYPE)
            self.variantInput.setDisabled(True)
            self.descriptionInput.setText(self.item[TreeModel.NameRole])
            self.speciesInput.setCurrentIndex(plant.species)
            self.costInput.setValue(plant.cost)
            self.preparationInput.setValue(plant.preparation)
            self.plantingInput.setValue(plant.planting)
            self.tendingInput.setValue(plant.tending)
            self.mortalityInput.setValue(plant.mortality * 100)

            # update the protection group
            self.protectionGroup.currentWidget().setValues(protection)
        else:
            self.variantInput.setCurrentIndex(self.last)
            if self.index.isValid():
                self.speciesInput.setCurrentIndex(self.index.data(TreeModel.SpeciesRole))

        # check the species and show
        # a warning, if necessary
        self.checkSpecies()

        # translate the graphical user interface
        self.retranslateUi()

    def updateCount(self, count):
        # TODO
        self.count = count

    def updateLength(self, length):
        # TODO
        self.length = length

    def retranslateUi(self):
        # dialog title
        self.setWindowTitle(QApplication.translate("VariantDataDialog", "Edit protection"))                         # Schutz bearbeiten

        # variant selection
        self.generalGroup.setTitle(QApplication.translate("VariantDataDialog", "Selection of protection"))          # Auswahl des Schutzes
        self.variantLabel.setText(QApplication.translate("VariantDataDialog", "Protection type") + ":")             # Schutztyp
        self.descriptionLabel.setText(QApplication.translate("VariantDataDialog", "Protection description") + ":")     # Schutzbeschreibung
        self.variantHint.setToolTip(QApplication.translate("VariantDataDialog",                                     # Bitte beachten Sie, dass Sie den Variantentyp später nicht mehr ändern können.
                "Keep in mind, that you can't change the variant type "
                "at a later time."))
        self.descriptionHint.setToolTip(QApplication.translate("VariantDataDialog",                                 # Geben Sie eine Beschreibung der Variante ein, um sie später identifizieren zu können.
                "Please describe the variant. The description helps you "
                "identify it."))

        # plant input
        self.plantGroup.setTitle(QApplication.translate("VariantDataDialog", "Cost of plants and planting"))        # Kosten Pflanze und Pflanzung
        self.speciesLabel.setText(QApplication.translate("VariantDataDialog", "Tree species") + ":")                # Baumart
        self.speciesHint.setToolTip("Text")
        self.speciesWarningText.setText(QApplication.translate("VariantDataDialog",
                "A fence with the selected species exists already!"))                                               # Es existiert bereits ein Zaun mit der ausgewählten Baumart!
        self.costLabel.setText(QApplication.translate("VariantDataDialog", "Unit cost") + "*:")                     # Stückkosten
        self.costHint.setToolTip("Text")
        self.costCalculator.setText(QApplication.translate("VariantDataDialog", "Calculation help"))                # Umrechnungshilfe
        self.preparationLabel.setText(QApplication.translate("VariantDataDialog", "Cost of preparation") + "*:")    # Kulturvorbereitung
        self.preparationHint.setToolTip("Text")
        self.preparationCalculator.setText(QApplication.translate("VariantDataDialog", "Calculation help"))         # Umrechnungshilfe
        self.plantingLabel.setText(QApplication.translate("VariantDataDialog", "Cost of planting") + "*:")          # Pflanzungskosten
        self.plantingHint.setToolTip("Text")
        self.plantingCalculator.setText(QApplication.translate("VariantDataDialog", "Calculation help"))            # Umrechnungshilfe
        self.tendingLabel.setText(QApplication.translate("VariantDataDialog", "Cost of tending (5 years)") + "*:")  # Kultursicherung
        self.tendingHint.setToolTip("Text")
        self.tendingCalculator.setText(QApplication.translate("VariantDataDialog", "Calculation help"))             # Umrechnungshilfe
        self.mortalityLabel.setText(QApplication.translate("MainWindow", "Decreased &mortality over fence") + ":")  # &Mortalitätsrate
        self.mortalityHint.setToolTip("Text")

    def help(self):
        # create the documentation path with
        # the current locale settings
        docFile = os.path.join("doc", "documentation_"
                + self.locale().name()[:2] + ".pdf")

        # on every platfrom a different
        # start operation is needed
        if sys.platform == "win32":
            os.startfile(docFile)
        elif sys.platform == "darwin":
            subprocess.call(("open", docFile))
        elif sys.platform.startswith("linux"):
            subprocess.call(("xdg-open", docFile))

    def variantChanged(self, index):
        # check for species
        self.checkSpecies()

        # update the visible status of the mortality input
        if index == Tube.TYPE:
            self.mortalityInput.setValue(10)
            self.mortalityInput.setEnabled(True)
        else:
            self.mortalityInput.setValue(0)
            self.mortalityInput.setDisabled(True)

        # set up the protection group
        self.protectionGroup.setCurrentIndex(index)

    def accept(self):
        # check name input field
        if not self.descriptionInput.text():
            warning = QMessageBox(self)
            warning.setWindowModality(Qt.WindowModal)  # check for mac only
            warning.setIcon(QMessageBox.Warning)
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setWindowTitle(QApplication.translate("VariantDataDialog", "Wuchshüllenrechner"))
            warning.setText("<b>" + QApplication.translate("VariantDataDialog",
                    "The variant description is missing!") + "</b>")
            warning.setInformativeText(QApplication.translate("VariantDataDialog",
                    "Please describe your new variant."))

            warning.exec()
        else:
            # return the input values
            plant = Plant()
            plant.species = self.speciesInput.currentIndex()
            plant.cost = self.costInput.value()
            plant.preparation = self.preparationInput.value()
            plant.planting = self.plantingInput.value()
            plant.tending = self.tendingInput.value()
            plant.mortality = self.mortalityInput.value() / 100 if self.mortalityInput.value() > 0 else 0

            protection = self.protectionGroup.currentWidget().values()

            if not self.item:
                if protection.TYPE == Fence.TYPE:
                    color = QColor(255, 0, 0).name()
                else:
                    color = QColor(random.randint(0, 256), random.randint(0, 256),
                            random.randint(0, 256)).name()
            else:
                color = self.item[TreeModel.ColorRole]

            self.value = {
                TreeModel.NameRole : self.descriptionInput.text(),
                TreeModel.ColorRole : color,
                TreeModel.StatusRole : True,
                TreeModel.PlantRole : plant,
                TreeModel.ProtectionRole : protection
            }

            super().accept()

    def checkSpecies(self):
        species = self.speciesInput.currentIndex()

        # only for fence variants
        if self.variantInput.currentIndex() == Fence.TYPE:
            if not species == self.species and species in self.speciesRegistry:
                # first disable the OK button
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                self.speciesWarningSymbol.show()
                self.speciesWarningText.show()
            else:
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                self.speciesWarningSymbol.hide()
                self.speciesWarningText.hide()
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.speciesWarningSymbol.hide()
            self.speciesWarningText.hide()

    def costCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.costInput.setValue(value)

    def preparationCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.preparationInput.setValue(value)

    def plantingCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.plantingInput.setValue(value)

    def tendingCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.tendingInput.setValue(value)

    def unitCostCalculator(self):
        dialog = UnitCostDialog(self.count)
        dialog.exec()

        # TODO
        self.count = dialog.count
        self.tubeWidget.count = self.count

        return dialog.value


class FenceInputWidget(QGroupBox):
    """Acquires a new plant protection variant for the cost calculation.

    The dialog contains two input fields to acquire a new plant protection variant.
    First there is a input field for the name of the new variant. The second
    input field asks about the used plant protection. The user cannot change
    the variant type at a later time.
    This class has no attributes or return values.

    """

    lengthChanged = pyqtSignal(int)

    def __init__(self, tax=True):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()

        self._LABEL_MIN_WIDTH = 240
        self._piece_unit = " St."
        self._length_unit = " Lfm."
        self._currency_unit = " " + self.locale().currencySymbol(QLocale.CurrencyIsoCode)
        self._currency_unit_length = self._currency_unit + "/" + self._length_unit.strip()
        self._spinbox_step = 0.05
        self.length = 0

        # determine the sales tax
        self.tax = 1.0 + library.SALES_TAX if tax else 1.0

        # input fields
        self.fenceInput = QComboBox()
        self.fenceInput.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.fenceInput.addItems(library.FENCE_DESCRIPTION)
        self.fenceLabel = QLabel()
        self.fenceLabel.setMinimumWidth(self._LABEL_MIN_WIDTH)
        self.fenceLabel.setBuddy(self.fenceInput)
        self.fenceHint = ToolTipLabel()
        self.fenceHint.hide()

        self.installationInput = QDoubleSpinBox()
        self.installationInput.setSuffix(self._currency_unit_length)
        self.installationInput.setSingleStep(self._spinbox_step)
        self.installationLabel = QLabel()
        self.installationLabel.setBuddy(self.installationInput)
        self.installationHint = ToolTipLabel()
        self.installationHint.hide()
        self.installationCalculator = QPushButton()

        self.maintenanceInput = QDoubleSpinBox()
        self.maintenanceInput.setSuffix(self._currency_unit_length)
        self.maintenanceInput.setSingleStep(self._spinbox_step)
        self.maintenanceLabel = QLabel()
        self.maintenanceLabel.setBuddy(self.maintenanceInput)
        self.maintenanceHint = ToolTipLabel()
        self.maintenanceHint.hide()

        self.removalInput = QDoubleSpinBox()
        self.removalInput.setSuffix(self._currency_unit_length)
        self.removalInput.setSingleStep(self._spinbox_step)
        self.removalLabel = QLabel()
        self.removalLabel.setBuddy(self.removalInput)
        self.removalHint = ToolTipLabel()
        self.removalHint.hide()

        spacerBottom = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # create the layout of the plant group box
        layout = QGridLayout(self)
        layout.addWidget(self.fenceLabel, 0, 0)
        layout.addWidget(self.fenceInput, 0, 1)
        layout.addWidget(self.fenceHint, 0, 2)
        layout.addWidget(self.installationLabel, 1, 0)
        layout.addWidget(self.installationInput, 1, 1)
        layout.addWidget(self.installationHint, 1, 2)
        layout.addWidget(self.installationCalculator, 1, 3)
        layout.addWidget(self.maintenanceLabel, 2, 0)
        layout.addWidget(self.maintenanceInput, 2, 1)
        layout.addWidget(self.maintenanceHint, 2, 2)
        layout.addWidget(self.removalLabel, 3, 0)
        layout.addWidget(self.removalInput, 3, 1)
        layout.addWidget(self.removalHint, 3, 2)
        layout.addItem(spacerBottom, 4, 0, 1, 3)

        # connect actions
        self.installationCalculator.clicked.connect(self.installationCalculation)
        self.fenceInput.currentIndexChanged.connect(self.updateCost)

        # translate the graphical user interface
        self.retranslateUi()

    def retranslateUi(self):
        # group title
        self.setTitle(QApplication.translate("FenceInputWidget", "Cost of fence and maintenance"))                  # Kosten Zaun und Unterhaltung

        # fence
        self.fenceLabel.setText(QApplication.translate("FenceInputWidget", "Fence type") + ":")                     # Zauntyp
        self.fenceHint.setToolTip("Text")
        self.installationLabel.setText(QApplication.translate("FenceInputWidget", "Cost of installation") + "*:")   # Installationskosten
        self.installationHint.setToolTip("Text")
        self.installationCalculator.setText(QApplication.translate("FenceInputWidget", "Calculation help"))         # Umrechnungshilfe
        self.maintenanceLabel.setText(QApplication.translate("FenceInputWidget", "Cost of maintenance") + "*:")     # Unterhaltungskosten
        self.maintenanceHint.setToolTip("Text")
        self.removalLabel.setText(QApplication.translate("FenceInputWidget", "Cost of removal") + "*:")             # Abbaukosten
        self.removalHint.setToolTip("Text")

    def setValues(self, protection):
        self.fenceInput.setCurrentIndex(protection.model)
        self.installationInput.setValue(protection.installation / 3)
        self.maintenanceInput.setValue(protection.installation / 3)
        self.removalInput.setValue(protection.installation / 3)

    def values(self):
        protection = Fence()
        protection.model = self.fenceInput.currentIndex()
        protection.installation = self.installationInput.value() + self.maintenanceInput.value() + self.removalInput.value()

        return protection

    def updateCost(self, index):
        cost = library.FENCE_COST[index] * self.tax / 3

        self.installationInput.setValue(cost)
        self.maintenanceInput.setValue(cost)
        self.removalInput.setValue(cost)

    def installationCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.installationInput.setValue(value)

    def unitCostCalculator(self):
        dialog = UnitCostDialog(self.length, False)
        dialog.exec()

        # TODO
        self.length = dialog.count
        self.lengthChanged.emit(self.length)

        return dialog.value


class TubeInputWidget(QGroupBox):
    """Acquires a new plant protection variant for the cost calculation.

    The dialog contains two input fields to acquire a new plant protection variant.
    First there is a input field for the name of the new variant. The second
    input field asks about the used plant protection. The user cannot change
    the variant type at a later time.
    This class has no attributes or return values.

    """

    countChanged = pyqtSignal(int)

    def __init__(self, tax=True):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()

        self.count = 0

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self._LABEL_MIN_WIDTH = 240
        self._piece_unit = " St."
        self._currency_unit = " " + self.locale().currencySymbol(QLocale.CurrencyIsoCode)
        self._currency_unit_piece = self._currency_unit + "/" + self._piece_unit.strip()
        self._spinbox_step = 0.05

        # determine the sales tax
        self.tax = 1.0 + library.SALES_TAX if tax else 1.0

        # input fields
        self.tubeInput = QComboBox()
        self.tubeInput.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.tubeInput.addItems(library.TREESHELTERS_DESCRIPTION)
        self.tubeLabel = QLabel()
        self.tubeLabel.setMinimumWidth(self._LABEL_MIN_WIDTH)
        self.tubeLabel.setBuddy(self.tubeInput)
        self.tubeHint = ToolTipLabel()
        self.tubeHint.hide()

        self.costInput = QDoubleSpinBox()
        self.costInput.setSuffix(self._currency_unit_piece)
        self.costInput.setSingleStep(self._spinbox_step)
        self.costLabel = QLabel()
        self.costLabel.setBuddy(self.costInput)
        self.costHint = ToolTipLabel()
        self.costHint.hide()
        self.costCalculator = QPushButton()

        self.accessoriesInput = QDoubleSpinBox()
        self.accessoriesInput.setSuffix(self._currency_unit_piece)
        self.accessoriesInput.setSingleStep(self._spinbox_step)
        self.accessoriesLabel = QLabel()
        self.accessoriesLabel.setBuddy(self.accessoriesInput)
        self.accessoriesHint = ToolTipLabel()
        self.accessoriesHint.hide()
        self.accessoriesCalculator = QPushButton()

        self.installationInput = QDoubleSpinBox()
        self.installationInput.setSuffix(self._currency_unit_piece)
        self.installationInput.setSingleStep(self._spinbox_step)
        self.installationLabel = QLabel()
        self.installationLabel.setBuddy(self.installationInput)
        self.installationHint = ToolTipLabel()
        self.installationHint.hide()
        self.installationCalculator = QPushButton()

        self.maintenanceInput = QDoubleSpinBox()
        self.maintenanceInput.setSuffix(self._currency_unit_piece)
        self.maintenanceInput.setSingleStep(self._spinbox_step)
        self.maintenanceLabel = QLabel()
        self.maintenanceLabel.setBuddy(self.maintenanceInput)
        self.maintenanceHint = ToolTipLabel()
        self.maintenanceHint.hide()

        self.removalInput = QDoubleSpinBox()
        self.removalInput.setSuffix(self._currency_unit_piece)
        self.removalInput.setSingleStep(self._spinbox_step)
        self.removalLabel = QLabel()
        self.removalLabel.setBuddy(self.removalInput)
        self.removalHint = ToolTipLabel()
        self.removalHint.hide()

        spacerBottom = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # create the layout of the plant group box
        layout = QGridLayout(self)
        layout.addWidget(self.tubeLabel, 0, 0)
        layout.addWidget(self.tubeInput, 0, 1)
        layout.addWidget(self.tubeHint, 0, 2)
        layout.addWidget(self.costLabel, 1, 0)
        layout.addWidget(self.costInput, 1, 1)
        layout.addWidget(self.costHint, 1, 2)
        layout.addWidget(self.costCalculator, 1, 3)
        layout.addWidget(self.accessoriesLabel, 2, 0)
        layout.addWidget(self.accessoriesInput, 2, 1)
        layout.addWidget(self.accessoriesHint, 2, 2)
        layout.addWidget(self.accessoriesCalculator, 2, 3)
        layout.addWidget(self.installationLabel, 3, 0)
        layout.addWidget(self.installationInput, 3, 1)
        layout.addWidget(self.installationHint, 3, 2)
        layout.addWidget(self.installationCalculator, 3, 3)
        layout.addWidget(self.maintenanceLabel, 4, 0)
        layout.addWidget(self.maintenanceInput, 4, 1)
        layout.addWidget(self.maintenanceHint, 4, 2)
        layout.addWidget(self.removalLabel, 5, 0)
        layout.addWidget(self.removalInput, 5, 1)
        layout.addWidget(self.removalHint, 5, 2)
        layout.addItem(spacerBottom, 7, 0, 1, 3)

        # connect actions
        self.tubeInput.currentIndexChanged.connect(self.updateCost)
        self.costCalculator.clicked.connect(self.costCalculation)
        self.accessoriesCalculator.clicked.connect(self.accessoriesCalculation)
        self.installationCalculator.clicked.connect(self.installationCalculation)

        #self.installationInput.valueChanged.connect(self.updateMaintenanceAndRemoval)

        # translate the graphical user interface
        self.retranslateUi()

    def retranslateUi(self):
        # group title
        self.setTitle(QApplication.translate("TubeInputWidget", "Cost of tree shelter and maintenance"))            # Kosten Wuchshülle und Unterhaltung

        # tree shelter
        self.tubeLabel.setText(QApplication.translate("TubeInputWidget", "Tree shelter type") + ":")                # Wuchshüllentyp
        self.tubeHint.setToolTip("Text")
        self.costLabel.setText(QApplication.translate("TubeInputWidget", "Unit cost") + "*:")                       # Stückkosten
        self.costHint.setToolTip("Text")
        self.costCalculator.setText(QApplication.translate("TubeInputWidget", "Calculation help"))                  # Umrechnungshilfe
        self.accessoriesLabel.setText(QApplication.translate("TubeInputWidget", "Cost of accessories") + "*:")      # Stückkosten
        self.accessoriesHint.setToolTip("Text")
        self.accessoriesCalculator.setText(QApplication.translate("TubeInputWidget", "Calculation help"))           # Umrechnungshilfe
        self.installationLabel.setText(QApplication.translate("TubeInputWidget", "Cost of installation") + "*:")    # Installationskosten
        self.installationHint.setToolTip("Text")
        self.installationCalculator.setText(QApplication.translate("TubeInputWidget", "Calculation help"))          # Umrechnungshilfe
        self.maintenanceLabel.setText(QApplication.translate("TubeInputWidget", "Cost of maintenance") + "*:")      # Unterhaltungskosten
        self.maintenanceHint.setToolTip("Text")
        self.removalLabel.setText(QApplication.translate("TubeInputWidget", "Cost of removal") + "*:")              # Entsorgungskosten
        self.removalHint.setToolTip("Text")

    def setValues(self, protection):
        self.tubeInput.setCurrentIndex(protection.model)
        self.costInput.setValue(protection.cost)
        self.accessoriesInput.setValue(protection.accessories)
        self.installationInput.setValue(protection.installation)
        self.maintenanceInput.setValue(protection.maintenance)
        self.removalInput.setValue(protection.removal)

    def values(self):
        protection = Tube()
        protection.model = self.tubeInput.currentIndex()
        protection.cost = self.costInput.value()
        protection.accessories = self.accessoriesInput.value()
        protection.installation = self.installationInput.value()
        protection.maintenance =  self.maintenanceInput.value()
        protection.removal = self.removalInput.value()

        return protection

    def updateCost(self, index):
        # update tube cost
        self.costInput.setValue(library.TREESHELTERS_COST[index] * self.tax)

        # search the stake cost
        height = library.TREESHELTERS_HEIGHT[index]
        if height > 0:
            for i, stake in enumerate(library.STAKES_HEIGHT):
                if stake > height:
                    cost = library.STAKES_COST[i] * self.tax
                    break
        else:
            cost = 0

        self.accessoriesInput.setValue(cost)

        # installation cost
        if self.tubeInput.currentIndex():
            self.installationInput.setValue(library.TREESHELTERS_INSTALLATION * self.tax)
        else:
            self.installationInput.setValue(0)

        # removal cost
        if not self.tubeInput.currentIndex() in library.TREESHELTERS_NO_REMOVAL:
            self.removalInput.setValue(library.TREESHELTERS_REMOVAL * self.tax)
        else:
            self.removalInput.setValue(0)

    def updateMaintenanceAndRemoval(self, value):
        # 1/3 rule
        if not (self.maintenanceInput.value() and self.removalInput.value()):
            self.maintenanceInput.setValue(value)
            self.removalInput.setValue(value)

    def costCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.costInput.setValue(value)

    def accessoriesCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.accessoriesInput.setValue(value)

    def installationCalculation(self):
        value = self.unitCostCalculator()
        if value > 0:
            self.installationInput.setValue(value)

    def unitCostCalculator(self):
        dialog = UnitCostDialog(self.count)
        dialog.exec()

        # TODO
        self.count = dialog.count
        self.countChanged.emit(self.count)

        return dialog.value


class UnitCostDialog(QDialog):

    def __init__(self, count=0, piece=True):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()

        self.piece = piece

        self.count = count
        self.cost = 0
        self.total = 0
        self.value = 0

        # TODO
        self._LABEL_MIN_WIDTH = 75
        self._piece_unit = " St."
        self._length_unit = " Lfm."
        self._area_unit = " ha"
        self._currency_unit = " " + self.locale().currencySymbol(QLocale.CurrencyIsoCode)
        self._currency_unit_area = self._currency_unit + "/" + self._area_unit.strip()
        self._input_name = ""
        self._input_unit = ""
        if self.piece:
            self._currency_unit_container = self._currency_unit + "/" + self._piece_unit.strip()
            self._input_name = QApplication.translate("UnitCostDialog", "Number of plants")
            self._input_unit = self._piece_unit
        else:
            self._currency_unit_container = self._currency_unit + "/" + self._length_unit.strip()
            self._input_name = QApplication.translate("UnitCostDialog", "Fence length")
            self._input_unit = self._length_unit
        self._spinbox_step = 0.05

        # input group box
        inputGroup = QGroupBox(QApplication.translate("UnitCostDialog", "User input"))     # Benutzereingaben
        inputGroup.setFlat(True)

        self.areaInput = QDoubleSpinBox(decimals=1, maximum=99999, singleStep=0.1, suffix=self._area_unit, value=1.0)
        areaLabel = QLabel(QApplication.translate("UnitCostDialog", "Area") + ":")             # Fläche
        areaLabel.setMinimumWidth(self._LABEL_MIN_WIDTH)
        areaLabel.setBuddy(self.areaInput)

        self.countInput = self.countInput = QSpinBox(self, maximum=99999, suffix=self._input_unit)
        self.countInput.setValue(self.count)
        self.countLabel = QLabel(self._input_name + ":")
        self.countLabel.setBuddy(self.countInput)

        self.costInput = QDoubleSpinBox(maximum=99999)
        self.costInput.setSuffix(self._currency_unit_area)
        self.costInput.setSingleStep(self._spinbox_step)
        costLabel = QLabel(QApplication.translate("UnitCostDialog", "Cost/ha") + ":")       # Kosten/ha
        costLabel.setBuddy(self.costInput)

        spacerAlternative = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        alternativeLabel = QLabel(QApplication.translate("UnitCostDialog", "Alternative user input") + ":")       # Alternative Benutzereingabe

        self.totalInput = QDoubleSpinBox(maximum=999999)
        self.totalInput.setSuffix(self._currency_unit)
        self.totalInput.setSingleStep(self._spinbox_step)
        totalLabel = QLabel(QApplication.translate("UnitCostDialog", "Total cost") + ":")       # Gesamtkosten
        totalLabel.setBuddy(self.totalInput)

        # create input group box layout
        inputLayout = QGridLayout(inputGroup)
        inputLayout.addWidget(areaLabel, 0, 0)
        inputLayout.addWidget(self.areaInput, 0, 1)
        inputLayout.addWidget(self.countLabel, 1, 0)
        inputLayout.addWidget(self.countInput, 1, 1)
        inputLayout.addWidget(costLabel, 2, 0)
        inputLayout.addWidget(self.costInput, 2, 1)
        inputLayout.addItem(spacerAlternative, 3, 0, 1, 2)
        inputLayout.addWidget(alternativeLabel, 4, 0, 1, 2)
        inputLayout.addWidget(totalLabel, 5, 0)
        inputLayout.addWidget(self.totalInput, 5, 1)

        # result group box
        resultGroup = QGroupBox(QApplication.translate("UnitCostDialog", "Calculation results"))     # Berechnungsergebnisse
        resultGroup.setFlat(True)

        self.unitResult = QLabel("0.00" + self._currency_unit_container)
        if self.piece:
            unitLabel = QLabel(QApplication.translate("UnitCostDialog", "Unit cost") + ":")       # Stückkosten
        else:
            unitLabel = QLabel(QApplication.translate("UnitCostDialog", "Fence cost") + ":")       # Zaunkosten
        unitLabel.setFixedWidth(self._LABEL_MIN_WIDTH)
        unitLabel.setBuddy(self.unitResult)

        # create input group box layout
        resultLayout = QGridLayout(resultGroup)
        resultLayout.addWidget(unitLabel, 0, 0)
        resultLayout.addWidget(self.unitResult, 0, 1)

        # create button box
        lineFrame = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.HLine)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        # create dialog main layout
        layout = QVBoxLayout(self)
        layout.addWidget(inputGroup)
        layout.addWidget(resultGroup)
        layout.addWidget(lineFrame)
        layout.addWidget(self.buttonBox)

        # connect actions
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.areaInput.valueChanged.connect(self.calculateTotal)
        self.countInput.valueChanged.connect(self.calculateTotal)
        self.costInput.valueChanged.connect(self.calculateTotal)
        self.totalInput.valueChanged.connect(self.calculateCost)

    def calculateTotal(self):
        self.count = self.countInput.value()
        self.cost = self.costInput.value()
        self.total = self.areaInput.value() * self.cost

        # update the total cost field
        self.totalInput.setValue(self.total)

        # calculate the unit cost
        self.calculate()

    def calculateCost(self):
        self.total = self.totalInput.value()
        if self.areaInput.value() > 0:
            self.cost = self.total / self.areaInput.value()
        else:
            self.cost = 0

        # update the cost field
        self.costInput.setValue(self.cost)

        # calculate the unit cost
        self.calculate()

    def calculate(self):
        # first calculate the value
        if self.count > 0:
            self.value = self.total / self.count
        else:
            self.value = 0

        # update results
        self.unitResult.setText("{:.2f}".format(self.value) + self._currency_unit_container)


class VariantHintDialog(QDialog):
    def __init__(self):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()

        # information about sales tax
        self.taxHeadline = QLabel()
        self.taxHint = QLabel(wordWrap=True)

        # information about associated employer outlay
        self.outlayHeadline = QLabel()
        self.outlayHint = QLabel(wordWrap=True)

        # create an ok button and abort button within a button box
        line = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.HLine)
        button = QDialogButtonBox(QDialogButtonBox.Ok)

        # create the dialog layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.taxHeadline)
        layout.addWidget(self.taxHint)
        layout.addSpacing(15)
        layout.addWidget(self.outlayHeadline)
        layout.addWidget(self.outlayHint)
        layout.addWidget(line)
        layout.addWidget(button)

        # connect the button action
        button.accepted.connect(self.accept)

        # translate the graphical user interface
        self.retranslateUi()

    def retranslateUi(self):
        # main window title
        self.setWindowTitle(QApplication.translate("VariantHintDialog", "Relevant information"))          # Nützliche Hinweise

        # sales tax
        self.taxHeadline.setText("<b>" + QApplication.translate("VariantHintDialog", "Sales tax") + "</b>")
        self.taxHint.setText(QApplication.translate("VariantHintDialog",
                "Wirkt sich auf Vorgabewerte aus und kann nach Anlegen einer "
                "Variante nicht geändert werden."))

        # associated employer outlay
        self.outlayHeadline.setText("<b>" + QApplication.translate("VariantHintDialog", "Associated employer outlay") + "</b>")
        self.outlayHint.setText(QApplication.translate("VariantHintDialog",
                "Berücksichtigen Sie bitte die gegebenenfalls vorhandenen "
                "Lohnnebenkosten im jeweiligen Eingabefeld."))
