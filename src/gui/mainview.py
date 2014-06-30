#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .circuit import Circuit


class MainView(QtGui.QGraphicsView):
    """Une vue graphique représentant le schéma d'un circuit, construit
    par l'utilisateur.
    """

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        self.setAcceptDrops(True)
        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)

    @QtCore.Slot()
    def getConnectionRequest(self, pluglist):
        print(pluglist)

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
        i.requestConnection.connect(self.getConnectionRequest)

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

    def mousePressEvent(self, e):
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            for i in range(item.nInputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    - item.diameter, i * item.ioHeight + item.iOffset +
                    item.bodyOffset - item.diameter, item.diameter * 3,
                    item.diameter * 3)
                if path.contains(pos):
                    print("Je veux connecter ", item, item.inputList[i])
                    return
            for i in range(item.nOutputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    item.oRight + 1 - item.diameter, i * item.ioHeight +
                    item.oOffset + item.bodyOffset - item.diameter,
                    item.diameter * 3, item.diameter * 3)
                if path.contains(pos):
                    print("Je veux connecter  ", item, item.outputList[i])
                    return

    def mouseReleaseEvent(self, e):
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            for i in range(item.nInputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    - item.diameter, i * item.ioHeight + item.iOffset +
                    item.bodyOffset - item.diameter, item.diameter * 3,
                    item.diameter * 3)
                if path.contains(pos):
                    print("à ", item, item.inputList[i])
                    return
            for i in range(item.nOutputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    item.oRight + 1 - item.diameter, i * item.ioHeight +
                    item.oOffset + item.bodyOffset - item.diameter,
                    item.diameter * 3, item.diameter * 3)
                if path.contains(pos):
                    print("à  ", item, item.outputList[i])
                    return
