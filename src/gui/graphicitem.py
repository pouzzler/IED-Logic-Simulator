#!/usr/bin/env python3
# coding=utf-8

from os.path import dirname, realpath
from math import atan2, pi, pow, sqrt

from PySide.QtCore import QPointF, QRectF, Qt
from PySide.QtGui import (
    QBrush, QColor, QFont, QGraphicsItem, QGraphicsPathItem, QImage,
    QPainterPath, QPen, QStyle)
from engine.simulator import Circuit, Plug


class WireItem(QGraphicsPathItem):

    RADIUS = 2.5

    def __init__(self, startIO, p1):
        super(WireItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # Remembering the Plug where the WireItem starts, for creating the
        # connection, when the last segment is drawn over another IO.
        self.startIO = startIO
        # The first point of our segments. The "moving point" used to
        # redraw during mouseMove events.
        self.points = [p1, p1]
        # We dont want't to catch the WireItem handle when it is connected
        # to a Plug, this puts our item under the Plug, and itemAt()
        # will grab the Plug.
        self.setZValue(-1)
        self.complete = False

    def moveLastPoint(self, endPoint):
        """While dragging the mouse, redrawing the last segment."""
        sq2 = sqrt(2) / 2
        A = [[0, 1], [sq2, sq2], [1, 0], [sq2, -sq2],
            [0, -1], [-sq2, -sq2], [-1, 0], [-sq2, sq2]]
        x = self.points[-2].x()
        y = self.points[-2].y()
        L = sqrt(pow(endPoint.x() - x, 2) + pow(endPoint.y() - y, 2))
        angle = atan2(endPoint.x() - x, endPoint.y() - y)
        a = round(8 * angle / (2 * pi)) % 8
        self.points[-1] = QPointF(x + A[a][0] * L, y + A[a][1] * L)
        self.redraw()

    def redraw(self):
        """We draw the segments between our array of points and a small
        handle circle on the last segment.
        """
        self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        path = QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        if not self.complete:
            path.addEllipse(self.points[-1], self.RADIUS, self.RADIUS)
        self.setPath(path)

    def addPoint(self):
        """When a segment ends (on mouseRelease), we duplicate the last
        point, to be used as a moving point during the next mouseMove.
        """
        self.points.append(self.points[-1])

    def handleAtPos(self, pos):
        """We drag the end-segment when the user clicks the handle."""
        if self.complete:
            return
        path = QPainterPath()
        path.addEllipse(self.points[-1], self.RADIUS, self.RADIUS)
        return path.contains(pos)

    def removeLast(self):
        """We remove the last segment (when the user made an error and
        corrects it).
        """
        if self.complete:
            return
        scene = self.scene()
        scene.removeItem(self)
        self.points = self.points[0:-2]
        if len(self.points) > 1:
            self.addPoint()
            self.redraw()
            scene.addItem(self)

    def connect(self, endIO):
        if not self.startIO.connect(endIO):
            return False
        else:
            self.endIO = endIO
            self.complete = True
            self.redraw()
            return True


class PlugItem(QGraphicsPathItem):
    """Graphical wrapper around the engine Plug class."""

    LARGE_DIAMETER = 25
    SMALL_DIAMETER = 5
    textH = 12

    def __init__(self, isInput, owner):
        super(PlugItem, self).__init__()
        self.item = Plug(isInput, None, owner)
        owner.add_plug(self.item)
        self.showName = False
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # This path is needed at each mouse over event, to check if
        # the mouse is over a pin. We save it as an instance field,
        # rather than recreate it at each event.
        self.pinPath = QPainterPath()
        self.pinPath.addEllipse(
            self.LARGE_DIAMETER - self.SMALL_DIAMETER,
            self.LARGE_DIAMETER / 2 - self.SMALL_DIAMETER,
            self.SMALL_DIAMETER * 2,
            self.SMALL_DIAMETER * 2)
        self.setupPaint()

    def setupPaint(self):
        path = QPainterPath()
        if self.item.isInput:
            path.addEllipse(0, 0, self.LARGE_DIAMETER, self.LARGE_DIAMETER)
        else:
            path.addRect(0, 0, self.LARGE_DIAMETER, self.LARGE_DIAMETER)
        path.addEllipse(
            self.LARGE_DIAMETER + 1,
            (self.LARGE_DIAMETER - self.SMALL_DIAMETER) / 2,
            self.SMALL_DIAMETER,
            self.SMALL_DIAMETER)
        if self.showName:
            path.addText(
                QPointF(0, self.LARGE_DIAMETER + 1),
                QFont(),
                self.item.name)
        self.setPath(path)
        self.update()
        
        
    def handleAtPos(self, pos):
        return self.item if self.pinPath.contains(pos) else None

    def setNameVisibility(self, isVisible):
        self.showName = isVisible
        self.setupPaint()

    def setClassVisibility(self, isVisible):
        self.showCategory = isVisible
        self.setupPaint()


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
        imgDir = dirname(realpath(__file__)) + '/../../icons/'
        self.item = owner.add_circuit(circuitClass)
        self.image = QImage(imgDir + circuitClass.__name__ + '.png')
        self.showCategory = False
        if not self.image:
            self.image = QImage(imgDir + 'Default.png')
            self.showCategory = True
        self.showName = True
        self.setupPaint()

    def setupPaint(self):
        """Setting up long-lived variables that might still change,
        necessiting a redraw (ie. number of inputs, height & width...)
        """
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
        self.update()

    def boundingRect(self):
        H = self.maxH
        W = 4 * self.radius + 2 * self.ioW + self.imgW
        if self.showCategory:
            H = H + 2 * self.textH
        elif self.showName:
            H = H + self.textH
        return QRectF(0, 0, W, H)

    def paint(self, painter, option, widget):
        """Drawing the i/o pins 'by hand', the handles from the saved
        collision detection paths, and pasting a png file for the body
        of the gate/circuit.
        """
        painter.setPen(QPen(QColor('black'), 2))
        for i in range(self.nIn):
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
            self.image)
        f = QFont('Times')
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
                QPointF(0, self.maxH + 2 * self.textH),
                self.item.__class__.__name__)
        # Apparently the default selection box doesn't work with custom
        # QGraphicsItems
        if option.state & QStyle.State_Selected:
            pen = QPen(Qt.black, 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def handleAtPos(self, pos):
        for i in range(self.nIn):
            if self.inputPaths[i].contains(pos):
                return self.item.inputList[i]
        for i in range(self.nOut):
            if self.outputPaths[i].contains(pos):
                return self.item.outputList[i]

    def setNameVisibility(self, isVisible):
        self.showName = isVisible
        self.setupPaint()

    def setClassVisibility(self, isVisible):
        self.showCategory = isVisible
        self.setupPaint()

    def setNbInputs(self, nb):
        if nb > self.item.nb_inputs():
            for x in range(nb - self.item.nb_inputs()):
                self.item.add_input()
        elif nb < self.item.nb_inputs():
            for x in range(self.item.nb_inputs() - nb):
                self.item.remove_input(self.item.inputList[0])
        self.setupPaint()
