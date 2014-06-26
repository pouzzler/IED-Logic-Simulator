#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore


class ToolOptions(QtGui.QWidget):
    """Contient des widgets permettant de modifier les paramètres
    de l'objet sélectionné"""

    clicked = QtCore.Signal(str)

    def __init__(self):
        super(ToolOptions, self).__init__()
        layout = QtGui.QVBoxLayout()
        label = QtGui.QLabel(u"Inputs number")
        layout.addWidget(label)
        nInputs = QtGui.QLineEdit(self)
        nInputs.setText('2')
        layout.addWidget(nInputs)
        self.setLayout(layout)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    @QtCore.Slot()
    def focusInEvent(self, event):
        self.clicked.emit(
            u"Ce panneau permet de régler les options"
            u" de l'objet sélectionné")

    @staticmethod
    def updateOptions():
        print('toto')
