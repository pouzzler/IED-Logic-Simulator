#!/usr/bin/env python3
# coding=utf-8

import pickle
from PySide.QtCore import QModelIndex, QPoint, Qt, QTimer
from PySide.QtGui import (
    QCursor, QImage, QInputDialog, QGraphicsItem, QGraphicsScene,
    QGraphicsView, QMenu, QStandardItemModel)
from .graphicitem import CircuitItem, PlugItem, WireItem
from .selectionoptions import SelectionOptions
from .toolbox import ToolBox
from .util import filePath
from engine.simulator import Circuit, Plug
import engine


class MainView(QGraphicsView):
    """Graphic representation of a user created circuit schematic."""

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        self.setAcceptDrops(True)       # Accept dragged items.
        self.setMouseTracking(True)     # Allow mouseover effects.
        self.setScene(QGraphicsScene(parent))
        self.isDrawing = False          # user currently not drawing
        self.mainCircuit = Circuit("Main", None)
        self.tooltip = None
        self.tooltipDelay = 333
        self.tooltipTimer = QTimer()
        self.tooltipTimer.setSingleShot(True)
        self.tooltipTimer.timeout.connect(self.showTooltip)

    def clearCircuit(self):
        """Clears every item from the circuit designer."""
        for item in self.scene().items():
            if not isinstance(item, WireItem):
                self.mainCircuit.remove(item.item)
            self.scene().removeItem(item)

    def contextMenuEvent(self, e):
        """Pops a contextual menu up on right-clicks"""
        item = self.itemAt(e.pos())
        if item:
            menu = QMenu(self)
            if isinstance(item, CircuitItem):
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                plug = item.handleAtPos(pos)
                item = plug if plug else item
                menu.addAction(self.str_setName, lambda: self.getNewName(item))
            elif isinstance(item, PlugItem):
                menu.addAction(self.str_setName, lambda: self.getNewName(item))
                if item.item.isInput:
                    menu.addAction(
                        str(item.item.value), lambda: self.setAndUpdate(item))
            elif isinstance(item, WireItem):
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                if item.handleAtPos(pos):
                    menu.addAction(
                        self.str_removeLast, lambda: item.removeLast())
            menu.popup(e.globalPos())

    def dragEnterEvent(self, e):
        """Accept drag events coming from ToolBox."""
        if isinstance(e.source(), ToolBox):
            e.accept()
        else:       # Refuse all other drags.
            e.ignore()

    def dragLeaveEvent(self, e):
        """Fixes bug: items are half dragged over self, then away. (#16)"""
        e.ignore()

    def dragMoveEvent(self, e):
        """Accept drag move events."""
        e.accept()

    def dropEvent(self, e):
        """Accept drop events."""
        model = QStandardItemModel()
        model.dropMimeData(
            e.mimeData(), Qt.CopyAction, 0, 0, QModelIndex())
        name = model.item(0).text()
        item = None
        if name in ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']:
            item = CircuitItem(
                getattr(engine.gates, name + 'Gate'), self.mainCircuit)
        elif name == self.str_I:
            item = PlugItem(True, self.mainCircuit)
        elif name == self.str_O:
            item = PlugItem(False, self.mainCircuit)
        elif model.item(0, 1).text() == 'user':
            item = CircuitItem(Circuit, self.mainCircuit)
            circuit = Circuit(None, self.mainCircuit, name)
            f = open(filePath('user/') + name + '.crc', 'rb')
            children = pickle.load(f)
            f.close()
            for child in children:
                if isinstance(child[0], Plug):
                    child[0].owner = circuit
                    if child[0].isInput:
                        circuit.inputList.append(child[0])
                    else:
                        circuit.outputList.append(child[0])
                elif isinstance(child[0], Circuit):
                    child[0].owner = circuit
                    circuit.circuitList.append(child[0])
            circuit.category = name
            item.item = circuit
        if item:
            # Fixes the default behavious of centering the first
            # item added to scene.
            if not len(self.scene().items()):
                self.scene().setSceneRect(0, 0, 1, 1)
            self.scene().addItem(item)
            item.setupPaint()
            item.setPos(item.mapFromScene(self.mapToScene(e.pos())))

    def getNewName(self, item):
        """Shows a dialog, and sets item name to user input."""
        # ret = tuple string, bool
        ret = QInputDialog.getText(self, self.str_setName, self.str_name)
        if ret[1] and item.item.setName(ret[0]):    # Not canceled.
            item.update()

    def keyPressEvent(self, e):
        """Manages keyboard events."""
        scene = self.scene()
        selection = scene.selectedItems()
        # ESC, unselect all items
        if e.key() == Qt.Key_Escape:
            for item in selection:
                item.setSelected(False)
        # Del, suppression
        elif e.key() == Qt.Key_Delete:
            for item in selection:
                if isinstance(item, CircuitItem):
                    self.mainCircuit.remove(item.item)
                    item.circuit = None
                elif isinstance(item, Plug):
                    self.mainCircuit.remove(item)
                elif isinstance(item, WireItem) and item.endIO is not None:
                    item.startIO.disconnect(item.endIO)
                scene.removeItem(item)
        # <- , anti-clockwise rotation
        # TODO: serious problem with Qt: it is impossible to rotate
        # a QGraphicsItemGroup around its gravity center like the
        # current code does for individual items even though the
        # group class inherits from the graphicsitem class.
        # EDIT: group.boundingRect() is apparently in scene coordinates
        elif e.key() == Qt.Key_Left:
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
        elif e.key() == Qt.Key_Right:
            for item in selection:
                x = item.boundingRect().width() / 2
                y = item.boundingRect().height() / 2
                item.setTransformOriginPoint(x, y)
                item.setRotation(item.rotation() + 90)
        # L, left align
        elif e.key() == Qt.Key_L:
            left = min([item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(left, item.scenePos().y())
        # R, right align
        elif e.key() == Qt.Key_R:
            right = max([item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(right, item.scenePos().y())
        # T, top align
        elif e.key() == Qt.Key_T:
            top = min([item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), top)
        # B, bottom align
        elif e.key() == Qt.Key_B:
            bottom = max([item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), bottom)
        for item in selection:
            item.setupPaint()

    def mouseMoveEvent(self, e):
        """Redraw CurrentWire; change cursor on mouseOver handles."""
        # Always active unless we stop moving for self.tooltipDelay
        if not self.tooltipTimer.isActive():
            self.tooltipTimer.start(self.tooltipDelay)
            self.tooltip = None
        if self.isDrawing:
            self.currentWire.moveLastPoint(
                self.currentWire.mapFromScene(self.mapToScene(e.pos())))
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            isCircuit = isinstance(item, CircuitItem)
            if isCircuit or isinstance(item, PlugItem):
                handle = item.handleAtPos(pos)
                if handle:
                    if isCircuit:
                        self.tooltip = handle.name
                    self.setCursor(Qt.CursorShape.UpArrowCursor)
                    return
            elif (isinstance(item, WireItem) and item.handleAtPos(pos) and
                    not self.isDrawing):
                self.setCursor(Qt.CursorShape.UpArrowCursor)
                return
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super(MainView, self).mouseMoveEvent(e)

    def mousePressEvent(self, e):
        """Start Wire creation/extension."""
        # Reserve right-clicks for contextual menus.
        if e.buttons() == Qt.RightButton:
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
        """Complete Wire segments."""
        # Ignore right-clicks.
        if e.buttons() == Qt.RightButton:
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

    def setAndUpdate(self, item):
        item.item.set(not item.item.value)
        for i in self.scene().items():
            if isinstance(i, PlugItem):
                i.setupPaint()

    def showTooltip(self):
        if self.tooltip:
            scene = self.scene()
            msg = scene.addText(self.tooltip)
            msg.setPos(self.mapToScene(self.mapFromGlobal(QCursor.pos())))
            QTimer.singleShot(1000, lambda: scene.removeItem(msg))

    def write(self, message):
        """Briefly display a log WARNING."""
        scene = self.scene()
        msg = scene.addText(message)
        QTimer.singleShot(1500, lambda: scene.removeItem(msg))
