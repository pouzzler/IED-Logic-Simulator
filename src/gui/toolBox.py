#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore


class toolBox(QtGui.QListWidget):
    """Une boîte à outils contenant les portes et circuits disponibles"""
    
    clicked = QtCore.Signal(str)
    
    def __init__(self):
        super(toolBox, self).__init__()
        self.insertItems(0, ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor'])
        self.setDragEnabled(True)

    def focusInEvent(self, event):
        self.clicked.emit(u'Ce panneau contient les objets que vous pouvez '
                          u'déposer dans la zone de dessin')
