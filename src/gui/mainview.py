#!/usr/bin/env python3
# coding=utf-8


from PySide import QtGui, QtCore
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .graphicitem import CircuitItem, IOItem
from engine.simulator import Circuit
from .settings import configFile


mainCircuit = Circuit("Main_Circuit")

class Wire(QtGui.QGraphicsPathItem):
    
    def __init__(self, startIO, p1):
        super(Wire, self).__init__()
        self.startIO = startIO
        self.points = [p1, p1]
        
    def moveLastPoint(self, endPoint):
        self.points[-1] = endPoint
        path = QtGui.QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        path.addEllipse(self.points[-1], 10, 10)
        self.setPath(path)
    
    def addPoint(self, point):
        self.points.append(point)

class MainView(QtGui.QGraphicsView):
    """A graphic view representing a circuit schematic, as created by
    the user. This view manages most user interaction, in particular:
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
        self.graphScene = QtGui.QGraphicsScene(parent)
        self.setScene(self.graphScene)
        self.isDrawing = False
        
    def setName(self, item):
        # ret = tuple string, bool (false when the dialog is dismissed)
        ret = QtGui.QInputDialog.getText(
            self,
            u'Set name',
            u'Enter a name for this item:')
        if ret[1] and len(ret[0]):
            item.name = ret[0]

    def toggleValue(self, item):
        item.set(not item.value)

    def contextMenuEvent(self, e):
        """Pops a contextual menu up on right-clicks"""
        item = self.itemAt(e.pos())
        if isinstance(item, CircuitItem) or isinstance(item, IOItem):
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            ioatpos = item.IOAtPos(pos)
            if ioatpos:
                item = ioatpos
            elif isinstance(item, CircuitItem):
                item = item.circuit
            menu = QtGui.QMenu(self)
            menu.addAction("Set name", lambda: self.setName(item))
            if ioatpos and ioatpos.owner == mainCircuit and ioatpos.isInput:
                menu.addAction(str(item.value), lambda: self.toggleValue(item))
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
        model = QtGui.QStandardItemModel()
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
            #~ QtGui.QTransform().translate(x, y).rotate(-90).translate(y, x))
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
                    self.currentWire = Wire(ioatpos, e.pos())
                    self.scene().addItem(self.currentWire)
                    # No super() processing, thus no dragging/selecting.
                    return
        # Didn't click an I/O? We wanted to drag or select the circuit.
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
            self.currentWire.addPoint(e.pos())
        super(MainView, self).mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        """Changes the cursor shape when the mouse hovers over an
        input or output pin.
        """
        if self.isDrawing:
            self.currentWire.moveLastPoint(e.pos())
        else:
            item = self.itemAt(e.pos())
            if item:
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                    ioatpos = item.IOAtPos(pos)
                    if ioatpos:
                        self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                        return
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super(MainView, self).mouseMoveEvent(e)

    #~ def mousePressEvent(self, e):
        #~ """When the mouse is pressed over a portion of a graphic item
        #~ that represents an engine.simulator.Plug, that Plug is appended
        #~ to self.connectionData.
        #~ """
        #~ # Reserve right-clicks for contextual menus.
        #~ if e.buttons() == QtCore.Qt.RightButton:
            #~ super(MainView, self).mousePressEvent(e)
            #~ return
        #~ self.connStart = None
        #~ self.connEnd = None
        #~ item = self.itemAt(e.pos())
        #~ if item:
            #~ pos = item.mapFromScene(self.mapToScene(e.pos()))
            #~ if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                #~ ioatpos = item.IOAtPos(pos)
                #~ if ioatpos:
                    #~ self.connStart = ioatpos
                    #~ # No super() processing, thus no dragging/selecting.
                    #~ return
        #~ # Didn't click an I/O? We wanted to drag or select the circuit.
        #~ super(MainView, self).mousePressEvent(e)
#~ 
    #~ def mouseReleaseEvent(self, e):
        #~ """When the mouse is released over an I/O, and was previously
        #~ pressed over another I/O, if one is an input, and the other an
        #~ output, a connection will be created between the two of them.
        #~ """
        #~ # Ignore right-clicks.
        #~ if e.buttons() == QtCore.Qt.RightButton:
            #~ super(MainView, self).mousePressEvent(e)
            #~ return
        #~ if self.connStart:
            #~ item = self.itemAt(e.pos())
            #~ if item:
                #~ pos = item.mapFromScene(self.mapToScene(e.pos()))
                #~ if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                    #~ ioatpos = item.IOAtPos(pos)
                    #~ if ioatpos:
                        #~ self.connEnd = ioatpos
        #keeping old drawing code here
                #~ origin = item.mapToScene(
                    #~ item.I_LEFT, i * item.IO_HEIGHT + item.iOffset
                    #~ + item.BODY_OFFSET + item.DIAMETER / 2.)
                #~ end = self.connectionData[0].mapToScene(
                    #~ self.connectionData[0].left,
                    #~ self.connectionData[2] *
                    #~ self.connectionData[0].IO_HEIGHT
                    #~ + self.connectionData[0].oOffset
                    #~ + self.connectionData[0].BODY_OFFSET
                    #~ + self.connectionData[0].DIAMETER / 2.)
                #~ line = QtCore.QLineF(origin, end)
                #~ self.scene().addLine(line)
                #~ item.circuit.inputList[i].connect(
                    #~ self.connectionData[1])
                #~ return

                #~ origin = self.connectionData[0].mapToScene(
                    #~ self.connectionData[0].I_LEFT,
                    #~ self.connectionData[2] *
                    #~ self.connectionData[0].IO_HEIGHT
                    #~ + self.connectionData[0].iOffset
                    #~ + self.connectionData[0].BODY_OFFSET +
                    #~ self.connectionData[0].DIAMETER / 2.)
                #~ end = item.mapToScene(
                    #~ item.left, i * item.IO_HEIGHT + item.oOffset +
                    #~ item.BODY_OFFSET + item.DIAMETER / 2.)
                #~ line = QtCore.QLineF(origin, end)
                #~ self.scene().addLine(line)
                #~ item.circuit.inputList[i].connect(
                    #~ self.connectionData[1])
                #~ return
        #~ if (
                #~ not self.connStart
                #~ or not self.connEnd
                #~ or self.connStart == self.connEnd):
            #~ super(MainView, self).mouseReleaseEvent(e)
            #~ return
        #~ elif (
                #~ self.connStart.owner == mainCircuit
                #~ and self.connEnd.owner == mainCircuit
                #~ and self.connStart.isInput == self.connEnd.isInput):
            #~ self.toast(
                #~ "Don't connect two global " +
                #~ ("inputs" if self.connStart.isInput else "outputs"))
            #~ return
        #~ elif (
                #~ self.connStart.owner != mainCircuit
                #~ and self.connEnd.owner != mainCircuit
                #~ and self.connStart.isInput == self.connEnd.isInput):
            #~ self.toast(
                #~ "Don't connect two circuit " +
                #~ ("inputs" if self.connStart.isInput else "outputs"))
            #~ return
        #~ elif ((
                #~ (self.connStart.owner != mainCircuit
                    #~ and self.connEnd.owner == mainCircuit)
                #~ or (self.connStart.owner == mainCircuit
                    #~ and self.connEnd.owner != mainCircuit))
                #~ and self.connStart.isInput != self.connEnd.isInput):
            #~ a = "local " if self.connStart.owner != mainCircuit else "global "
            #~ b = "input" if self.connStart.isInput else "output"
            #~ c = "global " if a == "local " else "local "
            #~ d = "output" if b == "inputs" else "input"
            #~ self.toast("Don't connect a " + a + b + " with a " + c + d)
            #~ return
        #~ else:
            #~ self.connStart.connect(self.connEnd)
        #~ super(MainView, self).mouseReleaseEvent(e)

    #~ def mouseMoveEvent(self, e):
        #~ """Changes the cursor shape when the mouse hovers over an
        #~ input or output pin.
        #~ """
        #~ item = self.itemAt(e.pos())
        #~ if item:
            #~ pos = item.mapFromScene(self.mapToScene(e.pos()))
            #~ if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                #~ ioatpos = item.IOAtPos(pos)
                #~ if ioatpos:
                    #~ self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                    #~ return
        #~ self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        #~ super(MainView, self).mouseMoveEvent(e)

    def toast(self, message):
        """Displays a short-lived informative message."""
        scene = self.scene()
        toast = scene.addText(message)
        QtCore.QTimer.singleShot(1500, lambda: scene.removeItem(toast))
