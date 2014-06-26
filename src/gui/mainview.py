#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from gui.toolbox import ToolBox
from gui.tooloptions import ToolOptions
from gui.circuit import Circuit
#~ import engine.gates


class MainView(QtGui.QGraphicsView):
    """Une vue graphique correspondant à la scène principale"""

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        self.setAcceptDrops(True)
        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)
        # On veut être prévenus des changements de sélection dans la vue
        # principale afin de mettre à jour le widget des options.
        self.scene().selectionChanged.connect(ToolOptions.updateOptions)

    def dragEnterEvent(self, e):
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        model = QtGui.QStandardItemModel()
        model.dropMimeData(
            e.mimeData(), QtCore.Qt.CopyAction, 0, 0,
            QtCore.QModelIndex())
        item = model.item(0)
        text = item.text()
        i = Circuit(2, 1, text)
        self.scene().addItem(i)
        i.setPos(e.pos())

    def keyPressEvent(self, e):
        """Gère les évènements clavier : suppression, rotation, alignement"""
        # Del, suppression
        if e.key() == QtCore.Qt.Key_Delete:
            for item in self.scene().selectedItems():
                self.scene().removeItem(item)
        # <- , rotation inverse au sens des aiguilles
        elif e.key() == QtCore.Qt.Key_Left:
            group = self.scene().createItemGroup(self.scene().selectedItems())
            group.setRotation(group.rotation() - 90)
            self.scene().destroyItemGroup(group)
        # -> , rotation dans le sens des aiguilles
        elif e.key() == QtCore.Qt.Key_Right:
            group = self.scene().createItemGroup(self.scene().selectedItems())
            group.setRotation(group.rotation() + 90)
            self.scene().destroyItemGroup(group)
        # L, aligner à gauche
        elif e.key() == QtCore.Qt.Key_L:
            left = min(
                [item.scenePos().x() for item in self.scene().selectedItems()])
            for item in self.scene().selectedItems():
                item.setPos(left, item.scenePos().y())
        # R, aligner à droite
        elif e.key() == QtCore.Qt.Key_R:
            right = max(
                [item.scenePos().x() for item in self.scene().selectedItems()])
            for item in self.scene().selectedItems():
                item.setPos(right, item.scenePos().y())
        # T, aligner en haut
        elif e.key() == QtCore.Qt.Key_T:
            top = min(
                [item.scenePos().y() for item in self.scene().selectedItems()])
            for item in self.scene().selectedItems():
                item.setPos(item.scenePos().x(), top)
        # B, aligner en bas
        elif e.key() == QtCore.Qt.Key_B:
            bottom = max(
                [item.scenePos().y() for item in self.scene().selectedItems()])
            for item in self.scene().selectedItems():
                item.setPos(item.scenePos().x(), bottom)
