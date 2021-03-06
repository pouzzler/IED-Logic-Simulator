#!/usr/bin/env python3
# coding=utf-8

from copy import copy, deepcopy
from functools import reduce
import pickle
from PySide.QtCore import QModelIndex, QPoint, QPointF, Qt, QTimer
from PySide.QtGui import (
    QCursor, QImage, QInputDialog, QGraphicsItem, QGraphicsScene,
    QGraphicsSimpleTextItem, QGraphicsView, QMenu, QStandardItemModel)
from .graphicitem import CircuitItem, PlugItem, WireItem
from .selectionoptions import SelectionOptions
from .toolbox import ToolBox
from .util import closestGridPoint, distance, filePath, GRIDSIZE
from engine.circuits import JKFlipFlop, RSFlipFlop
from engine.clock import Clock, ClockThread
from engine.simulator import Circuit, Plug
import engine

from engine.gates import *


class MainView(QGraphicsView):
    """Graphic representation of a user created circuit schematic."""

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        self.setAcceptDrops(True)       # Accept dragged items.
        self.setMouseTracking(True)     # Allow mouseover effects.
        self.setDragMode(QGraphicsView.RubberBandDrag)  # rubber select
        self.setScene(QGraphicsScene(parent))
        self.isDrawing = False          # user currently not drawing
        self.mainCircuit = Circuit("Main", None)
        self.timer = QTimer()
        """A timer for forcing redraws."""
        self.timer.setInterval(200)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.setItemsInGrid)
        self.copyBuffer = None
        """A buffer for ctrl-c, ctrl-v copy operations."""
        self.clockPlug = None

    def batchRename(self):
        """Experimental function to rename multiple items at once."""
        sel = self.scene().selectedItems()
        if (
                not all([isinstance(i, sel[0].__class__) for i in sel])
                or (isinstance(sel[0].data, Plug)
                    and not all([
                        i.data.isInput == sel[0].data.isInput for i in sel]))):
            print("Error")
            return
        ret = QInputDialog.getText(self, "Set prefix", "Prefix :")
        if ret[1] and len(ret[0]):
            for i in self.scene().selectedItems():
                i.data.generate_name(None, ret[0])
                i.setupPaint()
        self.parent().optionsDock.widget().updateOptions()

    def clearCircuit(self):
        """Clears every item from the circuit designer."""
        for i in self.scene().items():
            # https://bugreports.qt-project.org/browse/PYSIDE-252
            if not isinstance(i, QGraphicsSimpleTextItem):
                self.scene().removeItem(i)
        if self.bgClockThread:
            self.bgClockThread.stop()
        self.mainCircuit.clear()

    def clockUpdate(self):
        """Updates the view at each clock tick."""
        for item in self.scene().items():
            if isinstance(item, PlugItem) or isinstance(item, WireItem):
                item.setupPaint()

    def closeEvent(self, e):
        """Overload in order to kill the clock thread."""
        if self.bgClockThread is not None:
            self.bgClockThread.exit()

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
                if isinstance(item.data, Clock):
                    thread = item.data.clkThread
                    if thread.paused:
                        menu.addAction(
                            self.str_startClock, lambda: thread.unpause())
                    else:
                        menu.addAction(
                            self.str_pauseClock, lambda: thread.pause())
                menu.addAction(self.str_setName, lambda: self.getNewName(item))
                if item.data.isInput:
                    menu.addAction(
                        str(item.data.value), item.setAndUpdate)
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
                getattr(engine.gates, name + 'Gate')(None, self.mainCircuit))
        elif name == 'RSFlipFlop':
            item = CircuitItem(RSFlipFlop(None, self.mainCircuit))
        elif name == 'JKFlipFlop':
            item = CircuitItem(JKFlipFlop(None, self.mainCircuit))
        elif name == self.str_I:
            item = PlugItem(Plug(True, None, self.mainCircuit))
        elif name == self.str_O:
            item = PlugItem(Plug(False, None, self.mainCircuit))
        elif name == self.str_Clock:
            if not self.clockPlug:
                self.clockPlug = Clock(self.mainCircuit)
                self.clockPlug.clkThread.set_extern(self.clockUpdate)
                item = PlugItem(self.clockPlug)
            else:
                self.write(self.str_onlyOneClock)
        elif model.item(0, 1).text() == 'user':
            c = Circuit(None, self.mainCircuit)
            f = open(filePath('user/') + name + '.crc', 'rb')
            children = pickle.load(f)
            f.close()
            for child in children:
                if isinstance(child[0], Plug):
                    child[0].owner = c
                    if child[0].isInput:
                        c.inputList.append(child[0])
                    else:
                        c.outputList.append(child[0])
                elif isinstance(child[0], Circuit):
                    child[0].owner = c
                    c.circuitList.append(child[0])
            c.category = name
            item = CircuitItem(c)
        if item:
            # Fixes the default behaviour of centering the first
            # item added to scene.
            if not len(self.scene().items()):
                self.scene().setSceneRect(0, 0, 1, 1)
            else:
                self.scene().setSceneRect(0, 0, 0, 0)
            self.scene().addItem(item)
            item.setupPaint()
            item.setPos(
                closestGridPoint(item.mapFromScene(self.mapToScene(e.pos()))))
            for i in self.scene().selectedItems():
                i.setSelected(False)
            item.setSelected(True)
            self.timer.start()

    def fillIO(self):
        """Experimental function to add as many global I/Os as still needed
        by the main circuit.
        """
        for item in self.scene().items():
            if isinstance(item, CircuitItem):
                pos = item.pos()
                rot = item.rotation()
                circuit = item.data
                off = 0
                for input in circuit.inputList:
                    if not input.sourcePlug:
                        i = PlugItem(Plug(True, None, self.mainCircuit))
                        self.scene().addItem(i)
                        x = (
                            (pos.x() if not rot % 180 else pos.y())
                            - 4 * GRIDSIZE * (1 if not rot % 360 else -1))
                        y = (pos.y() if not rot % 180 else pos.x()) + off
                        i.setPos(x, y)
                        i.setRotation(rot)
                        off += 2 * GRIDSIZE
                off = 0
                for output in circuit.outputList:
                    if not len(output.destinationPlugs):
                        i = PlugItem(Plug(False, None, self.mainCircuit))
                        self.scene().addItem(i)
                        i.setPos(pos.x() + 100, pos.y() + off)
                        off += 30

    def getNewName(self, item):
        """Shows a dialog, and sets item name to user input."""
        # ret = tuple string, bool
        ret = QInputDialog.getText(self, self.str_setName, self.str_name)
        if ret[1] and item.data.setName(ret[0]):    # Not canceled.
            item.update()
        self.parent().optionsDock.widget().updateOptions()

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
                    self.mainCircuit.remove(item.data)
                elif isinstance(item, Plug):
                    self.mainCircuit.remove(item.data)
                elif (
                        isinstance(item, WireItem)
                        and item.data['endIO'] is not None):
                    item.data['startIO'].disconnect(item.data['endIO'])
                scene.removeItem(item)
        # <- ->, item rotation.
        elif e.key() == Qt.Key_Left or e.key() == Qt.Key_Right:
            self.rotateItems(90 if e.key() == Qt.Key_Right else -90)
        # L, left align and even spacing
        elif e.key() == Qt.Key_L:
            left = min([item.scenePos().x() for item in selection])
            sel = sorted(selection, key=lambda i: i.scenePos().y())
            sel[0].setPos(left, sel[0].scenePos().y())
            for i in range(1, len(sel)):
                sel[i].setPos(
                    left,
                    sel[i - 1].sceneBoundingRect().bottom() + 2 * GRIDSIZE)
        # R, right align and even spacing
        elif e.key() == Qt.Key_R:
            right = max([item.scenePos().x() for item in selection])
            sel = sorted(selection, key=lambda i: i.scenePos().y())
            sel[0].setPos(right, sel[0].scenePos().y())
            for i in range(1, len(sel)):
                sel[i].setPos(
                    right,
                    sel[i - 1].sceneBoundingRect().bottom() + 2 * GRIDSIZE)
        # T, top align and even spacing
        elif e.key() == Qt.Key_T:
            top = min([item.scenePos().y() for item in selection])
            sel = sorted(selection, key=lambda i: i.scenePos().x())
            sel[0].setPos(sel[0].scenePos().x(), top)
            for i in range(1, len(sel)):
                sel[i].setPos(
                    sel[i - 1].sceneBoundingRect().right() + 2 * GRIDSIZE,
                    top)
        # B, bottom align and even spacing
        elif e.key() == Qt.Key_B:
            bottom = max([item.scenePos().y() for item in selection])
            sel = sorted(selection, key=lambda i: i.scenePos().x())
            sel[0].setPos(sel[0].scenePos().x(), bottom)
        # Ctrl-C, copy
        elif e.key() == Qt.Key_C and e.nativeModifiers() == 4:
            self.copyBuffer = copy(selection)
        # Ctrl-V, paste
        elif e.key() == Qt.Key_V and e.nativeModifiers() == 4:
            memo = {}
            for item in self.copyBuffer:
                if isinstance(item, PlugItem):
                    dc = deepcopy(item.data, memo)
                    self.mainCircuit.add(dc)
                    dc.generate_name(None)
                    i = PlugItem(dc)
                elif isinstance(item, CircuitItem):
                    dc = deepcopy(item.data, memo)
                    self.mainCircuit.add(dc)
                    dc.generate_name()
                    i = CircuitItem(dc)
                elif isinstance(item, WireItem):
                    dc = deepcopy(item.data, memo)
                    i = WireItem(dc['startIO'], dc['points'], dc['endIO'])
                self.scene().addItem(i)
                # TODO : +100 et pourquoi 100 et pas pi ou 5000?
                i.setPos(item.pos().x() + 100, item.pos().y() + 100)
                i.setRotation(item.rotation())
                i.setupPaint()
        for item in selection:
            item.setupPaint()

    def mouseMoveEvent(self, e):
        """Redraw CurrentWire; change cursor on mouseOver handles."""
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
                        item.setToolTip(handle.name)
                    self.setCursor(Qt.CursorShape.UpArrowCursor)
                    return
                elif isCircuit:
                    item.setToolTip(item.data.name)
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
        self.mouseEventStart = None
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if isinstance(item, CircuitItem) or isinstance(item, PlugItem):
                plug = item.handleAtPos(pos)
                if plug:
                    self.isDrawing = True
                    p = closestGridPoint(self.mapToScene(e.pos()))
                    self.currentWire = WireItem(plug, [p, p])
                    self.scene().addItem(self.currentWire)
                    return   # no super(), prevents dragging/selecting
                elif (
                        isinstance(item, PlugItem) and item.data.isInput
                        and e.modifiers() & Qt.AltModifier):
                    item.setAndUpdate()
                    return
            elif isinstance(item, WireItem):
                if item.handleAtPos(pos):
                    self.currentWire = item
                    self.isDrawing = True
                    return   # no super(), prevents dragging/selecting
        # Didn't click a handle? We wanted to drag or select
        super(MainView, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """Complete Wire segments. Connect Plugs."""
        # Ignore right-clicks.
        if e.buttons() == Qt.RightButton:
            super(MainView, self).mousePressEvent(e)
            return
        if self.isDrawing:
            self.currentWire.addPoint()
            self.isDrawing = False
            old = self.currentWire.zValue()
            self.currentWire.setZValue(-500000)  # to detect other wires
            item = self.itemAt(e.pos())
            self.currentWire.setZValue(old)
            if item:
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                if isinstance(item, CircuitItem) or isinstance(item, PlugItem):
                    plug = item.handleAtPos(pos)
                    if (plug and
                            self.currentWire.handleAtPos(
                                self.currentWire.mapFromScene(
                                    self.mapToScene(e.pos())))):
                        if not self.currentWire.connect(plug):
                            self.currentWire.revert()
                        return
                elif (
                        isinstance(item, WireItem)
                        and item != self.currentWire and not item.complete):
                    if not self.currentWire.connect(item.data['startIO']):
                        self.currentWire.revert()
                    else:
                        p = self.currentWire.data['points'][-1]
                        points = item.data['points']
                        for i in range(len(points)):
                            a = points[i]
                            b = points[i + 1]
                            if (
                                    distance(a, p) + distance(p, b)
                                    == distance(a, b)):
                                points = points[0:i + 1]
                                points.reverse()
                                break
                        self.currentWire.data['points'].extend(
                            points)
                        self.scene().removeItem(item)
                        self.currentWire.setupPaint()
                        return
                elif isinstance(item, WireItem) and item.complete:
                    p = item.data['startIO']
                    p1 = item.data['endIO']
                    source = p if p1.sourcePlug == p else p1
                    if not self.currentWire.connect(source):
                        self.currentWire.revert()
                    #~ else: # test code
                        #~ print(self.currentWire.data)
            # Ugly hack to solve selection problems with multiple wireitems
            # on the same spot : the smallest area is selected.
            wires = sorted(
                [i for i in self.scene().items() if isinstance(i, WireItem)],
                key=
                lambda i: i.boundingRect().width() * i.boundingRect().height())
            for i in range(len(wires)):
                wires[i].setZValue(-i - 1)

            self.currentWire = None
        super(MainView, self).mouseReleaseEvent(e)

    def rotateItems(self, angle):
        """Rotates the current selection around its gravity center."""
        grp = self.scene().createItemGroup(self.scene().selectedItems())
        br = grp.sceneBoundingRect()
        grp.setTransformOriginPoint(
            br.left() + br.width() / 2, br.top() + br.height() / 2)
        grp.setRotation(grp.rotation() + angle)
        self.scene().destroyItemGroup(grp)
        # The item group doesn't transfer its rotation to its children
        # .setRotation() sets it correctly but rotates the item
        # .rotate() rotates the item back without setting it
        # rotate is deprecated, so this is far from ideal
        for item in self.scene().selectedItems():
            item.setRotation((item.rotation() + angle) % 360)
            item.rotate(-angle)

    def setItemsInGrid(self):
        """Correcting items pos to fit on the grid."""
        for item in self.scene().items():
            item.setPos(closestGridPoint(item.pos()))

    def write(self, message):
        """Briefly display a log WARNING."""
        scene = self.scene()
        msg = scene.addText(message)
        QTimer.singleShot(1500, lambda: scene.removeItem(msg))
