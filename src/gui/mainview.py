#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .circuit import Circuit


class MainView(QtGui.QGraphicsView):
    """A graphic view representing a circuit schematic, as created by
    the user. This view manages most user interaction :
    * Adding logic gates & circuits
    * Linking outputs and inputs
    * Translating and rotating elements around
    """

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        self.setAcceptDrops(True)
        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)
        self.connectionData = None

    def dragEnterEvent(self, e):
        """For receiving items from the toolbox panel,
        QT demands overloading this function.
        """

        e.accept()

    def dragMoveEvent(self, e):
        """For receiving items from the toolbox panel,
        QT demands overloading this function.
        """

        e.accept()

    def dropEvent(self, e):
        """For receiving items from the toolbox panel,
        QT demands overloading this function.
        """

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
        """Gère les évènements clavier : suppression, rotation,
        alignement.
        """

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
        """When a I/O is clicked, fills the field connectionData with
        that I/O's info.
        """

        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            for i in range(item.nInputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    - item.DIAMETER, i * item.IO_HEIGHT + item.iOffset +
                    item.BODY_OFFSET - item.DIAMETER, item.DIAMETER * 3,
                    item.DIAMETER * 3)
                if path.contains(pos):
                    self.connectionData = [item, item.inputList[i], i]
                    return
            for i in range(item.nOutputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    item.O_RIGHT + 1 - item.DIAMETER, i * item.IO_HEIGHT +
                    item.oOffset + item.BODY_OFFSET - item.DIAMETER,
                    item.DIAMETER * 3, item.DIAMETER * 3)
                if path.contains(pos):
                    self.connectionData = [item, item.outputList[i], i]
                    return
        super(MainView, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """When the mouse is released over an I/O, and was previously
        pressed over another I/O, if one is an input, and the other an
        output, a connection will be created between the two of them.
        """

        item = self.itemAt(e.pos())
        #TODO item is not good enough (it must be a Circuit)
        if self.connectionData and item:    # We need two items to proceed
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            for i in range(item.nInputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    - item.DIAMETER, i * item.IO_HEIGHT + item.iOffset +
                    item.BODY_OFFSET - item.DIAMETER, item.DIAMETER * 3,
                    item.DIAMETER * 3)
                if path.contains(pos):
                    if self.connectionData[1].isinput:
                        print(u"Connect an input to an output.")
                    else:
                        print(
                            u"Connecting ", self.connectionData,
                            [item, item.inputList[i], i])
                        origin = item.mapToScene(
                            item.I_LEFT, i * item.IO_HEIGHT  + item.iOffset 
                            + item.BODY_OFFSET + item.DIAMETER / 2.)
                        end = self.connectionData[0].mapToScene(
                            self.connectionData[0].left, self.connectionData[2] * 
                            self.connectionData[0].IO_HEIGHT 
                            + self.connectionData[0].oOffset 
                            + self.connectionData[0].BODY_OFFSET 
                            + self.connectionData[0].DIAMETER / 2.)   
                        line = QtCore.QLineF(origin, end)
                        self.scene().addLine(line)
                    return
            for i in range(item.nOutputs):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    item.O_RIGHT + 1 - item.DIAMETER, i * item.IO_HEIGHT +
                    item.oOffset + item.BODY_OFFSET - item.DIAMETER,
                    item.DIAMETER * 3, item.DIAMETER * 3)
                if path.contains(pos):
                    if not self.connectionData[1].isinput:
                        print(u"Connect an input to an output.")
                    else:
                        print(
                            u"Connecting ", self.connectionData,
                            [item, item.inputList[i], i])
                        origin = self.connectionData[0].mapToScene(
                            self.connectionData[0].I_LEFT,
                            self.connectionData[2] * self.connectionData[0].IO_HEIGHT 
                            + self.connectionData[0].iOffset 
                            + self.connectionData[0].BODY_OFFSET +
                            self.connectionData[0].DIAMETER / 2.)
                        end = item.mapToScene(
                            item.left, i * item.IO_HEIGHT + item.oOffset +
                            item.BODY_OFFSET + item.DIAMETER / 2.)   
                        line = QtCore.QLineF(origin, end)
                        self.scene().addLine(line)
                    return
        self.connectionData = None
        super(MainView, self).mouseReleaseEvent(e)
