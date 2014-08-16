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

        self.orientLabel = QLabel(self.str_orientation, self)
        self.gridLayout.addWidget(self.orientLabel, 4, 0, 1, 1)

        self.cwRotationButton = QPushButton(self)
        self.cwRotationButton.setText("↻")
        self.cwRotationButton.clicked.connect(
            lambda: self.view.rotateItems(90))
        self.gridLayout.addWidget(self.cwRotationButton, 4, 1, 1, 1)

        self.acwRotationButton = QPushButton(self)
        self.acwRotationButton.setText("↺")
        self.acwRotationButton.clicked.connect(
            lambda: self.view.rotateItems(-90))
        self.gridLayout.addWidget(self.acwRotationButton, 4, 2, 1, 1)
        self.updateOptions()

    def updateOptions(self):
        """Hides irrelevant options, and sets reasonable values for the
        visible options.
        """
        selection = self.view.scene().selectedItems()
        for widget in self.findChildren(QWidget):     # Hide all options
            widget.setHidden(True)
        if not len(selection):          # then return if no selection.
            return
        # The number of entries option only applies to gates (except NOT)
        notAllGates = any([i.data.__class__ not in [
            AndGate, NandGate, OrGate, NorGate, XorGate, XnorGate]
            for i in selection])
        self.nbInputsLabel.setHidden(notAllGates)
        self.nbInputsCB.setHidden(notAllGates)
        # Only circuits may display their category, we only show the
        # option if at least one circuit is present
        if any([isinstance(i, CircuitItem) for i in selection]):
            self.showCategoryLabel.setHidden(False)
            self.showCategoryCB.setHidden(False)
        # Wires have no name; no need for name visibility
        if not all([isinstance(i, WireItem) for i in selection]):
            self.showNameLabel.setHidden(False)
            self.showNameCB.setHidden(False)
        # We only show the name if we have exactly one non-wire item
        if len(selection) == 1 and not isinstance(selection[0], WireItem):
            self.nameLE.blockSignals(True)
            self.nameLE.setText(selection[0].data.name)
            self.nameLE.blockSignals(False)
            self.nameLE.setHidden(False)

    def setCategoryVisibility(self, state):
        """Show/Hide the category of an item in the main view."""
        for item in self.view.scene().selectedItems():
            if isinstance(item, CircuitItem):
                item.setCategoryVisibility(True if state else False)

    def setItemName(self):
        """Show/Hide the category of an item in the main view."""
        item = self.view.scene().selectedItems()[0]
        item.data.setName(self.nameLE.text())
        item.setupPaint()

    def setNameVisibility(self, state):
        """Show/Hide the name of items in the main view."""
        for item in self.view.scene().selectedItems():
            if not isinstance(item, WireItem):
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
