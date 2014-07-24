#!/usr/bin/env python3
# coding=utf-8

from PySide.QtGui import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton)
from .graphicitem import CircuitItem

class ToolOptions(QWidget):
    """Widget for modifying the selected circuit or gate."""

    def __init__(self, view):
        super(ToolOptions, self).__init__()
        self.view = view
        self.view.scene().selectionChanged.connect(self.grayOrSetNameLE)
        self.resize(400, 300)
        self.gridLayout = QGridLayout(self)

        nameLabel = QLabel('Name:', self)
        self.gridLayout.addWidget(nameLabel, 0, 0, 1, 1)

        self.nameLE = QLineEdit(self)
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 2)
        self.nameLE.setDisabled(True)
        self.nameLE.textChanged.connect(self.setItemName)

        nbInputsLabel = QLabel('Inputs number:', self)
        self.gridLayout.addWidget(nbInputsLabel, 1, 0, 1, 1)

        self.nbInputsLE = QLineEdit(self)
        self.gridLayout.addWidget(self.nbInputsLE, 1, 1, 1, 2)

        orientLabel = QLabel('Orientation:', self)
        self.gridLayout.addWidget(orientLabel, 2, 0, 1, 1)

        self.cwRotationButton = QPushButton(self)
        self.cwRotationButton.setText("↻")
        self.gridLayout.addWidget(self.cwRotationButton, 2, 1, 1, 1)

        self.acwRotationButton = QPushButton(self)
        self.acwRotationButton.setEnabled(True)
        self.acwRotationButton.setText("↺")
        self.gridLayout.addWidget(self.acwRotationButton, 2, 2, 1, 1)

        valueLabel = QLabel('Value:', self)
        self.gridLayout.addWidget(valueLabel, 3, 0, 1, 1)

        self.lowRadioButton = QRadioButton(self)
        self.lowRadioButton.setStatusTip("")
        self.lowRadioButton.setShortcut("")
        self.lowRadioButton.setText('Low')
        self.gridLayout.addWidget(self.lowRadioButton, 3, 1, 1, 1)

        self.highRadioButton = QRadioButton(self)
        self.highRadioButton.setText('High')
        self.gridLayout.addWidget(self.highRadioButton, 3, 2, 1, 1)

    def grayOrSetNameLE(self):
        selection = self.view.scene().selectedItems()
        if len(selection) == 1 and isinstance(selection[0], CircuitItem): 
            self.nameLE.setDisabled(False)
            self.nameLE.setText(selection[0].circuit.name)
        else:
            self.nameLE.setDisabled(True)
        
    def setItemName(self):
        item = self.view.scene().selectedItems()[0]
        self.view.setItemName(self.nameLE.text(), item)
            
