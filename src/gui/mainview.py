#!/usr/bin/env python3
# coding=utf-8

from PySide import QtCore
from PySide.QtGui import (
    QImage, QInputDialog, QGraphicsItem, QGraphicsScene, QGraphicsView,
    QMenu, QStandardItemModel, QBrush)
from .toolbox import ToolBox
from .selectionoptions import SelectionOptions
from .graphicitem import CircuitItem, PlugItem, WireItem
from engine.simulator import Circuit, Plug
from .settings import configFile
import engine

mainCircuit = Circuit("Main_Circuit", None)


class BgItem(QGraphicsItem):
    """Draws a light grid of points for easier alignment of items."""
    
    def __init__(self):
        super(BgItem, self).__init__()
       
    def boundingRect(self):
        pass
        
    def paint(self, painter, option, widget):
        for i in range(10):
            for j in range(10):
                painter.drawPoint(10 * i, 10 * j)


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
        #~ self.scene().addItem(BgItem())
        self.isDrawing = False

    def getNewName(self, item):
        # ret = tuple string, bool (false when the dialog is dismissed)
        ret = QInputDialog.getText(self, u'Set name', u'Name:')
        if ret[1]:
            self.setItemName(ret[0], item)

    def setItemName(self, name, item):
        if isinstance(item, CircuitItem):
            if item.item.setName(name):
                item.update()
        elif isinstance(item, Plug):
            item.setName(name)

    def contextMenuEvent(self, e):
        """Pops a contextual menu up on right-clicks"""
        item = self.itemAt(e.pos())
        if item:
            menu = QMenu(self)
            if isinstance(item, CircuitItem):
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                plug = item.handleAtPos(pos)
                item = plug if plug else item
                menu.addAction("Set name", lambda: self.getNewName(item))
            elif isinstance(item, PlugItem):
                menu.addAction("Set name", lambda: self.getNewName(item))
                if item.isInput:
                    menu.addAction(
                        str(item.value), lambda: item.set(not item.value))
            elif isinstance(item, WireItem):
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

    def dragLeaveEvent(self, e):
        """Fixing bug where items are not fully dragged over MainView,
        then dragged away.
        """
        e.ignore()
        
    def dragMoveEvent(self, e):
        """Accept drag move events."""
        e.accept()

    def dropEvent(self, e):
        """Accept drop events."""
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
            item = CircuitItem(
                getattr(engine.gates, name + 'Gate'), mainCircuit)
        elif name == 'Input Pin':
            item = PlugItem(True, mainCircuit)
        elif name == 'Output Pin':
            item = PlugItem(False, mainCircuit)
        else:
            item = CircuitItem(Circuit, mainCircuit)
        if item:
            # Fixing the default behavious of centering the first
            # item added to scene.
            if not len(self.scene().items()):
                self.scene().setSceneRect(0, 0, 1, 1)
            self.scene().addItem(item)
            item.setPos(item.mapFromScene(self.mapToScene(e.pos())))

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
        elif e.key() == QtCore.Qt.Key_Delete:
            for item in selection:
                if isinstance(item, CircuitItem):
                    mainCircuit.remove(item.item)
                    item.circuit = None
                elif isinstance(item, Plug):
                    mainCircuit.remove(item)
                elif isinstance(item, WireItem) and hasattr(item, 'endIO'):
                    item.startIO.disconnect(item.endIO)
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
        that represents a Plug, we create a WireItem.
        Over a WireItem handle, we extend the WireItem.
        """
        # Reserve right-clicks for contextual menus.
        if e.buttons() == QtCore.Qt.RightButton:
            super(MainView, self).mousePressEvent(e)
            return
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if isinstance(item, CircuitItem) or isinstance(item, PlugItem):
                plug = item.handleAtPos(pos)
                if plug:
                    self.isDrawing = True
                    self.currentWire = WireItem(plug, self.mapToScene(e.pos()))
                    self.scene().addItem(self.currentWire)
                    return   # no super(), prevents dragging/selecting
            elif isinstance(item, WireItem):
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
                if isinstance(item, CircuitItem) or isinstance(item, PlugItem):
                    plug = item.handleAtPos(pos)
                    if (plug and
                            self.currentWire.handleAtPos(
                                self.currentWire.mapFromScene(
                                    self.mapToScene(e.pos())))):
                        if not self.currentWire.connect(plug):
                            self.scene().removeItem(self.currentWire)
                        return
            self.currentWire.addPoint()
            self.currentWire = None
        super(MainView, self).mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        """Changes the cursor shape on mousing over a handle."""
        if self.isDrawing:
            self.currentWire.moveLastPoint(
                self.currentWire.mapFromScene(self.mapToScene(e.pos())))
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if ((isinstance(item, CircuitItem) or isinstance(item, PlugItem))
                    and item.handleAtPos(pos)):
                self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                return
            elif (isinstance(item, WireItem) and item.handleAtPos(pos) and
                    not self.isDrawing):
                self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                return
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super(MainView, self).mouseMoveEvent(e)
        
    def write(self, message):
        """Displays a short-lived informative message."""
        scene = self.scene()
        msg = scene.addText(message)
        QtCore.QTimer.singleShot(1500, lambda: scene.removeItem(msg))
