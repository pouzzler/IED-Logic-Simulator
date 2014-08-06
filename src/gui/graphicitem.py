#!/usr/bin/env python3
# coding=utf-8

from math import atan2, pi, pow, sqrt
from PySide.QtCore import QPointF, QRectF, Qt, QTimer
from PySide.QtGui import (
    QBrush, QColor, QCursor, QFont, QGraphicsItem, QGraphicsPathItem,
    QGraphicsSimpleTextItem, QImage, QPainterPath, QPen, QStyle)
from .util import filePath
from engine.simulator import Circuit, Plug


class WireItem(QGraphicsPathItem):
    """Represents an electrical wire connecting two items."""

    radius = 5

    def __init__(self, startIO, pts, endIO=None):
        super(WireItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        self.startIO = startIO
        self.endIO = endIO
        # Duplicate the origin, for redraws during mouse moves
        self.points = (pts if isinstance(pts, list) else [pts, pts])
        # Wire handle hovering over a Plug, MainView.mouseMove will detect
        # correctly the Plug, not the wire handle.
        self.setZValue(-1)
        # Can the wire be modified (not complete)?
        self.complete = True if endIO else False

    def addPoint(self):
        """Duplicates the end point, for use as a moving point during moves."""
        self.points.append(self.points[-1])

    def connect(self, endIO):
        """Try to connect the end points of the Wire."""
        if self.startIO.connect(endIO):
            self.endIO = endIO
            self.complete = True    # Wire can't be modified anymore.
            self.setupPaint()
            return True
        return False

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?"""
        if not self.complete:
            path = QPainterPath()
            path.addEllipse(self.points[-1], self.radius, self.radius)
            return path.contains(pos)

    def moveLastPoint(self, endPoint):
        """Redraw the last, unfinished segment while the mouse moves."""
        sq2 = sqrt(2) / 2
        A = [[0, 1], [sq2, sq2], [1, 0], [sq2, -sq2],
            [0, -1], [-sq2, -sq2], [-1, 0], [-sq2, sq2]]
        x = self.points[-2].x()
        y = self.points[-2].y()
        L = sqrt(pow(endPoint.x() - x, 2) + pow(endPoint.y() - y, 2))
        angle = atan2(endPoint.x() - x, endPoint.y() - y)
        a = round(8 * angle / (2 * pi)) % 8
        self.points[-1] = QPointF(x + A[a][0] * L, y + A[a][1] * L)
        self.setupPaint()

    def setupPaint(self):
        """Draw the wire segments and handle."""
        path = QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        if not self.complete:   # An incomplete wire needs a handle
            path.addEllipse(self.points[-1], self.radius, self.radius)
        self.setPath(path)
        self.update()

    def removeLast(self):
        """Remove the last segment (user corrects user errors)."""
        if not self.complete:
            self.points = self.points[0:-2]
            if len(self.points) > 1:
                self.addPoint()
                self.setupPaint()
            else:
                self.scene().removeItem(self)


class PlugItem(QGraphicsPathItem):
    """Graphical wrapper around the engine Plug class."""

    bodyW = 30
    piNW = 10

    def __init__(self, isInput, owner):
        super(PlugItem, self).__init__()
        self.item = Plug(isInput, None, owner)
        self.showName = False
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.itemHasStopped)
        self.setAcceptsHoverEvents(True)
        self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        self.oldPos = QPointF(0, 0)
        # This path is needed at each mouse over event, to check if
        # the mouse is over a pin. We save it as an instance field,
        # rather than recreate it at each event.
        self.pinPath = QPainterPath()
        if isInput:
            self.pinPath.addEllipse(
                self.bodyW + 1, (self.bodyW - self.piNW) / 2,
                self.piNW, self.piNW)
        else:
            self.pinPath.addEllipse(
                0, (self.bodyW - self.piNW) / 2, self.piNW, self.piNW)
        f = QFont('Times', 12, 75)
        # Name and value text labels.
        self.name = QGraphicsSimpleTextItem(self)
        # that won't rotate when the PlugItem is rotated by the user.
        self.name.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.name.setText(self.item.name)
        self.name.setFont(f)
        self.value = QGraphicsSimpleTextItem(self)
        self.value.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        # Or else value would get the clicks, instead of the PlugItem.
        self.value.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.value.setFont(f)
        self.setupPaint()

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?
        Also return the Plug under this handle.
        """
        return self.item if self.pinPath.contains(pos) else None

    def itemChange(self, change, value):
        """Telling self to correct pos after timer expires."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.timer.start()  # Restart till we stop moving.
        return QGraphicsItem.itemChange(self, change, value)

    def itemHasStopped(self):
        """Correcting pos to fit on the grid."""
        newPos = QPointF(
            int(10 * round(self.pos().x() / 10)),
            int(10 * round(self.pos().y() / 10)))
        self.setPos(newPos)

    def setCategoryVisibility(self, isVisible):
        """MainView requires PlugItems to function like CircuitItems."""
        pass

    def setNameVisibility(self, isVisible):
        """Shows/Hide the item name in the graphical view."""
        self.showName = isVisible
        self.setupPaint()

    def setupPaint(self):
        """Offscreen rather than onscreen redraw (few changes)."""
        path = QPainterPath()
        if self.item.isInput:
            path.addEllipse(0, 0, self.bodyW, self.bodyW)
        else:
            path.addRect(
                self.piNW + 1, 0,
                self.bodyW, self.bodyW)
        path.addPath(self.pinPath)
        self.setPath(path)
        self.name.setVisible(self.showName)
        self.name.setText(self.item.name)
        br = self.mapToScene(self.boundingRect())
        w = self.boundingRect().width()
        h = self.boundingRect().height()
        realX = min([i.x() for i in br])
        realY = min([i.y() for i in br])
        self.name.setPos(self.mapFromScene(
            realX, realY + (w if self.rotation() % 180 else h) + 1))
        self.value.setText(str(int(self.item.value)))
        self.value.setPos(self.mapFromScene(realX + w / 3, realY + h / 3))
        self.value.setBrush(QColor('green' if self.item.value else 'red'))
        self.update()       # Force onscreen redraw after changes.


class CircuitItem(QGraphicsItem):
    """Graphical wrapper around the engine Circuit class."""

    textH = 12
    ioH = 10
    ioW = 20
    radius = 2.5

    def __init__(self, circuitClass, owner):
        super(CircuitItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.showName = True
        self.showCategory = False
        imgDir = filePath('icons/')
        self.item = owner.add_circuit(circuitClass)
        self.image = QImage(imgDir + circuitClass.__name__ + '.png')
        if not self.image:
            self.image = QImage(imgDir + 'Default.png')
            self.showCategory = True
        self.setupPaint()

    def boundingRect(self):
        """Qt requires overloading this when overloading QGraphicsItem."""
        H = self.maxH
        W = 4 * self.radius + 2 * self.ioW + self.imgW
        if self.showCategory:
            H = H + 2 * self.textH
        elif self.showName:
            H = H + self.textH
        return QRectF(0, 0, W, H)

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is? Return it."""
        for i in range(self.nIn):
            if self.inputPaths[i].contains(pos):
                return self.item.inputList[i]
        for i in range(self.nOut):
            if self.outputPaths[i].contains(pos):
                return self.item.outputList[i]

    def paint(self, painter, option, widget):
        """Draws the item."""
        # TEST CODE FOR FUTURE REWRITE
        #~ painter.drawImage(QRectF(0, 0, self.imgW, self.imgH), self.image)
        #~ self.ioH = 20
        #~ self.ioW = 15
        #~ self.radius = 5
        #~ n = self.item.nb_inputs()
        #~ for i in range(1 - int(n / 2), 2 + int(n / 2)):
            #~ if i != 1 or n % 2:
                #~ painter.drawLine(-self.ioW, i * self.ioH, 0, i * self.ioH)
                #~ painter.drawEllipse(
                    #~ -self.ioW - self.radius, i * self.ioH - self.radius / 2,
                    #~ self.radius, self.radius)
        #~ n = self.item.nb_outputs()
        #~ for i in range(1 - int(n / 2), 2 + int(n / 2)):
            #~ if i != 1 or n % 2:
                #~ painter.drawLine(
                    #~ self.imgW, i * self.ioH, self.imgW + self.ioW, i * self.ioH)
                #~ painter.drawEllipse(
                    #~ self.imgW + self.ioW, i * self.ioH - self.radius / 2,
                    #~ self.radius, self.radius)
        painter.setPen(QPen(QColor('black'), 2))
        for i in range(self.nIn):   # Handles drawn 'by hand'.
            painter.drawPath(self.inputPaths[i])
            painter.drawLine(
                2 * self.radius,
                i * self.ioH + self.inOff + self.radius,
                2 * self.radius + self.ioW,
                i * self.ioH + self.inOff + self.radius)
        painter.drawLine(
            2 * self.radius + self.ioW,
            self.inOff + self.radius,
            2 * self.radius + self.ioW,
            (self.nIn - 1) * self.ioH + self.inOff + self.radius)
        for i in range(self.nOut):
            painter.drawPath(self.outputPaths[i])
            painter.drawLine(
                2 * self.radius + self.ioW + self.imgW,
                i * self.ioH + self.outOff + self.radius,
                2 * self.radius + 2 * self.ioW + self.imgW,
                i * self.ioH + self.outOff + self.radius)
        painter.drawLine(
            2 * self.radius + self.ioW + self.imgW,
            self.outOff + self.radius,
            2 * self.radius + self.ioW + self.imgW,
            (self.nOut - 1) * self.ioH + self.outOff + self.radius)
        painter.drawImage(
            QRectF(
                2 * self.radius + self.ioW,
                self.imgOff,
                self.imgW,
                self.imgH),
            self.image)                 # Body drawn from a png.
        f = QFont('Times')              # Draw name & category.
        f.setPixelSize(self.textH)
        painter.setFont(f)
        if self.showName:
            painter.setPen(QPen(QColor('red')))
            painter.drawText(
                QPointF(0, self.maxH + self.textH),
                self.item.name)
        if self.showCategory:
            painter.setPen(QPen(QColor('green')))
            painter.drawText(
                QPointF(0, self.maxH + 2 * self.textH), (
                    self.item.category if self.item.category
                    else self.item.__class__.__name__))
        # Default selection box doesn't work; simple reimplementation.
        if option.state & QStyle.State_Selected:
            pen = QPen(Qt.black, 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def setCategoryVisibility(self, isVisible):
        """Show/Hide circuit category (mostly useful for user circuits)."""
        self.showCategory = isVisible
        self.setupPaint()

    def setNameVisibility(self, isVisible):
        """Shows/Hide the item name in the graphical view."""
        self.showName = isVisible
        self.setupPaint()

    def setNbInputs(self, nb):
        """Add/Remove inputs (for logical gates)."""
        if nb > self.item.nb_inputs():
            for x in range(nb - self.item.nb_inputs()):
                Plug(True, None, self.item)
        elif nb < self.item.nb_inputs():
            for x in range(self.item.nb_inputs() - nb):
                self.item.remove_input(self.item.inputList[0])
        self.setupPaint()

    def setupPaint(self):
        """Offscreen rather than onscreen redraw (few changes)."""
        self.nIn = self.item.nb_inputs()
        self.nOut = self.item.nb_outputs()
        # 3 sections with different heights must be aligned :
        self.imgH = self.image.size().height()   # central (png image)
        self.imgW = self.image.size().width()
        self.inH = (self.nIn - 1) * self.ioH + 2 * self.radius  # inputs
        self.outH = (self.nOut - 1) * self.ioH + 2 * self.radius    # outputs
        # therefore we calculate a vertical offset for each section :
        self.maxH = max(self.imgH, self.inH, self.outH)
        self.imgOff = (
            0 if self.maxH == self.imgH else (self.maxH - self.imgH) / 2.)
        self.inOff = (
            0 if self.maxH == self.inH else (self.maxH - self.inH) / 2.)
        self.outOff = (
            0 if self.maxH == self.outH else (self.maxH - self.outH) / 2.)
        # i/o mouseover detection. Create once, use on each mouseMoveEvent.
        self.inputPaths = []
        self.outputPaths = []
        for i in range(self.nIn):
            path = QPainterPath()
            path.addEllipse(
                0,
                i * self.ioH + self.inOff,
                2 * self.radius,
                2 * self.radius)
            self.inputPaths.append(path)
        for i in range(self.nOut):
            path = QPainterPath()
            path.addEllipse(
                2 * self.radius + 2 * self.ioW + self.imgW,
                i * self.ioH + self.outOff,
                2 * self.radius,
                2 * self.radius)
            self.outputPaths.append(path)
        self.prepareGeometryChange()
        self.update()       # Force onscreen redraw after changes.
