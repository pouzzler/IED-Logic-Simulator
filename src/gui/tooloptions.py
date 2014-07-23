#!/usr/bin/env python3
# coding=utf-8

from PySide.QtGui import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton)
from PySide.QtCore import Signal, Qt, QMetaObject, Slot


class ToolOptions(QWidget):
    """Widget for modifying the selected circuit or gate."""

    clicked = Signal(str)

    def __init__(self):
        super(ToolOptions, self).__init__()

        self.setObjectName("tooloptions")
        self.resize(400, 300)
        self.setFocusPolicy(Qt.StrongFocus)
        self.gridLayout = QGridLayout(self)
        QMetaObject.connectSlotsByName(self)
        self.gridLayout.setObjectName("gridLayout")

        self.nameLabel = QLabel(self)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText('Name:')
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)

        self.nameLE = QLineEdit(self)
        self.nameLE.setObjectName("nameLE")
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 2)

        self.nbInputsLabel = QLabel(self)
        self.nbInputsLabel.setObjectName("label")
        self.nbInputsLabel.setText('Inputs number:')
        self.gridLayout.addWidget(self.nbInputsLabel, 1, 0, 1, 1)

        self.nbInputsLE = QLineEdit(self)
        self.nbInputsLE.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.nbInputsLE, 1, 1, 1, 2)

        self.orientLabel = QLabel(self)
        self.orientLabel.setObjectName("orientLabel")
        self.orientLabel.setText('Orientation:')
        self.gridLayout.addWidget(self.orientLabel, 2, 0, 1, 1)

        self.cwRotationButton = QPushButton(self)
        self.cwRotationButton.setObjectName("cwRotationButton")
        self.cwRotationButton.setText("↻")
        self.gridLayout.addWidget(self.cwRotationButton, 2, 1, 1, 1)

        self.acwRotationButton = QPushButton(self)
        self.acwRotationButton.setEnabled(True)
        self.acwRotationButton.setObjectName("pushButton")
        self.acwRotationButton.setText("↺")
        self.gridLayout.addWidget(self.acwRotationButton, 2, 2, 1, 1)

        self.valueLabel = QLabel(self)
        self.valueLabel.setObjectName("valueLabel")
        self.valueLabel.setText('Value:')
        self.gridLayout.addWidget(self.valueLabel, 3, 0, 1, 1)

        self.lowRadioButton = QRadioButton(self)
        self.lowRadioButton.setStatusTip("")
        self.lowRadioButton.setShortcut("")
        self.lowRadioButton.setObjectName("lowRadioButton")
        self.lowRadioButton.setText('Low')
        self.gridLayout.addWidget(self.lowRadioButton, 3, 1, 1, 1)

        self.highRadioButton = QRadioButton(self)
        self.highRadioButton.setObjectName("highRadioButton")
        self.highRadioButton.setText('High')
        self.gridLayout.addWidget(self.highRadioButton, 3, 2, 1, 1)

    @Slot()
    def focusInEvent(self, event):
        self.clicked.emit(
            u"Ce panneau permet de régler les options"
            u" de l'objet sélectionné")
