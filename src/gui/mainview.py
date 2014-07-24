#!/usr/bin/env python3
# coding=utf-8


from PySide import QtCore
from PySide.QtGui import (
    QInputDialog, QGraphicsScene, QGraphicsView, QMenu,
    QStandardItemModel)
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .graphicitem import CircuitItem, IOItem, Wire
from engine.simulator import Circuit, Plug
from .settings import configFile


mainCircuit = Circuit("Main_Circuit", None)


class MainView(QGraphicsView):
    """A graphic representation of a circuit schematic created by the
    user. This view manages most user interaction, in particular:
    * Adding logic gates & circuits
    * Linking outputs and inputs
    * Translating and rotating elements around
    * Setting input values
    """

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        # Accept dragged items from the toolbox to the main view.
        self.setAcceptDrops(True)
        # Allow mouseover effects (self.mouseMoveEvent)
        self.setMouseTracking(True)
        self.setScene(QGraphicsScene(parent))
        self.isDrawing = False

    def getNewName(self, item):
        # ret = tuple string, bool (false when the dialog is dismissed)
        ret = QInputDialog.getText(self, u'Set name', u'Name:')
        if ret[1]:
            setItemName(self, item, ret[0])
            
    def setItemName(self, name, item):
        if isinstance(item, CircuitItem):
            if item.circuit.setName(name):
                item.initPath()
        elif isinstance(item, Plug):
            item.setName(name)

    def contextMenuEvent(self, e):
        """Pops a contextual menu up on right-clicks"""
        item = self.itemAt(e.pos())
        if item:
            menu = QMenu(self)
            if isinstance(item, CircuitItem):
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                ioatpos = item.IOAtPos(pos)
                item = ioatpos if ioatpos else item
                menu.addAction("Set name", lambda: self.getNewName(item))
            elif isinstance(item, IOItem):
                menu.addAction("Set name", lambda: self.getNewName(item))
                if item.isInput:
                    menu.addAction(
                        str(item.value), lambda: item.set(not item.value))
            elif isinstance(item, Wire):
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                if item.handleAtPos(pos):
                    menu.addAction("Remove last", lambda: item.removeLast())
            menu.popup(e.globalPos())

    def dragEnterEvent(self, e):
        """Accept drag events coming from ToolBox."""
        if isinstance(e.source(), ToolBox):
            e.accept()
        # Refuse drags from anything but our ToolBox
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        """Accept drag move events."""
        e.accept()

    def dropEvent(self, e):
        """Accept drop events."""
        # TODO: Found on the web, maybe a cleaner way exists.
        # it would be better to receive the correct item directly,
        # rather than test some text string.
        model = QStandardItemModel()
        model.dropMimeData(
            e.mimeData(),
            QtCore.Qt.CopyAction,
            0,
            0,
            QtCore.QModelIndex())
        name = model.item(0).text()
        item = None
        if name in ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']:
            item = CircuitItem(name, mainCircuit)
        elif name == 'Input Pin':
            item = IOItem(True, mainCircuit)
        elif name == 'Output Pin':
            item = IOItem(False, mainCircuit)
        if item:
            self.scene().addItem(item)
            item.setPos(e.pos())

    def keyPressEvent(self, e):
        """Manages keyboard events, in particular item rotation,
        translation, removal and alignment.
        """
        scene = self.scene()
        selection = scene.selectedItems()
        # ESC, unselect all items
        if e.key() == QtCore.Qt.Key_Escape:
            for item in selection:
                item.setSelected(False)
        # Del, suppression
        if e.key() == QtCore.Qt.Key_Delete:
            for item in selection:
                if isinstance(item, CircuitItem):
                    mainCircuit.remove(item.circuit)
                    item.circuit = None
                elif isinstance(item, Plug):
                    mainCircuit.remove(item)
                scene.removeItem(item)
        # <- , anti-clockwise rotation
        # TODO: serious problem with Qt: it is impossible to rotate
        # a QGraphicsItemGroup around its gravity center like the
        # current code does for individual items even though the
        # group class inherits from the graphicsitem class.
        # EDIT: group.boundingRect() is apparently in scene coordinates
        elif e.key() == QtCore.Qt.Key_Left:
            #~ group = scene.createItemGroup(selection)
            #~ print(selection[0].boundingRect(), group.boundingRect())
            #~ x = group.boundingRect().width() / 2
            #~ y = group.boundingRect().height() / 2
            #~ group.setTransformOriginPoint(x, y)
            #~ group.setRotation(group.rotation() - 90)
            #~ group.setTransform(
            #~ QTransform().translate(x, y).rotate(-90).translate(y, x))
            #~ scene.destroyItemGroup(group)
            for item in selection:
                x = item.boundingRect().width() / 2
                y = item.boundingRect().height() / 2
                item.setTransformOriginPoint(x, y)
                item.setRotation(item.rotation() - 90)
        # -> , clockwise rotation
        elif e.key() == QtCore.Qt.Key_Right:
            for item in selection:
                x = item.boundingRect().width() / 2
                y = item.boundingRect().height() / 2
                item.setTransformOriginPoint(x, y)
                item.setRotation(item.rotation() + 90)
        # L, left align
        elif e.key() == QtCore.Qt.Key_L:
            left = min([item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(left, item.scenePos().y())
        # R, right align
        elif e.key() == QtCore.Qt.Key_R:
            right = max([item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(right, item.scenePos().y())
        # T, top align
        elif e.key() == QtCore.Qt.Key_T:
            top = min([item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), top)
        # B, bottom align
        elif e.key() == QtCore.Qt.Key_B:
            bottom = max([item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), bottom)

    def mousePressEvent(self, e):
        """When the mouse is pressed over a portion of a graphic item
        that represents an engine.simulator.Plug, that Plug is appended
        to self.connectionData.
        """
        # Reserve right-clicks for contextual menus.
        if e.buttons() == QtCore.Qt.RightButton:
            super(MainView, self).mousePressEvent(e)
            return
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                ioatpos = item.IOAtPos(pos)
                if ioatpos:
                    self.isDrawing = True
                    self.currentWire = Wire(ioatpos, self.mapToScene(e.pos()))
                    self.scene().addItem(self.currentWire)
                    return   # no super(), prevents dragging/selecting
            elif isinstance(item, Wire):
                if item.handleAtPos(pos):
                    self.currentWire = item
                    self.isDrawing = True
                    return   # no super(), prevents dragging/selecting
        # Didn't click a handle? We wanted to drag or select
        super(MainView, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """When the mouse is released over an I/O, and was previously
        pressed over another I/O, if one is an input, and the other an
        output, a connection will be created between the two of them.
        """
        # Ignore right-clicks.
        if e.buttons() == QtCore.Qt.RightButton:
            super(MainView, self).mousePressEvent(e)
            return
        if self.isDrawing:
            self.isDrawing = False
            item = self.itemAt(e.pos())
            if item:
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                    ioatpos = item.IOAtPos(pos)
                    if ioatpos:
                        self.currentWire.startIO.connect(ioatpos)
            self.currentWire.addPoint()
            self.currentWire = None
        super(MainView, self).mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        """Changes the cursor shape when the mouse hovers over an
        input or output pin.
        """
        if self.isDrawing:
            self.currentWire.moveLastPoint(
                self.currentWire.mapFromScene(self.mapToScene(e.pos())))
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                ioatpos = item.IOAtPos(pos)
                if ioatpos:
                    self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                    return
            elif isinstance(item, Wire) and item.handleAtPos(pos):
                self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                return
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super(MainView, self).mouseMoveEvent(e)

    def toast(self, message):
        """Displays a short-lived informative message."""
        scene = self.scene()
        toast = scene.addText(message)
        QtCore.QTimer.singleShot(1500, lambda: scene.removeItem(toast))
