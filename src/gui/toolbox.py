#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore


class ToolBox(QtGui.QTreeWidget):
    """A toolbox that contains logic gates and user circuits, for use
    in the main designer window.
    """

    clicked = QtCore.Signal(str)

    def __init__(self):
        super(ToolBox, self).__init__()
        icon = QtGui.QIcon('gui/icons/AND.png')
        self.setDragEnabled(True)
        self.setColumnCount(2)
        gatesheader = QtGui.QTreeWidgetItem(self, [u'Basic Gates'])
        gates = [
            QtGui.QTreeWidgetItem(gatesheader, [name]) 
            for name in ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']]
        for gate in gates:
            gate.setIcon(1, icon)
        ioheader = QtGui.QTreeWidgetItem(self, [u'Inputs & Outputs'])
        io = [
            QtGui.QTreeWidgetItem(ioheader, [name]) 
            for name in ['Input Pin', 'Output Pin']]
        userheader = QtGui.QTreeWidgetItem(self, [u'User Circuits'])
        self.insertTopLevelItems(0, [gatesheader, ioheader, userheader])

    def focusInEvent(self, event):
        self.clicked.emit(u'Ce panneau contient les objets que vous pouvez '
                          u'déposer dans la zone de dessin')
