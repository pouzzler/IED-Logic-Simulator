#!/usr/bin/env python3
# coding=utf-8

import os
from math import atan2, pi, pow, sqrt


from PySide.QtCore import QPointF, QRectF, Qt
from PySide.QtGui import (QFont, QGraphicsItem, QGraphicsPathItem, 
    QImage, QPainterPath, QPen, QStyle)
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


class PlugItem(QGraphicsPathItem, Plug):
    """We represent an I pin as a graphic square path,
    and a O pin as a circle.
    """

    LARGE_DIAMETER = 25
    SMALL_DIAMETER = 5

    def __init__(self, isInput, parent):
        super(PlugItem, self).__init__()
        Plug.__init__(self, isInput, None, parent)
        # Creating a plug from our engine
        parent.add_plug(self)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        path = QPainterPath()
        if isInput:
            path.addEllipse(0, 0, self.LARGE_DIAMETER, self.LARGE_DIAMETER)
        else:
            path.addRect(0, 0, self.LARGE_DIAMETER, self.LARGE_DIAMETER)
        path.addEllipse(
            self.LARGE_DIAMETER + 1,
            (self.LARGE_DIAMETER - self.SMALL_DIAMETER) / 2,
            self.SMALL_DIAMETER,
            self.SMALL_DIAMETER)
        self.setPath(path)
        # This path is needed at each mouse over event, to check if
        # the mouse is over a pin. We save it as an instance field,
        # rather than recreate it at each event.
        self.pinPath = QPainterPath()
        self.pinPath.addEllipse(
            self.LARGE_DIAMETER - self.SMALL_DIAMETER,
            self.LARGE_DIAMETER / 2 - self.SMALL_DIAMETER,
            self.SMALL_DIAMETER * 2,
            self.SMALL_DIAMETER * 2)

    def handleAtPos(self, pos):
        return self if self.pinPath.contains(pos) else None

    def __getnewargs__(self):
        return (self.isInput, self.owner)


class CircuitItem(QGraphicsItem):
    """Should represent any sub-item of the circuit, ie. circuits, gates,
    inputs, outputs and wires."""

    ioH = 10
    ioW = 20
    radius = 2.5

    def __init__(self, circuitClass, owner):
        super(CircuitItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        imgDir = os.path.dirname(os.path.realpath(__file__)) + '/icons/'
        self.item = owner.add_circuit(circuitClass)
        self.image = QImage(imgDir + circuitClass.__name__ + '.png')
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
        self.imgOff = 0 if self.maxH == self.imgH else (self.maxH - self.imgH) / 2.
        self.inOff = 0 if self.maxH == self.inH else (self.maxH - self.inH) / 2.
        self.outOff = 0 if self.maxH == self.outH else (self.maxH - self.outH) / 2.
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

    def boundingRect(self):
        return QRectF(
            0,
            0,
            4 * self.radius + 2 * self.ioW + self.imgW,
            self.maxH)

    def paint(self, painter, option, widget):
        """Drawing the i/o pins 'by hand', the handles from the saved
        collision detection paths, and pasting a png file for the body
        of the gate/circuit.
        """
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
        # Apparently the default selection box doesn't work with custom 
        # QGraphicsItems
        if option.state & QStyle.State_Selected:
            pen = QPen(Qt.black, 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def handleAtPos(self, pos):
        for i in range(len(self.inputPaths)):
            if self.inputPaths[i].contains(pos):
                return self.item.inputList[i]
        for i in range(len(self.outputPaths)):
            if self.outputPaths[i].contains(pos):
                return self.item.outputList[i]

    def toggleNameVisibility(self):
        self.showName = not self.showName
        self.initPath()


class CircuitItemOld(QGraphicsPathItem):
    """We represent a circuit or logic gate as a graphic path."""

    IO_HEIGHT = 25   # pixels par E/S
    DIAMETER = 5     # pour les négations et les pins
    BODY_OFFSET = 5  # le corps dépasse des entrées extrêmes de 5 pixels
    I_LEFT = 5       # limite gauche des entrées
    I_RIGHT = 24     # limite droite des entrées
    O_LEFT = 50      # pareil pour les sorties
    O_RIGHT = 69
    XOR_LEFT = -3    # les index gauches des trois courbes possibles )) ) xor
    OR_LEFT = 2      # )  ) or
    AND_LEFT = 31    # |  ) and
    ARC_BOX = 18     # la largeur du rectangle dans lequel l'arc s'inscrit

    def __init__(self, circuitClass, parent):
        super(CircuitItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # Creating a circuit from our engine, using dynamic class lookup.
        self.circuit = parent.add_circuit(circuitClass)
        self.showName = True
        self.initPath()

    def initPath(self):
        # Getting some model values useful for the drawing.
        nInputs = self.circuit.nb_inputs()
        nOutputs = self.circuit.nb_outputs()
        # Some graphical values and offsets useful for the drawing.
        offset = self.IO_HEIGHT * abs(nInputs - nOutputs) / 2.
        height = max(nInputs, nOutputs)
        if nInputs > nOutputs:
            self.oOffset = offset + self.BODY_OFFSET
            self.iOffset = self.BODY_OFFSET
        else:
            self.oOffset = self.BODY_OFFSET
            self.iOffset = offset + self.BODY_OFFSET
        path = QPainterPath()
        if self.showName:
            path.addText(
                0, 0, QFont("Times", 8, QFont.Bold), self.circuit.name)
        # Drawing inputs.
        for i in range(nInputs):
            path.addEllipse(
                0, i * self.IO_HEIGHT + self.iOffset + self.BODY_OFFSET,
                self.DIAMETER, self.DIAMETER)
            path.moveTo(
                self.I_LEFT,
                i * self.IO_HEIGHT + self.iOffset + self.BODY_OFFSET +
                self.DIAMETER / 2.)
            path.lineTo(
                self.I_RIGHT, i * self.IO_HEIGHT + self.iOffset +
                self.BODY_OFFSET + self.DIAMETER / 2.)
        # Drawing the little circle implying negation.
        if self.circuit.__class__.__name__ in [
                'NandGate', 'NotGate', 'NorGate', 'XnorGate']:
            path.addEllipse(
                self.O_LEFT, height * self.IO_HEIGHT / 2. - self.DIAMETER / 2.,
                self.DIAMETER, self.DIAMETER)
        #Drawing outputs.
        for i in range(nOutputs):
            path.addEllipse(
                self.O_RIGHT + 1, i * self.IO_HEIGHT + self.oOffset +
                self.BODY_OFFSET, self.DIAMETER, self.DIAMETER)
            self.left = (
                self.O_LEFT + self.DIAMETER
                if self.circuit.__class__.__name__ in [
                    'NandGate', 'NotGate', 'NorGate', 'XnorGate']
                else self.O_LEFT)
            path.moveTo(
                self.left, i * self.IO_HEIGHT + self.oOffset +
                self.BODY_OFFSET + self.DIAMETER / 2.)
            path.lineTo(
                self.O_RIGHT, i * self.IO_HEIGHT + self.oOffset +
                self.BODY_OFFSET + self.DIAMETER / 2.)
        # Vertical line for these gates.
        if self.circuit.__class__.__name__ in [
                'NandGate', 'NotGate', 'AndGate']:
            path.moveTo(self.I_RIGHT + 1, 0)
            path.lineTo(self.I_RIGHT + 1, height * self.IO_HEIGHT)
        if self.circuit.__class__.__name__ == 'NotGate':
            path.lineTo(self.O_LEFT - 1, height * self.IO_HEIGHT / 2)
        elif self.circuit.__class__.__name__ in ['XorGate', 'XnorGate']:
            path.moveTo(self.XOR_LEFT + self.ARC_BOX, 0)
            path.arcTo(
                self.XOR_LEFT, 0, self.ARC_BOX, height * self.IO_HEIGHT,
                90, -180)
        if self.circuit.__class__.__name__ in [
                'OrGate', 'NorGate', 'XorGate', 'XnorGate']:
            path.moveTo(self.OR_LEFT + self.ARC_BOX, 0)
            path.arcTo(
                self.OR_LEFT, 0, self.ARC_BOX, height * self.IO_HEIGHT,
                90, -180)
        if self.circuit.__class__.__name__ in [
                'AndGate', 'NandGate', 'OrGate',
                'NorGate', 'XorGate', 'XnorGate']:
            path.lineTo(self.AND_LEFT,  height * self.IO_HEIGHT)
            path.arcTo(
                self.AND_LEFT,  0, self.ARC_BOX, height * self.IO_HEIGHT,
                -90, 180)
        path.closeSubpath()
        self.setPath(path)
        # These paths are needed at each mouse over event, to check if
        # the mouse is over a pin. We save them as an instance field,
        # rather than recreate them at each event.
        self.inputPaths = []
        self.outputPaths = []
        for i in range(self.circuit.nb_inputs()):
            path = QPainterPath()
            path.addEllipse(
                - self.DIAMETER, i * self.IO_HEIGHT + self.iOffset +
                self.BODY_OFFSET - self.DIAMETER, self.DIAMETER * 3,
                self.DIAMETER * 3)
            self.inputPaths.append(path)
        for i in range(self.circuit.nb_outputs()):
            path = QPainterPath()
            path.addEllipse(
                self.O_RIGHT + 1 - self.DIAMETER, i * self.IO_HEIGHT +
                self.oOffset + self.BODY_OFFSET - self.DIAMETER,
                self.DIAMETER * 3, self.DIAMETER * 3)
            self.outputPaths.append(path)

    def handleAtPos(self, pos):
        for i in range(self.circuit.nb_inputs()):
            if self.inputPaths[i].contains(pos):
                return self.circuit.inputList[i]
        for i in range(self.circuit.nb_outputs()):
            if self.outputPaths[i].contains(pos):
                return self.circuit.outputList[i]

    def toggleNameVisibility(self):
        self.showName = not self.showName
        self.initPath()
