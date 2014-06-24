#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore


class toolOptions(QtGui.QWidget):
    """Contient des widgets permettant de modifier les paramètres
    de l'objet sélectionné"""
    def __init__(self):
        super(toolOptions, self).__init__()

        layout = QtGui.QVBoxLayout()
        label = QtGui.QLabel(u"Inputs number")
        layout.addWidget(label)
        nInputs = QtGui.QLineEdit(self)
        nInputs.setText('2')
        layout.addWidget(nInputs)
        self.setLayout(layout)

    @staticmethod
    def updateOptions():
        print 'toto'
