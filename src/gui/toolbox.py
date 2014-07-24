#!/usr/bin/env python3
# coding=utf-8

import inspect

from PySide.QtGui import QTreeWidget, QTreeWidgetItem
from PySide.QtCore import Signal, Slot

import engine.gates, engine.circuits

class ToolBox(QTreeWidget):
    """A toolbox that contains logic gates and user circuits, for use
    in the main designer window.
    """

    def __init__(self):
        super(ToolBox, self).__init__()
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.header().setVisible(False)
        gatesheader = QTreeWidgetItem(self, [u'Basic Gates'])
        gates = [
            QTreeWidgetItem(gatesheader, [name[:-4]])
            for name, _ in inspect.getmembers(
                engine.gates,
                lambda m: inspect.isclass(m) and m.__module__ == 'engine.gates')]
        ioheader = QTreeWidgetItem(self, [u'I/O'])
        io = [
            QTreeWidgetItem(ioheader, [name])
            for name in ['Input Pin', 'Output Pin']]
        circuitsheader = QTreeWidgetItem(self, [u'Circuits'])
        circuits = [
            QTreeWidgetItem(circuitsheader, [name[:-4]])
            for name, _ in inspect.getmembers(
                engine.circuits,
                lambda m: inspect.isclass(m) and m.__module__ == 'engine.circuits')]
        userheader = QTreeWidgetItem(self, [u'User Circuits'])

