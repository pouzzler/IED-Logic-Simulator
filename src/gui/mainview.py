#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .circuititem import CircuitItem
from engine.comod import _INPUT, _OUTPUT


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
        name = item.text()
        c = CircuitItem(name)
        self.scene().addItem(c)
        c.setPos(e.pos())

    def keyPressEvent(self, e):
        """Manages keyboard events, in particular item rotation,
        translation, removal and alignment.
        """

        scene = self.scene()
        selection = scene.selectedItems()
        # Del, suppression
        if e.key() == QtCore.Qt.Key_Delete:
            for item in selection:
                scene.removeItem(item)
        # <- , rotation inverse au sens des aiguilles
        elif e.key() == QtCore.Qt.Key_Left:
            group = scene.createItemGroup(selection)
            group.setRotation(group.rotation() - 90)
            scene.destroyItemGroup(group)
        # -> , rotation dans le sens des aiguilles
        elif e.key() == QtCore.Qt.Key_Right:
            group = scene.createItemGroup(selection)
            group.setRotation(group.rotation() + 90)
            scene.destroyItemGroup(group)
        # L, aligner à gauche
        elif e.key() == QtCore.Qt.Key_L:
            left = min(
                [item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(left, item.scenePos().y())
        # R, aligner à droite
        elif e.key() == QtCore.Qt.Key_R:
            right = max(
                [item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(right, item.scenePos().y())
        # T, aligner en haut
        elif e.key() == QtCore.Qt.Key_T:
            top = min(
                [item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), top)
        # B, aligner en bas
        elif e.key() == QtCore.Qt.Key_B:
            bottom = max(
                [item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), bottom)

    def mousePressEvent(self, e):
        """When the mouse is pressed over an I/O, fills the field
        connectionData with that I/O's info.
        """
        
        self.connectionData = []
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            for i in range(item.circuit.nb_inputs()):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    - item.DIAMETER, i * item.IO_HEIGHT + item.iOffset +
                    item.BODY_OFFSET - item.DIAMETER, item.DIAMETER * 3,
                    item.DIAMETER * 3)
                if path.contains(pos):
                    self.connectionData = [item, item.circuit.inputList[i], i]
                    return
            for i in range(item.circuit.nb_outputs()):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    item.O_RIGHT + 1 - item.DIAMETER, i * item.IO_HEIGHT +
                    item.oOffset + item.BODY_OFFSET - item.DIAMETER,
                    item.DIAMETER * 3, item.DIAMETER * 3)
                if path.contains(pos):
                    self.connectionData = [item, item.circuit.outputList[i], i]
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
            for i in range(item.circuit.nb_inputs()):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    - item.DIAMETER, i * item.IO_HEIGHT + item.iOffset +
                    item.BODY_OFFSET - item.DIAMETER, item.DIAMETER * 3,
                    item.DIAMETER * 3)
                if path.contains(pos):
                    if self.connectionData[1].ptype is _INPUT:
                        self.toast(u"Connect an input to an output.")
                    else:
                        origin = item.mapToScene(
                            item.I_LEFT, i * item.IO_HEIGHT + item.iOffset
                            + item.BODY_OFFSET + item.DIAMETER / 2.)
                        end = self.connectionData[0].mapToScene(
                            self.connectionData[0].left,
                            self.connectionData[2] *
                            self.connectionData[0].IO_HEIGHT
                            + self.connectionData[0].oOffset
                            + self.connectionData[0].BODY_OFFSET
                            + self.connectionData[0].DIAMETER / 2.)
                        line = QtCore.QLineF(origin, end)
                        self.scene().addLine(line)
                        item.circuit.inputList[i].connect(
                            self.connectionData[1])
                    return
            for i in range(item.circuit.nb_outputs()):
                path = QtGui.QPainterPath()
                path.addEllipse(
                    item.O_RIGHT + 1 - item.DIAMETER, i * item.IO_HEIGHT +
                    item.oOffset + item.BODY_OFFSET - item.DIAMETER,
                    item.DIAMETER * 3, item.DIAMETER * 3)
                if path.contains(pos):
                    if self.connectionData[1].ptype is _OUTPUT:
                        self.toast(u"Connect an input to an output.")
                    else:
                        origin = self.connectionData[0].mapToScene(
                            self.connectionData[0].I_LEFT,
                            self.connectionData[2] *
                            self.connectionData[0].IO_HEIGHT
                            + self.connectionData[0].iOffset
                            + self.connectionData[0].BODY_OFFSET +
                            self.connectionData[0].DIAMETER / 2.)
                        end = item.mapToScene(
                            item.left, i * item.IO_HEIGHT + item.oOffset +
                            item.BODY_OFFSET + item.DIAMETER / 2.)
                        line = QtCore.QLineF(origin, end)
                        self.scene().addLine(line)
                        item.circuit.inputList[i].connect(
                            self.connectionData[1])
                    return
        self.connectionData = None
        super(MainView, self).mouseReleaseEvent(e)

    def toast(self, message):
        """Displays a short-lived informative message."""
        scene = self.scene()
        toast = scene.addText(message)
        QtCore.QTimer.singleShot(1500, lambda: scene.removeItem(toast))
