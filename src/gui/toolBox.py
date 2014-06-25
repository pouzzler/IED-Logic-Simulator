#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore


class toolBox(QtGui.QListWidget):
    """Une boîte à outils contenant les portes et circuits disponibles"""
    def __init__(self):
        super(toolBox, self).__init__()
        self.insertItems(0, ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor'])
        self.setDragEnabled(True)
