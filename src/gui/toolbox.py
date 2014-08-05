#!/usr/bin/env python3
# coding=utf-8

import inspect
from os import listdir
from PySide.QtCore import QByteArray, QDir, QMimeData, Qt
from PySide.QtGui import (
    QDockWidget, QDrag, QIcon, QTreeWidget, QTreeWidgetItem)
from .util import filePath
from engine import gates


class ToolBox(QTreeWidget):
    """A toolbox that contains logic gates and user circuits, for use
    in the main designer window.
    """

    def __init__(self):
        super(ToolBox, self).__init__()
        self.setDragEnabled(True)
        self.setColumnCount(2)
        self.header().setVisible(False)
        gatesheader = QTreeWidgetItem(self, [self.str_basicGates])
        gatesheader.setExpanded(True)
        imgDir = filePath('icons/')
        for name, class_ in inspect.getmembers(
                gates,
                lambda m: (
                    inspect.isclass(m) and m.__module__ == 'engine.gates')):
            item = QTreeWidgetItem(gatesheader, [name[:-4]])
            item.setIcon(0, QIcon(imgDir + name + '.png'))
        ioheader = QTreeWidgetItem(self, [self.str_IO])
        ioheader.setExpanded(True)
        [
            QTreeWidgetItem(ioheader, [name])
            for name in [self.str_I, self.str_O, self.str_Clock]]
        self.userheader = QTreeWidgetItem(self, [self.str_userCircuits])
        [QTreeWidgetItem(self.userheader, [name[:-4], 'user'])
            for name in listdir(filePath('user/'))]
        self.userheader.setExpanded(True)

    def addUserCircuit(self, name):
        QTreeWidgetItem(self.userheader, [name, 'user'])


class ToolBoxDockWidget(QDockWidget):
    """A dock widget containing our toolbox."""

    def __init__(self):
        super(ToolBoxDockWidget, self).__init__(self.str_dockTitle)
        self.setWidget(ToolBox())
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
