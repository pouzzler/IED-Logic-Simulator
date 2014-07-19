#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore


class ToolOptions(QtGui.QWidget):
    """A widget containing widgets for changing the properties of the
    selected circuit or gate.
    """

    clicked = QtCore.Signal(str)

    def __init__(self):
        super(ToolOptions, self).__init__()
        self.initUI()

    def initUI(self):
        # -+++++++-------------- the tooloptions widget -------------+++++++- #
        self.setObjectName("tooloptions")
        self.resize(400, 300)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.gridLayout = QtGui.QGridLayout(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.gridLayout.setObjectName("gridLayout")
        # -+++++++------------------ the name label -----------------+++++++- #
        self.nameLabel = QtGui.QLabel(self)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText('Name:')
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)
        # -+++++++---------------- the name line edit ---------------+++++++- #
        self.nameLE = QtGui.QLineEdit(self)
        self.nameLE.setObjectName("nameLE")
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 2)
        # -+++++++------------- the inputs number label -------------+++++++- #
        self.nbInputsLabel = QtGui.QLabel(self)
        self.nbInputsLabel.setObjectName("label")
        self.nbInputsLabel.setText('Inputs number:')
        self.gridLayout.addWidget(self.nbInputsLabel, 1, 0, 1, 1)
        # -+++++++----------- the inputs number line edit -----------+++++++- #
        self.nbInputsLE = QtGui.QLineEdit(self)
        self.nbInputsLE.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.nbInputsLE, 1, 1, 1, 2)
        # -+++++++-------------- the orientation label --------------+++++++- #
        self.orientLabel = QtGui.QLabel(self)
        self.orientLabel.setObjectName("orientLabel")
        self.orientLabel.setText('Orientation:')
        self.gridLayout.addWidget(self.orientLabel, 2, 0, 1, 1)
        # -+++++++---------- the clockwise rotation button ----------+++++++- #
        self.cwRotationButton = QtGui.QPushButton(self)
        self.cwRotationButton.setObjectName("cwRotationButton")
        self.cwRotationButton.setText("↻")
        self.gridLayout.addWidget(self.cwRotationButton, 2, 1, 1, 1)
        # -+++++++------- the anti-clockwise rotation button --------+++++++- #
        self.acwRotationButton = QtGui.QPushButton(self)
        self.acwRotationButton.setEnabled(True)
        self.acwRotationButton.setObjectName("pushButton")
        self.acwRotationButton.setText("↺")
        self.gridLayout.addWidget(self.acwRotationButton, 2, 2, 1, 1)
        # -+++++++----------------- the value label -----------------+++++++- #
        self.valueLabel = QtGui.QLabel(self)
        self.valueLabel.setObjectName("valueLabel")
        self.valueLabel.setText('Value:')
        self.gridLayout.addWidget(self.valueLabel, 3, 0, 1, 1)
        # -+++++++-------------- the low radio button ---------------+++++++- #
        self.lowRadioButton = QtGui.QRadioButton(self)
        self.lowRadioButton.setStatusTip("")
        self.lowRadioButton.setShortcut("")
        self.lowRadioButton.setObjectName("lowRadioButton")
        self.lowRadioButton.setText('Low')
        self.gridLayout.addWidget(self.lowRadioButton, 3, 1, 1, 1)
        # -+++++++-------------- the high radio button --------------+++++++- #
        self.highRadioButton = QtGui.QRadioButton(self)
        self.highRadioButton.setObjectName("highRadioButton")
        self.highRadioButton.setText('High')
        self.gridLayout.addWidget(self.highRadioButton, 3, 2, 1, 1)

    @QtCore.Slot()
    def focusInEvent(self, event):
        self.clicked.emit(
            u"Ce panneau permet de régler les options"
            u" de l'objet sélectionné")

    @QtCore.Slot()
    def updateOptions():
        print('toto')
