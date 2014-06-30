#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore


class ToolBox(QtGui.QListWidget):
    """A toolbox that contains logic gates and user circuits, for use
    in the main designer window.
    """

    clicked = QtCore.Signal(str)

    def __init__(self):
        super(ToolBox, self).__init__()
        self.insertItems(0, ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor'])
        self.setDragEnabled(True)

    def focusInEvent(self, event):
        self.clicked.emit(u'Ce panneau contient les objets que vous pouvez '
                          u'déposer dans la zone de dessin')
