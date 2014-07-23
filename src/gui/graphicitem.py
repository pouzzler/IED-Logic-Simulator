#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from PySide.QtGui import (
    QFont, QGraphicsItem, QGraphicsPathItem, QPainterPath)
from engine.simulator import Circuit, Plug
import engine


class Wire(QGraphicsPathItem):

    RADIUS = 2.5

    def __init__(self, startIO, p1):
        super(Wire, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # Remembering the Plug where the Wire starts, for creating the
        # connection, when the last segment is drawn over another IO.
        self.startIO = startIO
        # The first point of our segments. The "moving point" used to
        # redraw during mouseMove events.
        self.points = [p1, p1]
        # We dont want't to catch the Wire handle when it is connected
        # to a Plug, this puts our item under the Plug, and itemAt()
        # will grab the Plug.
        self.setZValue(-1)

    def moveLastPoint(self, endPoint):
        """While dragging the mouse, redrawing the last segment."""
        self.points[-1] = endPoint
        self.redraw()

    def redraw(self):
        """We draw the segments between our array of points and a small
        handle circle on the last segment.
        """
        path = QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        path.addEllipse(self.points[-1], self.RADIUS, self.RADIUS)
        path.closeSubpath()
        self.setPath(path)

    def addPoint(self):
        """When a segment ends (on mouseRelease), we duplicate the last
        point, to be used as a moving point during the next mouseMove.
        """
        self.points.append(self.points[-1])

    def handleAtPos(self, pos):
        """We drag the end-segment when the user clicks the handle."""
        handlePath = QPainterPath()
        handlePath.addEllipse(self.points[-1], self.RADIUS, self.RADIUS)
        return handlePath.contains(pos)

    def removeLast(self):
        """We remove the last segment (when the user made an error and
        corrects it).
        """
        scene = self.scene()
        scene.removeItem(self)
        self.points = self.points[0:-2]
        if len(self.points) > 1:
            self.addPoint()
            self.redraw()
            scene.addItem(self)


class IOItem(QGraphicsPathItem, Plug):
    """We represent an I pin as a graphic square path,
    and a O pin as a circle.
    """

    LARGE_DIAMETER = 25
    SMALL_DIAMETER = 5

    def __init__(self, isInput, parent):
        super(IOItem, self).__init__()
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

    def IOAtPos(self, pos):
        return self if self.pinPath.contains(pos) else None


class CircuitItem(QGraphicsPathItem):
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

    def __init__(self, gate, parent):
        super(CircuitItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # Creating a circuit from our engine, using dynamic class lookup.
        self.circuit = parent.add_circuit(
            getattr(engine.gates, gate + "Gate")(parent))
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
        path.addText(0, 0, QFont(), self.circuit.name)
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
            'AndGate', 'NandGate', 'OrGate', 'NorGate', 'XorGate', 'XnorGate']:
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

    def IOAtPos(self, pos):
        for i in range(self.circuit.nb_inputs()):
            if self.inputPaths[i].contains(pos):
                return self.circuit.inputList[i]
        for i in range(self.circuit.nb_outputs()):
            if self.outputPaths[i].contains(pos):
                return self.circuit.outputList[i]

