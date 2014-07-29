#!/usr/bin/env python3
# coding=utf-8

import inspect
from PySide.QtGui import (
    QCheckBox, QComboBox, QDockWidget, QGridLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QWidget)
from PySide.QtCore import Qt
from .graphicitem import CircuitItem
from engine import gates

class ToolOptions(QWidget):
    """Widget for modifying the selected circuit or gate."""

    def __init__(self, view):
        super(ToolOptions, self).__init__()
        self.ignoreShowNameCB = True
        self.view = view
        self.view.scene().selectionChanged.connect(self.updateOptions)
        self.resize(400, 300)
        self.gridLayout = QGridLayout(self)

        nameLabel = QLabel('Name:', self)
        self.gridLayout.addWidget(nameLabel, 0, 0, 1, 1)

        self.nameLE = QLineEdit(self)
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 2)
        self.nameLE.setDisabled(True)
        self.nameLE.returnPressed.connect(self.setItemName)

        showNameLabel = QLabel('Show name?', self)
        self.gridLayout.addWidget(showNameLabel, 1, 0, 1, 1)

        self.showNameCB = QCheckBox(self)
        self.showNameCB.setDisabled(True)
        self.gridLayout.addWidget(self.showNameCB, 1, 1, 1, 1)
        self.showNameCB.stateChanged.connect(self.setNameVisibility)

        showClassNameLabel = QLabel('Show class name?', self)
        self.gridLayout.addWidget(showClassNameLabel, 2, 0, 1, 1)

        self.showClassNameCB = QCheckBox(self)
        self.showClassNameCB.setDisabled(True)
        self.gridLayout.addWidget(self.showClassNameCB, 2, 1, 1, 1)
        self.showClassNameCB.stateChanged.connect(self.setClassVisibility)

        nbInputsLabel = QLabel('Number of inputs:', self)
        self.gridLayout.addWidget(nbInputsLabel, 3, 0, 1, 1)

        self.nbInputsCB = QComboBox(self)
        self.nbInputsCB.setDisabled(True)
        self.nbInputsCB.activated.connect(self.setNbInputs)
        self.nbInputsCB.addItems([str(x) for x in range(2, 33)])
        self.gridLayout.addWidget(self.nbInputsCB, 3, 1, 1, 2)

        orientLabel = QLabel('Orientation:', self)
        self.gridLayout.addWidget(orientLabel, 4, 0, 1, 1)

        self.cwRotationButton = QPushButton(self)
        self.cwRotationButton.setText("↻")
        self.gridLayout.addWidget(self.cwRotationButton, 4, 1, 1, 1)

        self.acwRotationButton = QPushButton(self)
        self.acwRotationButton.setEnabled(True)
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

    def updateOptions(self):
        self.nameLE.setDisabled(True)
        self.nameLE.setText('')
        self.showNameCB.setDisabled(True)
        self.showClassNameCB.setDisabled(True)
        self.showNameCB.setCheckState(Qt.CheckState.Unchecked)
        self.showClassNameCB.setCheckState(Qt.CheckState.Unchecked)

        selection = self.view.scene().selectedItems()
        notAllGates = True
        for item in selection:
            if not isinstance(item, CircuitItem) or item.item.__class__ not in [
                    gates.AndGate, gates.NandGate, gates.OrGate,
                    gates.NorGate, gates.XorGate, gates.XnorGate]:
                break
            notAllGates = False
        self.nbInputsCB.setDisabled(notAllGates) 
        self.showNameCB.setDisabled(False)
        self.showClassNameCB.setDisabled(False)
        if len(selection) == 1:
            self.nameLE.setDisabled(False)
            self.nameLE.setText(selection[0].item.name)
            # Wrong check box on multiple selection
            # Better than arbitrarily setting them all
            # TODO : possible solution by ignoring events while doing it
            self.showNameCB.setCheckState(
                Qt.CheckState.Checked if selection[0].showName
                else Qt.CheckState.Unchecked)
            self.showClassNameCB.setCheckState(
                Qt.CheckState.Checked if selection[0].showClassName
                else Qt.CheckState.Unchecked)
            self.nbInputsCB.setCurrentIndex(selection[0].item.nb_inputs() - 2)

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

class ToolOptionsDockWidget(QDockWidget):
    """A dock widget containing our tool options."""

    def __init__(self, view):
        super(ToolOptionsDockWidget, self).__init__('Tool Options')
        self.setWidget(ToolOptions(view))
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
