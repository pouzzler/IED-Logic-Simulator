#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
import os


class ToolBox(QtGui.QTreeWidget):
    """A toolbox that contains logic gates and user circuits, for use
    in the main designer window.
    """

    clicked = QtCore.Signal(str)

    def __init__(self):
        super(ToolBox, self).__init__()
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.header().setVisible(False)
        gatesheader = QtGui.QTreeWidgetItem(self, [u'Basic Gates'])
        gates = [
            QtGui.QTreeWidgetItem(gatesheader, [name])
            for name in ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']]
        ioheader = QtGui.QTreeWidgetItem(self, [u'I/O'])
        io = [
            QtGui.QTreeWidgetItem(ioheader, [name])
            for name in ['Input Pin', 'Output Pin']]
        userheader = QtGui.QTreeWidgetItem(self, [u'User Circuits'])
        self.insertTopLevelItems(0, [gatesheader, ioheader, userheader])

    def focusInEvent(self, event):
        self.clicked.emit(
            u'This panel contains items draggable to the main area.')
