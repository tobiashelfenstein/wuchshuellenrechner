"""
widget_plot.py -

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


import numpy as np
from pyqtgraph import GraphicsView
from pyqtgraph import PlotItem
from pyqtgraph import PlotWidget
from pyqtgraph import ViewBox
from pyqtgraph import AxisItem
from pyqtgraph import PlotCurveItem
from pyqtgraph import InfiniteLine
from pyqtgraph import TextItem
from pyqtgraph import ArrowItem
from pyqtgraph import GraphicsObject
from pyqtgraph import Point
from pyqtgraph.exporters import ImageExporter
from pyqtgraph.python2_3 import asUnicode
import pyqtgraph
from PyQt5.QtCore import Qt, QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QBoxLayout
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtGui import QGraphicsScene
from PyQt5.QtGui import QGraphicsProxyWidget
from gui.treemodel import TreeModel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Signal
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtProperty
from PyQt5.QtWidgets import QColorDialog
from gui.dialog_data import VariantDataDialog
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
import os.path
import sys
import subprocess

import numpy



LENGTH_COEFFICIENT = 1.5
COLOR_TRANSPARENCY = 0.3


class VariantPlotView(QGroupBox):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self):
        super().__init__()

        # information widget
        self.plotWidget = VariantPlotWidget()
        self.infoWidget = VariantInfoWidget()

        # splitter settings
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.plotWidget)
        splitter.addWidget(self.infoWidget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        # layout
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(splitter)
        self.setLayout(layout)

        # connect signals
        self.plotWidget.curvePlotted.connect(self.infoWidget.updateResults)
        self.plotWidget.plotReady.connect(self.infoWidget.showResults)
        self.plotWidget.cleared.connect(self.infoWidget.clear)
        self.infoWidget.legendChanged.connect(self.plotWidget.paintCalculation)

        # translate the graphical user interface
        self.retranslateUi()

    def setModel(self, model):
        self.plotWidget.setModel(model)
        self.infoWidget.setModel(model)

    def setSelectionModel(self, selectionModel):
        self.plotWidget.setSelectionModel(selectionModel)

    def clear(self):
        self.plotWidget.clear()
        self.plotWidget.setDisabled(True)
        self.infoWidget.clear()

    def retranslateUi(self):
        # title of the group box
        self.setTitle(QApplication.translate("VariantPlotView", "Chart and result view"))          # Diagramm- und Ergebnisansicht

        # repaint the calculation
        self.plotWidget.retranslateUi()
        self.infoWidget.showResults()


class VariantInfoWidget(QWidget):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """
    legendChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(220)
        self._OXYGEN_PATH_22 = os.path.join("resources", "icons", "oxygen", "22")

        self.model = None
        self.curves = []

        self.results = QWidget()

        # main layout
        self.layout = QVBoxLayout(self)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.results)

        self.showResults()

    def setModel(self, model):
        self.model = model
        self.model.dataChanged.connect(self.update)
        #self.model.modelReset.connect(self.update)
        self.model.modelReset.connect(self.clear)

        # das muss optimiert werden, weil dies private Signale sind
        # es dient dazu, dass gelöschte, oder veränderte (verschobene) Zeilen
        # nicht mehr ausgewählt werden können (selectionModel)
        #self.model.rowsRemoved.connect(self.clear)
        #self.model.rowsMoved.connect(self.clear)

        #self.model.calculated.connect(self.calculate)

    def clear(self):
        self.curves.clear()
        self.showResults()

    def updateResults(self, index):
        self.curves.append(index)

    def updateColor(self, index, color):
        self.model.setData(index, color.name(), TreeModel.ColorRole)
        self.legendChanged.emit()

    def showResults(self):
        new = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # title label of the results area
        self.titleLabel = QLabel("<b>" + QApplication.translate("VariantInfoWidget", "Legend and result(s)") + ":</b>")
        layout.addWidget(self.titleLabel)

        if self.curves:
            # headline
            description = QLabel(QApplication.translate("VariantInfoWidget", "Break even line for"))
            layout.addSpacing(10)
            layout.addWidget(description)

            # show legend for all plotted curves
            for curve in self.curves:
                layout.addSpacing(6)
                vertical = QHBoxLayout()
                vertical.setContentsMargins(0, 0, 0, 0)
                line = ColorLine(curve)
                line.farbeDef = curve.data(TreeModel.ColorRole)
                line.colorChanged.connect(self.updateColor)


                vertical.addWidget(line)
                vertical.addSpacing(10)
                vertical.addWidget(QLabel(
                    curve.parent().data(TreeModel.IdentificationRole) +
                    " " + QApplication.translate("VariantInfoWidget", "and") + " " +
                    curve.data(TreeModel.IdentificationRole)))
                layout.addLayout(vertical)
                result = QHBoxLayout()
                result.setContentsMargins(0, 0, 0, 0)
                result.addSpacing(35)

                # check, if the plant count is smaller than the calculation
                point = curve.data(TreeModel.ResultRole) * self.model.projectData("length")

                resultText = QApplication.translate("VariantInfoWidget", "The costs are equal")
                if self.model.projectData("count") < point:
                    resultText = QApplication.translate("VariantInfoWidget", "Tree shelter is profitable")
                elif self.model.projectData("count") > point:
                    resultText = QApplication.translate("VariantInfoWidget", "Fence is profitable")

                result.addWidget(QLabel("<i>" + resultText + "</i>"))
                layout.addLayout(result)

            # show the color hint
            layout.addSpacing(10)
            layout.addWidget(QLabel("(" + QApplication.translate("VariantInfoWidget", "to change the color click on the symbol") + ")", wordWrap=True))

            layout.addSpacing(10)
            helpSymbol = QLabel(pixmap=QPixmap(os.path.join(self._OXYGEN_PATH_22, "system-help.png")))
            helpText = ClickableLabel("<a href='#'>" + QApplication.translate("VariantInfoWidget", "Explanation of calculation") + "</a>")
            helpText.clicked.connect(self.showHelp)
            helpLayout = QHBoxLayout()
            helpLayout.setContentsMargins(0, 0, 0, 0)
            helpLayout.setSpacing(8)
            helpLayout.addWidget(helpSymbol, alignment=Qt.AlignVCenter)
            helpLayout.addWidget(helpText, alignment=Qt.AlignVCenter)
            helpLayout.addStretch()
            layout.addLayout(helpLayout)

            # add hints
            separator = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.HLine)

            # not the best solution but it works
            # this is very tricky!
            hintTitle = QLabel("<b>" + QApplication.translate("VariantInfoWidget", "Relevant information:") + "</b>")
            hintArrow = QLabel("<ul style='list-style-type: square; margin-left: -25px;'>" +
                    "<li>" + QApplication.translate("VariantInfoWidget", "the orange arrow displays the result of the calculation") + "</li></ul>", wordWrap=True)                # orangener Pfeil zeigt das Ergebnis der Kalkulation
            hintLines = QLabel("<ul style='list-style-type: square; margin-left: -25px;'>" +
                    "<li>" + QApplication.translate("VariantInfoWidget", "the auxiliary lines for fence length and number of plants are movable") + "</li></ul>", wordWrap=True)             # Hilfslinien für Zaunlänge und Pflanzenzahl sind beweglich

            layout.addSpacing(30)
            layout.addWidget(separator)
            layout.addWidget(hintTitle)
            layout.addSpacing(10)
            layout.addWidget(hintArrow)
            layout.addSpacing(6)
            layout.addWidget(hintLines)
            layout.addStretch()
        else:
            # no curve was plotted
            # there is no result available
            layout.addSpacing(10)
            layout.addWidget(QLabel(QApplication.translate("VariantInfoWidget", "No results available!")))
            layout.addStretch()

        new.setLayout(layout)

        self.layout.replaceWidget(self.results, new)
        self.results.deleteLater()
        self.results = new

    def showHelp(self):
        # create the documentation path with
        # the current locale settings
        docFile = os.path.join("doc", "documentation_" +
                self.locale().name()[:2] + ".pdf")

        # on every platfrom a different
        # start operation is needed
        if sys.platform == "win32":
            os.startfile(docFile)
        elif sys.platform == "darwin":
            subprocess.call(("open", docFile))
        elif sys.platform.startswith("linux"):
            subprocess.call(("xdg-open", docFile))


class ClickableLabel(QLabel):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class VariantPlotWidget(QWidget):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    AREA = 0
    LINE = 1

    curvePlotted = pyqtSignal(QModelIndex)
    plotReady = pyqtSignal()
    cleared = pyqtSignal()

    def __init__(self):
        super().__init__()

        # the plot widget is always
        # disabled at the first start
        self.setDisabled(True)

        ### TESTING ###
        self.model = None
        self.selectionModel = None
        self.view = 0
        self.calc = False

        self.plotLength = 0
        self.plotCount = 0

        self.fenceLine = None
        self.plantLine = None
        self.arrowItem = None

        #self.lengthCoefficient = 1.5    # in model festlegen!
        #self.transparency = 0.3

        ### TESTING ###

        self.controlWidget = PlotControlWidget()
        self.plotWidget = NaturalPlotView()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.controlWidget)
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)

        # connect signals
        self.controlWidget.chartViewChanged.connect(self.updateChartView)
        self.controlWidget.arrowEnabled.connect(self.setArrowItemVisible)
        self.controlWidget.countEnabled.connect(self.setPlantLineVisible)
        self.controlWidget.lengthEnabled.connect(self.setFenceLineVisible)

    def retranslateUi(self):
        # update the control widget
        self.controlWidget.retranslateUi()

        # translate the plot widget
        self.plotWidget.retranslateUi()

    def setModel(self, model):
        self.model = model
        self.model.dataChanged.connect(self.update)
        self.model.modelReset.connect(self.update)

        # das muss optimiert werden, weil dies private Signale sind
        # es dient dazu, dass gelöschte, oder veränderte (verschobene) Zeilen
        # nicht mehr ausgewählt werden können (selectionModel)
        self.model.rowsRemoved.connect(self.modelRemoveAction)
        self.model.rowsMoved.connect(self.modelRemoveAction)

        self.model.calculated.connect(self.calculate)

    def calculate(self):
        self.calc = True
        self.paintCalculation()

    def updateChartView(self, index):
        self.view = index

        # update calculation
        # möglicherweise sollte hier paintEvent() verwendet werden?!
        #
        # vorher muss hier noch eine Berechnung stattfinden
        if self.calc:
            self.paintCalculation()

    def setSelectionModel(self, selectionModel):
        # setup view's selectionModel
        self.selectionModel = selectionModel

    def modelRemoveAction(self):
        # TODO
        # wird benötigt, da sonst Fehler, wenn mit Enter bestätigt in Zaunlänge
        self.setDisabled(True)
        self.clear()

    def clear(self):
        # disconnect signals
        if isinstance(self.plantLine, InfiniteLine):
            self.plantLine.disconnect()
            self.plantLine = None

        if isinstance(self.fenceLine, InfiniteLine):
            self.fenceLine.disconnect()
            self.fenceLine = None

        if isinstance(self.arrowItem, MovableArrowItem):
            self.arrowItem.disconnect()
            self.arrowItem = None

        self.plotWidget.clear()
        self.cleared.emit()

    def paintCalculation(self):
        if not self.calc:
            return

        # search for enabeld items
        # items contains at least one parent and one child
        # remove parents from children
        items = self.model.match(self.model.index(0, 0),
                TreeModel.StatusRole, True, -1, Qt.MatchRecursive)
        children = [item for item in items if item.parent().isValid()]

        if self.view == self.AREA:
            self.plotAreaChart(children)
        elif self.view == self.LINE:
            self.plotLineChart(children)

    def createIntersectionPoint(self):
        # TODO
        self.plotLength = self.model.projectData("length") * LENGTH_COEFFICIENT

        # create the horizontal plant line
        green = QColor(0, 144, 54)
        plantPen = pyqtgraph.mkPen(width=2, color=green)   # Hochschule für Forstwirtschaft Rottenburg
        self.plantLine = InfiniteLine(self.model.projectData("count"), 0, plantPen, True)
        self.plantLine.sigPositionChanged.connect(self.updateCount)
        self.controlWidget.setCount(self.model.projectData("count"))
        self.controlWidget.countChanged.connect(self.plantLine.setValue)

        self.plantLabel = TextItem(html="<b><font color='" + green.name() +
                "'>Pflanzenzahl</font></b>", anchor=(-0.15, 0.9))
        self.plantLabel.setParentItem(self.plantLine)

        self.plotWidget.addPlotItem(self.plantLine)

        # create the vertical fence line
        red = QColor(255, 0, 0)
        fencePen = pyqtgraph.mkPen(width=2, color=red)
        self.fenceLine = InfiniteLine(self.model.projectData("length"), 90, fencePen, True)
        self.fenceLine.sigPositionChanged.connect(self.updateLength)
        self.fenceLine.sigPositionChangeFinished.connect(self.updatePlotLength)
        self.controlWidget.setLength(self.model.projectData("length"))
        self.controlWidget.lengthChanged.connect(self.fenceLine.setValue)

        self.fenceLabel = TextItem(html="<b><font color='" + red.name() +
                "'>Zaunlänge</font></b>", anchor=(-2.5, 0.9), angle=-90)
        self.fenceLabel.setParentItem(self.fenceLine)

        self.plotWidget.addPlotItem(self.fenceLine)

        # create an arrow item as point of intersection
        self.arrowItem = MovableArrowItem(movable=True, angle=-45, tipAngle=30, baseAngle=20,
                headLen=20, tailLen=None,
                pen={"color" : "#333", "width" : 2}, brush=QColor(255, 123, 0))
        self.arrowItem.sigPositionChangeFinished.connect(self.updateArrow)
        self.arrowItem.setPos((self.model.projectData("length"), self.model.projectData("count")))

        self.controlWidget.setArrow()
        self.plotWidget.addPlotItem(self.arrowItem)

    def plotAreaChart(self, children):
        # check parents and children
        # the lists must contain only one item
        if len(children) == 0:
            print("Fehler")
            return False

        # clear the plot widget
        self.clear()

        # first sort all slopes to plot the area chart
        # then plot the curves
        children.sort(key=lambda c: c.data(TreeModel.ResultRole), reverse=True) # is this a good way or is better to sort the model?
        for child in children:
            curve = EnhancedCurveItem(child, True)
            self.plotWidget.addPlotItem(curve)
            self.curvePlotted.emit(child)

        # create point of intersection
        self.createIntersectionPoint()

        # add the description to the view
        self.setEnabled(True)
        self.plotWidget.showDescription()
        self.plotReady.emit()

    def plotLineChart(self, children):
        # check parents and children
        # the lists must contain only one item
        if len(children) == 0:
            print("Fehler")
            return False

        # clear the plot widget
        self.clear()

        for child in children:
            # plot the curve
            curve = EnhancedCurveItem(child)
            self.plotWidget.addPlotItem(curve)
            self.curvePlotted.emit(child)

        # create point of intersection
        self.createIntersectionPoint()

        # add the description to the view
        self.setEnabled(True)
        self.plotWidget.showDescription()
        self.plotReady.emit()

    def updatePlotLength(self):
        length = self.fenceLine.value()
        hint = False

        # update the chart, if necessary
        if length >= self.plotLength:
            self.paintCalculation()
            hint = True
        elif length < self.plotLength / 5:
            self.paintCalculation()
            hint = True

        if hint:
            # notice the user about the update
            notice = QMessageBox(self)
            notice.setWindowModality(Qt.WindowModal)  # check for mac only
            notice.setIcon(QMessageBox.Information)
            notice.setStandardButtons(QMessageBox.Ok)
            notice.setWindowTitle(QApplication.translate("VariantPlotWidget", "Wuchshüllenrechner"))
            notice.setText("<b>" + QApplication.translate("VariantPlotWidget",
                    "Die Skalierung wurde verändert!") + "</b>")
            notice.setInformativeText(QApplication.translate("VariantPlotWidget",
                    "Da sich die Zaunlänge geändert hat, wurde die Skalierung "
                    "des Diagramms ebenfalls verändert."))

            notice.exec()

    def updateArrow(self, arrow):
        """
        TODO
        Hier ist es eventuell hilfreich einige Funktionen zu vereinfachen und zusammenzufassen,
        weil es sehr ähnliche Elemente gibt. Außerdem wäre es vielleicht sinnvoll die setProjectData und setLength
        zusammenzufassen und mit einem Signal zu verbinden. Ein eleganter Weg sollte gesucht werden.
        """
        # get fence length and plant count from arrow's postion
        (length, count) = map(int, arrow.pos())

        # update the model to save the new postion
        self.model.setProjectData("length", length)
        self.controlWidget.setLength(length)
        self.model.setProjectData("count", count)
        self.controlWidget.setCount(count)

        # update the legend
        self.plotReady.emit()

    def updateCount(self, line):
        # save the new value in the model and
        # update the control widget
        count = int(self.plantLine.value())
        self.model.setProjectData("count", count)
        self.controlWidget.setCount(count)

        # change the arrow item
        self.arrowItem.setPos((self.model.projectData("length"), self.model.projectData("count")))

        # update the legend
        self.plotReady.emit()

    def updateLength(self, line):
        # save the new value in the model and
        # update the control widget
        length = int(self.fenceLine.value())
        self.model.setProjectData("length", length)
        self.controlWidget.setLength(length)

        # change the arrow item
        self.arrowItem.setPos((self.model.projectData("length"), self.model.projectData("count")))

        # update the legend
        self.plotReady.emit()

    def setPlantLineVisible(self, state):
        # check, if plant line is not None to avoid errors
        if not self.plantLine:
            return False

        self.plantLine.setVisible(state)

    def setFenceLineVisible(self, state):
        # check, if fence line is not None to avoid errors
        if not self.fenceLine:
            return False

        self.fenceLine.setVisible(state)

    # improvement for new version 2.0
    # mail from Sebastian Hein at 2020-03-30
    def setArrowItemVisible(self, state):
        # check, if arrow item is not None to avoid errors
        if not self.arrowItem:
            return False

        self.arrowItem.setVisible(state)


class EnhancedCurveItem(PlotCurveItem):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self, index, filled=False):
        super().__init__()
        self.index = index
        self.internalId = str(index.internalId())
        self.parent = index.parent()

        # calculate
        length = self.index.data(TreeModel.LengthRole)
        slope = self.index.data(TreeModel.ResultRole)
        self.x = numpy.arange(length * LENGTH_COEFFICIENT)
        self.y = slope * self.x

        # update item's data
        color = self.index.data(TreeModel.ColorRole)
        self.setData(self.x, self.y, pen=pyqtgraph.mkPen(width=3, color=color), antialias=True)
        if filled:
            self.setFillLevel(0.0)
            self.setBrush(QColor.fromRgbF(color.redF(),
                                      color.greenF(),
                                      color.blueF(),
                                      COLOR_TRANSPARENCY))


class NaturalPlotView(GraphicsView):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self):
        super().__init__()

        # settings
        self.setBackground("#fff")
        self.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.setAntialiasing(True)

        # create custom view box
        view_box = ViewBox()
        view_box.setMouseEnabled(False, False)
        view_box.setLimits(xMin=0, yMin=0, minXRange=10, minYRange=100)
        view_box.setRange(xRange=(0, 400), yRange=(0, 5000))
        view_box.enableAutoRange()

        # create natural axis items
        self.x_axis = NaturalAxis("bottom")
        self.x_axis.setLabel(QApplication.translate("NaturalPlotView", "Fence length"), "m")
        self.y_axis = NaturalAxis("left")
        self.y_axis.setLabel(QApplication.translate("NaturalPlotView", "Number of plants"))

        # create fence information text
        self.fenceItem = TextItem(border=pyqtgraph.mkPen(width=2, color="#555"),
                fill=pyqtgraph.mkBrush((255, 255, 255, 200)))

        # create tube information text
        self.tubeItem = TextItem(border=pyqtgraph.mkPen(width=2, color="#555"),
                fill=pyqtgraph.mkBrush((255, 255, 255, 200)),
                anchor=(1,1))

        # create plot item with custom view box and natural axis items
        self.plotItem = PlotItem(viewBox=view_box,
                axisItems={"bottom" : self.x_axis, "left" : self.y_axis}, enableMenu=False)
        self.plotItem.setContentsMargins(5, 5, 12, 5)
        self.plotItem.hideButtons()
        self.plotItem.hide()
        self.setCentralWidget(self.plotItem)

        # connect actions
        view_box.sigResized.connect(self.updateTubeLegendPosition)

        # translate the plot item
        self.retranslateUi()

    def retranslateUi(self):
        # title label
        titleStyle = "color: #111; font-size: 15px; font-weight: bold"
        titleLabel = "<span style='{style}'>{title}</span>".format(style=titleStyle,
                title="Ergebnis: Funktion(en) der Kostengleichheit")
        self.plotItem.setTitle(titleLabel)

        # axis items
        #self.x_axis.setLabel(QApplication.translate("NaturalPlotView", "Fence length"), "m")
        #self.y_axis.setLabel(QApplication.translate("NaturalPlotView", "Number of plants"))

        # fence hint
        self.fenceItem.setHtml("<p style='margin: 0; color: #555'><b>" +
                QApplication.translate("NaturalPlotView", "Pfeil über Funktion(en):") + "</b> " +
                QApplication.translate("NaturalPlotView", "Zaun günstiger") + "</p>")

        # tube hint
        self.tubeItem.setHtml("<p style='margin: 0; color: #555'><b>" +
                QApplication.translate("NaturalPlotView", "Pfeil unter Funktion(en):") + "</b> " +
                QApplication.translate("NaturalPlotView", "Wuchshülle günstiger") + "</p>")


    def addPlotItem(self, item, *args, **kwargs):
        # first show the plot item
        if not self.plotItem.isVisible():
            self.plotItem.show()

        self.plotItem.addItem(item, *args, **kwargs)

    def removePlotItem(self, item):
        self.plotItem.removeItem(item)

    #TODO:
    def clear(self):
        self.plotItem.hide()
        self.plotItem.clear()

    def showDescription(self):
        viewBox = self.plotItem.getViewBox()

        self.fenceItem.setPos(15, 10)
        self.fenceItem.setParentItem(viewBox)

        rect = viewBox.screenGeometry()
        self.tubeItem.setPos(rect.width() - 15, rect.height() - 10)
        self.tubeItem.setParentItem(viewBox)

    def updateTubeLegendPosition(self):
        rect = self.plotItem.getViewBox().screenGeometry()
        self.tubeItem.setPos(rect.width() - 15, rect.height() - 10)

    def export(self, gfxfile):
        exporter = TestImageExporter(self.plotItem)
        exporter.parameters()["width"] = 2007.0   # 17 cm / 300 DPI

        # export the graphics to the selected file
        exporter.export(gfxfile)


class TestImageExporter(ImageExporter):
    def __init__(self, p):
        super().__init__(p)

    def export(self, fileName=None, toBytes=False, copy=False):

        targetRect = pyqtgraph.QtCore.QRect(0, 0, int(self.params['width']), int(self.params['height']))
        sourceRect = self.getSourceRect()


        #self.png = QtGui.QImage(targetRect.size(), QtGui.QImage.Format_ARGB32)
        #self.png.fill(pyqtgraph.mkColor(self.params['background']))
        w, h = self.params['width'], self.params['height']
        if w == 0 or h == 0:
            raise Exception("Cannot export image with size=0 (requested export size is %dx%d)" % (w,h))
        bg = np.empty((int(self.params['width']), int(self.params['height']), 4), dtype=np.ubyte)
        color = self.params['background']
        bg[:,:,0] = color.blue()
        bg[:,:,1] = color.green()
        bg[:,:,2] = color.red()
        bg[:,:,3] = color.alpha()
        self.png = pyqtgraph.functions.makeQImage(bg, alpha=True)

        ## set resolution of image:
        origTargetRect = self.getTargetRect()
        resolutionScale = targetRect.width() / origTargetRect.width()
        #self.png.setDotsPerMeterX(self.png.dotsPerMeterX() * resolutionScale)
        #self.png.setDotsPerMeterY(self.png.dotsPerMeterY() * resolutionScale)

        painter = pyqtgraph.QtGui.QPainter(self.png)
        #dtr = painter.deviceTransform()
        try:
            self.setExportMode(True, {'antialias': self.params['antialias'], 'background': self.params['background'], 'painter': painter, 'resolutionScale': resolutionScale})
            painter.setRenderHint(pyqtgraph.QtGui.QPainter.Antialiasing, self.params['antialias'])
            self.getScene().render(painter, pyqtgraph.QtCore.QRectF(targetRect), pyqtgraph.QtCore.QRectF(sourceRect))
        finally:
            self.setExportMode(False)
        painter.end()

        self.png.save(fileName)


class PlotControlWidget(QWidget):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    # signals
    chartViewChanged = pyqtSignal(int)
    lengthEnabled = pyqtSignal(bool)
    countEnabled = pyqtSignal(bool)
    arrowEnabled = pyqtSignal(bool)
    lengthChanged = pyqtSignal(int)
    countChanged = pyqtSignal(int)
    lengthFinished = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._COMBOBOX_ITEM_LIST = (QtCore.QT_TRANSLATE_NOOP("PlotControlWidget", "Area chart"),
                                    QtCore.QT_TRANSLATE_NOOP("PlotControlWidget", "Line chart"))

        # create labels and input fields
        self.viewLabel = QLabel()
        self.viewInput = QComboBox(self)

        # enable arrow item
        # improvement for new version 2.0
        # mail from Sebastian Hein at 2020-03-30
        self.arrowCheckBox = QCheckBox()
        self.arrowCheckBox.setCheckState(Qt.Checked)
        self.arrowCheckBox.setDisabled(True)

        self.lengthCheckBox = QCheckBox()
        self.lengthCheckBox.setCheckState(Qt.Checked)
        self.lengthCheckBox.setDisabled(True)
        self.lengthInput = QSpinBox(self, maximum=99999)
        self.lengthInput.setSuffix(" Lfm.")
        self.lengthInput.setDisabled(True)

        self.countCheckBox = QCheckBox()
        self.countCheckBox.setCheckState(Qt.Checked)
        self.countCheckBox.setDisabled(True)
        self.countInput = QSpinBox(self, maximum=99999)
        self.countInput.setSuffix(" St.")
        self.countInput.setDisabled(True)
        self.countCalculator = QPushButton()
        self.countCalculator.setDisabled(True)

        lineFrame = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.VLine)

        # create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.viewLabel)
        layout.addWidget(self.viewInput)
        layout.addStretch()
        layout.addWidget(self.arrowCheckBox)
        layout.addWidget(self.lengthCheckBox)
        layout.addWidget(self.lengthInput)
        layout.addWidget(lineFrame)
        layout.addWidget(self.countCheckBox)
        layout.addWidget(self.countInput)
        layout.addWidget(self.countCalculator)

        # connect signals
        self.viewInput.currentIndexChanged.connect(self.chartViewChanged)
        self.arrowCheckBox.stateChanged.connect(self.enableArrowItem)
        self.lengthCheckBox.stateChanged.connect(self.enableLengthInput)
        self.countCheckBox.stateChanged.connect(self.enableCountInput)
        self.lengthInput.valueChanged.connect(self.lengthChanged)
        self.lengthInput.editingFinished.connect(self.lengthFinished)
        self.countInput.valueChanged.connect(self.countChanged)

        self.countCalculator.clicked.connect(self.countCalculation)

        # translate the graphical user interface
        self.retranslateUi()

    def countCalculation(self):
        dialog = PlantCountDialog()
        if dialog.exec() == QDialog.Accepted:
            self.countInput.setValue(dialog.value)

    def enableArrowItem(self, state):
        if state == Qt.Checked:
            self.arrowEnabled.emit(True)
        else:
            self.arrowEnabled.emit(False)

    def enableLengthInput(self, state):
        if state == Qt.Checked:
            self.lengthInput.setEnabled(True)
            self.lengthEnabled.emit(True)
        else:
            self.lengthInput.setDisabled(True)
            self.lengthEnabled.emit(False)

    def enableCountInput(self, state):
        if state == Qt.Checked:
            self.countInput.setEnabled(True)
            self.countCalculator.setEnabled(True)
            self.countEnabled.emit(True)
        else:
            self.countInput.setDisabled(True)
            self.countCalculator.setDisabled(True)
            self.countEnabled.emit(False)

    def setArrow(self):
        self.arrowCheckBox.setEnabled(True)

    def setLength(self, length):
        self.lengthCheckBox.setEnabled(True)
        self.lengthInput.setEnabled(True)
        self.lengthInput.setValue(length)

    def setCount(self, count):
        self.countCheckBox.setEnabled(True)
        self.countInput.setEnabled(True)
        self.countCalculator.setEnabled(True)
        self.countInput.setValue(count)

    def reset(self):
        # reset the view input field
        self.viewInput.disconnect()
        self.viewInput.setCurrentIndex(0)
        #self.viewInput.setDisabled(True)

        # reset length input field
        self.lengthCheckBox.setCheckState(Qt.Checked)
        #self.lengthCheckBox.setDisabled(True)
        self.lengthInput.setValue(0)
        #self.lengthInput.setDisabled(True)

        # reset count check box and count input field
        self.countCheckBox.setCheckState(Qt.Checked)
        #self.countCheckBox.setDisabled(True)
        self.countInput.setValue(0)
        #self.countInput.setDisabled(True)
        #self.countCalculator.setDisabled(True)

    def retranslateUi(self):
        # input fields
        self.viewLabel.setText(QApplication.translate("PlotControlWidget", "Chart view") + ":")                 # Diagrammansicht
        self.viewInput.clear()
        for item in self._COMBOBOX_ITEM_LIST:
            self.viewInput.addItem(QApplication.translate("PlotControlWidget", item))

        self.arrowCheckBox.setText(QApplication.translate("PlotControlWidget", "Ergebnispfeil"))
        self.lengthCheckBox.setText(QApplication.translate("PlotControlWidget", "Fence length") + ":")          # Zaunlänge
        self.countCheckBox.setText(QApplication.translate("PlotControlWidget", "Number of plants") + ":")       # Anzahl der Pflanzen
        self.countCalculator.setText(QApplication.translate("PlotControlWidget", "Calculation help"))           # Umrechnungshilfe


class NaturalAxis(AxisItem):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enableAutoSIPrefix(False)
        self.setPen(width=2, color="#111")

    def setLabel(self, text=None, units=None, unitPrefix=None):
        label_style = {"color" : "#111",
                       "font-weight" : "bold"}

        super().setLabel(text, units, unitPrefix, **label_style)

    def labelString(self):
        if self.labelUnits == "":
            if not self.autoSIPrefix or self.autoSIPrefixScale == 1.0:
                units = ""
            else:
                units = asUnicode("[x%g]") % (1.0/self.autoSIPrefixScale)
        else:
            units = asUnicode("[%s%s]") % (asUnicode(self.labelUnitPrefix), asUnicode(self.labelUnits))

        s_label = asUnicode("%s %s") % (asUnicode(self.labelText), asUnicode(units))
        s_style = ";".join(["%s: %s" % (k, self.labelStyle[k]) for k in self.labelStyle])

        return asUnicode("<span style='%s'>%s</span>") % (s_style, asUnicode(s_label))


class PlantSpacingWidget(QWidget):

    calculated = pyqtSignal()

    def __init__(self):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()

        self.value = 0

        # create the input fields
        self.x = QDoubleSpinBox(decimals=1, maximum=99, singleStep=0.1, suffix=" m")
        self.y = QDoubleSpinBox(decimals=1, maximum=99, singleStep=0.1, suffix=" m")
        label = QLabel("x")

        # dialog main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.x)
        layout.addWidget(label)
        layout.addWidget(self.y)

        # connect actions
        self.x.valueChanged.connect(self.calculate)
        self.y.valueChanged.connect(self.calculate)

    def calculate(self):
        try:
            self.value = 10000 / (self.x.value() * self.y.value())
        except ZeroDivisionError:
            self.value = 0

        self.calculated.emit()


class PlantCountDialog(QDialog):
    def __init__(self):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__()

        self.value = 0

        self._LABEL_MIN_WIDTH = 75

        # input group box
        inputGroup = QGroupBox(QApplication.translate("PlantCountDialog", "User input"))     # Benutzereingaben
        inputGroup.setFlat(True)

        self.areaInput = QDoubleSpinBox(decimals=1, maximum=99999, singleStep=0.1, suffix=" ha", value=1.0)
        areaLabel = QLabel(QApplication.translate("PlantCountDialog", "Area") + ":")             # Fläche
        areaLabel.setMinimumWidth(self._LABEL_MIN_WIDTH)
        areaLabel.setBuddy(self.areaInput)

        self.spacingInput = PlantSpacingWidget()
        spacingLabel = QLabel(QApplication.translate("PlantCountDialog", "Spacing") + ":")       # Pflanzverband
        spacingLabel.setBuddy(self.spacingInput)

        # create input group box layout
        inputLayout = QGridLayout(inputGroup)
        inputLayout.addWidget(areaLabel, 0, 0)
        inputLayout.addWidget(self.areaInput, 0, 1)
        inputLayout.addWidget(spacingLabel, 1, 0)
        inputLayout.addWidget(self.spacingInput, 1, 1)

        # result group box
        resultGroup = QGroupBox(QApplication.translate("PlantCountDialog", "Calculation results"))     # Berechnungsergebnisse
        resultGroup.setFlat(True)

        self.countResult = QLabel("0")
        countLabel = QLabel(QApplication.translate("PlantCountDialog", "Plants/ha") + ":")       # Pflanzen/ha
        countLabel.setFixedWidth(self._LABEL_MIN_WIDTH)
        countLabel.setBuddy(self.countResult)

        self.totalResult = QLabel("0")
        totalLabel = QLabel(QApplication.translate("PlantCountDialog", "Total") + ":")          # Gesamt
        totalLabel.setFixedWidth(self._LABEL_MIN_WIDTH)
        totalLabel.setBuddy(self.totalResult)

        # create input group box layout
        resultLayout = QGridLayout(resultGroup)
        resultLayout.addWidget(countLabel, 0, 0)
        resultLayout.addWidget(self.countResult, 0, 1)
        resultLayout.addWidget(totalLabel, 1, 0)
        resultLayout.addWidget(self.totalResult, 1, 1)

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

        self.areaInput.valueChanged.connect(self.calculate)
        self.spacingInput.calculated.connect(self.calculate)

    def calculate(self):
        # first calculate the value
        self.value = self.areaInput.value() * self.spacingInput.value

        # update results
        self.countResult.setText("{:.0f}".format(self.spacingInput.value))
        self.totalResult.setText("{:.0f}".format(self.value))


class ColorLine(QFrame):
    """Acquires a new plant protection variant for the cost calculation.

    The dialog contains two input fields to acquire a new plant protection variant.
    First there is a input field for the name of the new variant. The second
    input field asks about the used plant protection. The user cannot change
    the variant type at a later time.
    This class has no attributes or return values.

    """

    colorChanged = pyqtSignal(QModelIndex, QColor)

    def __init__(self, index):
        """The constructor initializes the class NewVariantDialog."""
        super().__init__(frameShadow=QFrame.Plain, frameShape=QFrame.HLine, lineWidth=3)

        self._farbe = QColor()
        self.index = index

        self.setFixedSize(25, 18)
        self.setContentsMargins(0, 0, 0, 0)

        self.palette = self.palette()
        self.palette.setColor(QPalette.Foreground, self._farbe)
        self.setPalette(self.palette)

    def mousePressEvent(self, event):
        self._farbe = QColorDialog().getColor()
        self.palette.setColor(QPalette.Foreground, self._farbe)
        self.setPalette(self.palette)

        self.colorChanged.emit(self.index, self._farbe)

    @pyqtProperty(str)
    def farbeDef(self):
        return self._farbe.name()

    @farbeDef.setter
    def farbeDef(self, value):
        self._farbe = QColor(value)

        self.palette.setColor(QPalette.Foreground, self._farbe)
        self.setPalette(self.palette)


class MovableArrowItem(GraphicsObject):
    """

    Soweit funktioniert diese Klasse. Jedoch muss die Funktion zur Berechnung des BoundingRect verbessert werden.
    Diese ist hardcoded und muss von der größe des Pfeils abhängen.

    Die Hover-Funktion kann verbessert werden, indem der Pfeil bei Hover aktiv dargestellt wird. Das sollte
    bei den Linien ähnlich sei. Darüber hinaus können einige Funktionen gestrichen werden.

    Als weiteren Punkt muss die Paint-Funktion einen Rahmen zeichen, damit ich nachvollziehen kann,
    wo der aktive Bereich des Pfeils ist.

    """

    sigDragged = QtCore.Signal(object)
    sigPositionChanged = QtCore.Signal(object)
    sigPositionChangeFinished = QtCore.Signal(object)

    def __init__(self, movable=True, name=None, **opts):
        """The constructor initializes the class MovableArrowItem."""
        super().__init__()

        self.arrow = ArrowItem(**opts)
        self.arrow.setParentItem(self)

        self._boundingRect = None

        self._name = name

        # movable
        self.moving = False
        self.setMovable(movable)
        self.mouseHovering = False
        self.p = [0, 0]

        #if pos is None:
        pos = QtCore.QPointF(0, 0)
        self.setPos(pos)

        # cache variables for managing bounds
        self._endPoints = [0, 1]
        self._bounds = None
        self._lastViewSize = None

    def setMovable(self, m):
        """Set whether the line is movable by the user."""
        self.movable = m
        self.setAcceptHoverEvents(m)

    def setStyle(self, **opts):
        return self.arrow.setStyle(**opts)

    def setPos(self, pos):
        if type(pos) in [list, tuple]:
            newPos = pos
        elif isinstance(pos, QtCore.QPointF):
            newPos = [pos.x(), pos.y()]
        else:
            raise Exception("Must specify 2D coordiante for non-orthogonal lines.")

        if self.p != newPos:
            self.p = newPos
            self._invalidateCache()
            super().setPos(Point(self.p))

            self.sigPositionChanged.emit(self)

    def getXPos(self):
        return self.p[0]

    def getYPos(self):
        return self.p[1]

    def getPos(self):
        return self.p

    def _invalidateCache(self):
        self._boundingRect = None

    def hoverEvent(self, ev):
        if (not ev.isExit()) and self.movable and ev.acceptDrags(QtCore.Qt.LeftButton):
            self.setMouseHover(True)
        else:
            self.setMouseHover(False)

    def setMouseHover(self, hover):
        if self.mouseHovering == hover:
            return

        self.mouseHovering = hover
        self.update()

    def mouseDragEvent(self, ev):
        if self.movable and ev.button() == QtCore.Qt.LeftButton:
            if ev.isStart():
                self.moving = True
                self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                self.startPosition = self.pos()
            ev.accept()

            if not self.moving:
                return

            self.setPos(self.cursorOffset + self.mapToParent(ev.pos()))
            self.sigDragged.emit(self)
            if ev.isFinish():
                self.moving = False
                self.sigPositionChangeFinished.emit(self)

    def mouseClickEvent(self, ev):
        if self.moving and ev.button() == QtCore.Qt.RightButton:
            ev.accept()
            self.setPos(self.startPosition)
            self.moving = False
            self.sigDragged.emit(self)
            self.sigPositionChangeFinished.emit(self)

    def _computeBoundingRect(self):
        br = self.arrow.boundingRect()

        vr = self.viewRect()
        if vr is None:
            return QtCore.QRectF()

        # add a 4-pixel radius around the line for mouse interaction
        px = self.pixelLength(direction=Point(1,0))
        if px is None:
            px = 0

        """w = 4
        w = w * px
        br = QtCore.QRectF(vr)
        br.setBottom(-w)
        br.setTop(w)

        length = br.width()
        left = br.left() + 200
        right = br.left() + 200
        br.setLeft(left - w)
        br.setRight(right + w)
        br = br.normalized()"""

        br.setWidth(200)
        br.setHeight(200)
        br = br.normalized() # needed?

        if self._bounds != br:
            self._bounds = br
            self.prepareGeometryChange()

        return self._bounds

    def boundingRect(self):
        if self._boundingRect is None:
            self._boundingRect = self._computeBoundingRect()

        return self._boundingRect

    def paint(self, p, *args):
        pass

    def viewTransformChanged(self):
        """
        Called whenever the transformation matrix of the view has changed.
        (eg, the view range has changed or the view was resized)
        """
        self._invalidateCache()

    def setName(self, name):
        self._name = name

    def name(self):
        return self._name
