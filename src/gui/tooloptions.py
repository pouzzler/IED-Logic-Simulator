#!/usr/bin/env python3
# coding=utf-8

from PySide.QtGui import (
    QCheckBox, QDockWidget, QGridLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QWidget)
from PySide.QtCore import Qt
from .graphicitem import CircuitItem


class ToolOptions(QWidget):
    """Widget for modifying the selected circuit or gate."""

    def __init__(self, view):
        super(ToolOptions, self).__init__()
        self.ignoreShowNameCB = True
        self.view = view
        self.view.scene().selectionChanged.connect(self.updateName)
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
        self.showNameCB.stateChanged.connect(self.toggleItemNameVisibility)

        nbInputsLabel = QLabel('Inputs number:', self)
        self.gridLayout.addWidget(nbInputsLabel, 2, 0, 1, 1)

        self.nbInputsLE = QLineEdit(self)
        self.gridLayout.addWidget(self.nbInputsLE, 2, 1, 1, 2)

        orientLabel = QLabel('Orientation:', self)
        self.gridLayout.addWidget(orientLabel, 3, 0, 1, 1)

        self.cwRotationButton = QPushButton(self)
        self.cwRotationButton.setText("↻")
        self.gridLayout.addWidget(self.cwRotationButton, 3, 1, 1, 1)

        self.acwRotationButton = QPushButton(self)
        self.acwRotationButton.setEnabled(True)
        self.acwRotationButton.setText("↺")
        self.gridLayout.addWidget(self.acwRotationButton, 3, 2, 1, 1)

        valueLabel = QLabel('Value:', self)
        self.gridLayout.addWidget(valueLabel, 4, 0, 1, 1)

        self.lowRadioButton = QRadioButton(self)
        self.lowRadioButton.setStatusTip("")
        self.lowRadioButton.setShortcut("")
        self.lowRadioButton.setText('Low')
        self.gridLayout.addWidget(self.lowRadioButton, 4, 1, 1, 1)

        self.highRadioButton = QRadioButton(self)
        self.highRadioButton.setText('High')
        self.gridLayout.addWidget(self.highRadioButton, 4, 2, 1, 1)

    def updateName(self):
        selection = self.view.scene().selectedItems()
        if len(selection) == 1 and isinstance(selection[0], CircuitItem):
            self.nameLE.setDisabled(False)
            self.nameLE.setText(selection[0].circuit.name)
            self.showNameCB.setDisabled(False)
            self.showNameCB.setCheckState(
                Qt.CheckState.Checked if selection[0].showName
                else Qt.CheckState.Unchecked)
            self.ignoreShowNameCB = True
        else:
            self.nameLE.setDisabled(True)
            self.nameLE.setText('')
            self.showNameCB.setDisabled(True)
            self.showNameCB.setCheckState(Qt.CheckState.Unchecked)

    def setItemName(self):
        item = self.view.scene().selectedItems()[0]
        self.view.setItemName(self.nameLE.text(), item)

    def toggleItemNameVisibility(self):
        if self.ignoreShowNameCB:
            print("Was true")
            self.ignoreShowNameCB = False
        else:
            print("Was false")
            item = self.view.scene().selectedItems()[0]
            item.toggleNameVisibility()


class ToolOptionsDockWidget(QDockWidget):
    """A dock widget containing our tool options."""

    def __init__(self, view):
        super(ToolOptionsDockWidget, self).__init__('Tool Options')
        self.setWidget(ToolOptions(view))
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
