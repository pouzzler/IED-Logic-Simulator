#!/usr/bin/env python3
# coding=utf-8

import inspect
from PySide.QtGui import (
    QCheckBox, QComboBox, QDockWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QWidget)
from .graphicitem import CircuitItem, WireItem
from .util import boolToCheckState
from engine.gates import *


class SelectionOptions(QWidget):
    """Widget for modifying the selected circuit or gate."""

    def __init__(self, view):
        super(SelectionOptions, self).__init__()

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.view = view
        self.view.scene().selectionChanged.connect(self.updateOptions)
        self.gridLayout = QGridLayout(self)

        self.nameLabel = QLabel(self.str_name, self)
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)

        self.nameLE = QLineEdit(self)
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 2)
        self.nameLE.returnPressed.connect(self.setItemName)

        self.showNameLabel = QLabel(self.str_showName, self)
        self.gridLayout.addWidget(self.showNameLabel, 1, 0, 1, 1)

        self.showNameCB = QCheckBox(self)
        self.gridLayout.addWidget(self.showNameCB, 1, 1, 1, 1)
        self.showNameCB.stateChanged.connect(self.setNameVisibility)

        self.showCategoryLabel = QLabel(self.str_showCategory, self)
        self.gridLayout.addWidget(self.showCategoryLabel, 2, 0, 1, 1)

        self.showCategoryCB = QCheckBox(self)
        self.gridLayout.addWidget(self.showCategoryCB, 2, 1, 1, 1)
        self.showCategoryCB.stateChanged.connect(self.setCategoryVisibility)

        self.nbInputsLabel = QLabel(self.str_nbInputs, self)
        self.gridLayout.addWidget(self.nbInputsLabel, 3, 0, 1, 1)

        self.nbInputsCB = QComboBox(self)
        self.nbInputsCB.activated.connect(self.setNbInputs)
        self.nbInputsCB.addItems([str(x) for x in range(2, 33)])
        self.gridLayout.addWidget(self.nbInputsCB, 3, 1, 1, 2)

        orientLabel = QLabel(self.str_orientation, self)
        self.gridLayout.addWidget(orientLabel, 4, 0, 1, 1)

        self.cwRotationButton = QPushButton(self)
        self.cwRotationButton.setText("↻")
        self.gridLayout.addWidget(self.cwRotationButton, 4, 1, 1, 1)

        self.acwRotationButton = QPushButton(self)
        self.acwRotationButton.setText("↺")
        self.gridLayout.addWidget(self.acwRotationButton, 4, 2, 1, 1)

        valueLabel = QLabel('Value:', self)
        self.gridLayout.addWidget(valueLabel, 5, 0, 1, 1)

        self.lowRadioButton = QRadioButton(self)
        self.lowRadioButton.setText('Low')
        self.gridLayout.addWidget(self.lowRadioButton, 5, 1, 1, 1)

        self.highRadioButton = QRadioButton(self)
        self.highRadioButton.setText('High')
        self.gridLayout.addWidget(self.highRadioButton, 5, 2, 1, 1)

        self.updateOptions()

    def updateOptions(self):
        """Hides irrelevant options, and sets reasonable values for the
        visible options.
        """
        selection = self.view.scene().selectedItems()
        size = len(selection)
        if size == 0:
            for widget in self.findChildren(QWidget):
                widget.setHidden(True)
        elif size >= 1:
            for widget in self.findChildren(QWidget):
                widget.setHidden(False)
                notAllGates = True
                for item in selection:
                    if (
                        not isinstance(item, CircuitItem)
                        or item.item.__class__ not in [
                            AndGate, NandGate, OrGate,
                            NorGate, XorGate, XnorGate]):
                        break
                    notAllGates = False
                self.nbInputsLabel.setHidden(notAllGates)
                self.nbInputsCB.setHidden(notAllGates)
                for item in selection:
                    if not isinstance(item, CircuitItem):
                        self.showCategoryLabel.setHidden(True)
                        self.showCategoryCB.setHidden(True)
        if size > 1:
            self.nameLabel.setHidden(True)
            self.nameLE.setHidden(True)
        if size == 1:
            self.nameLE.blockSignals(True)
            self.nameLE.setText(selection[0].item.name)
            self.nameLE.blockSignals(False)
        if size >= 1:
            self.showNameCB.blockSignals(True)
            self.showNameCB.setCheckState(
                boolToCheckState(selection[0].showName))
            self.showNameCB.blockSignals(False)
            if not self.showCategoryCB.isHidden():
                self.showCategoryCB.blockSignals(True)
                self.showCategoryCB.setCheckState(
                    boolToCheckState(selection[0].showCategory))
                self.showCategoryCB.blockSignals(False)
            if not self.nbInputsCB.isHidden():
                self.nbInputsCB.blockSignals(True)
                self.nbInputsCB.setCurrentIndex(
                    selection[0].item.nb_inputs() - 2)
                self.nbInputsCB.blockSignals(False)

    def setCategoryVisibility(self, state):
        """Show/Hide the category of an item in the main view."""
        for item in self.view.scene().selectedItems():
            item.setCategoryVisibility(True if state else False)

    def setItemName(self):
        """Show/Hide the category of an item in the main view."""
        item = self.view.scene().selectedItems()[0]
        item.item.setName(self.nameLE.text())
        item.setupPaint()

    def setNameVisibility(self, state):
        """Show/Hide the name of an item in the main view."""
        for item in self.view.scene().selectedItems():
            item.setNameVisibility(True if state else False)

    def setNbInputs(self, index):
        """Add/Remove inputs from basic gates."""
        for item in self.view.scene().selectedItems():
            item.setNbInputs(index + 2)


class SelectionOptionsDockWidget(QDockWidget):
    """A dock widget containing our tool options."""

    def __init__(self, view):
        super(SelectionOptionsDockWidget, self).__init__(
            self.str_selectionDockTitle)
        self.setWidget(SelectionOptions(view))
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
