#!/usr/bin/env python3
# coding=utf-8

from PySide.QtGui import QTreeWidget, QTreeWidgetItem
from PySide.QtCore import Signal, Slot


class ToolBox(QTreeWidget):
    """A toolbox that contains logic gates and user circuits, for use
    in the main designer window.
    """

    clicked = Signal(str)

    def __init__(self):
        super(ToolBox, self).__init__()
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.header().setVisible(False)
        gatesheader = QTreeWidgetItem(self, [u'Basic Gates'])
        gates = [
            QTreeWidgetItem(gatesheader, [name])
            for name in ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']]
        ioheader = QTreeWidgetItem(self, [u'I/O'])
        io = [
            QTreeWidgetItem(ioheader, [name])
            for name in ['Input Pin', 'Output Pin']]
        userheader = QTreeWidgetItem(self, [u'User Circuits'])
        self.insertTopLevelItems(0, [gatesheader, ioheader, userheader])

    @Slot()
    def focusInEvent(self, event):
        self.clicked.emit(u'This panel contains draggable items.')
