#!/usr/bin/env python3
# coding=utf-8

import inspect
from PySide.QtGui import (
    QCheckBox, QComboBox, QDockWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QWidget)
from PySide.QtCore import Qt
from .graphicitem import CircuitItem
from engine.gates import *

class SelectionOptions(QWidget):
    """Widget for modifying the selected circuit or gate."""

    def __init__(self, view):
        super(SelectionOptions, self).__init__()

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.view = view
        self.view.scene().selectionChanged.connect(self.updateOptions)
        self.gridLayout = QGridLayout(self)

        self.nameLabel = QLabel('Name:', self)
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)

        self.nameLE = QLineEdit(self)
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 2)
        self.nameLE.returnPressed.connect(self.setItemName)

        self.showNameLabel = QLabel('Show name?', self)
        self.gridLayout.addWidget(self.showNameLabel, 1, 0, 1, 1)

        self.showNameCB = QCheckBox(self)
        self.gridLayout.addWidget(self.showNameCB, 1, 1, 1, 1)
        self.showNameCB.stateChanged.connect(self.setNameVisibility)

        showCategoryLabel = QLabel('Show category?', self)
        self.gridLayout.addWidget(showCategoryLabel, 2, 0, 1, 1)

        self.showCategoryCB = QCheckBox(self)
        self.gridLayout.addWidget(self.showCategoryCB, 2, 1, 1, 1)
        self.showCategoryCB.stateChanged.connect(self.setClassVisibility)

        self.nbInputsLabel = QLabel('Number of inputs:', self)
        self.gridLayout.addWidget(self.nbInputsLabel, 3, 0, 1, 1)

        self.nbInputsCB = QComboBox(self)
        self.nbInputsCB.activated.connect(self.setNbInputs)
        self.nbInputsCB.addItems([str(x) for x in range(2, 33)])
        self.gridLayout.addWidget(self.nbInputsCB, 3, 1, 1, 2)

        orientLabel = QLabel('Orientation:', self)
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
        self.lowRadioButton.setStatusTip("")
        self.lowRadioButton.setShortcut("")
        self.lowRadioButton.setText('Low')
        self.gridLayout.addWidget(self.lowRadioButton, 5, 1, 1, 1)

        self.highRadioButton = QRadioButton(self)
        self.highRadioButton.setText('High')
        self.gridLayout.addWidget(self.highRadioButton, 5, 2, 1, 1)

        self.updateOptions()

    def updateOptions(self):
        selection = self.view.scene().selectedItems()
        size = len(selection)
        # Hiding options that don't apply to the current selection.
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
        if size > 1:
            self.nameLabel.setHidden(True)
            self.nameLE.setHidden(True)
        # Putting reasonable values in the visible options  
        if size == 1:
            self.nameLE.setText(selection[0].item.name)  
        if size >= 1:
            # Wrong check box on multiple selection
            # Better than arbitrarily setting them all
            # TODO : possible solution by ignoring events while doing it
            self.showNameCB.blockSignals(True)
            self.showNameCB.setCheckState(
                Qt.CheckState.Checked if selection[0].showName
                else Qt.CheckState.Unchecked)
            self.showNameCB.blockSignals(False)
            self.showCategoryCB.blockSignals(True)
            self.showCategoryCB.setCheckState(
                Qt.CheckState.Checked if selection[0].showClassName
                else Qt.CheckState.Unchecked)
            self.showCategoryCB.blockSignals(False)
            self.nbInputsCB.blockSignals(True)
            self.nbInputsCB.setCurrentIndex(selection[0].item.nb_inputs() - 2)
            self.nbInputsCB.blockSignals(False)

    def setItemName(self):
        item = self.view.scene().selectedItems()[0]
        self.view.setItemName(self.nameLE.text(), item)

    def setNameVisibility(self, arg1):
        for item in self.view.scene().selectedItems():
            item.setNameVisibility(True if arg1 else False)

    def setClassVisibility(self, arg1):
        for item in self.view.scene().selectedItems():
            item.setClassVisibility(True if arg1 else False)

    def setNbInputs(self, index):
        for item in self.view.scene().selectedItems():
            item.setNbInputs(index + 2)

class SelectionOptionsDockWidget(QDockWidget):
    """A dock widget containing our tool options."""

    def __init__(self, view):
        super(SelectionOptionsDockWidget, self).__init__('Selection options')
        self.setWidget(SelectionOptions(view))
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
