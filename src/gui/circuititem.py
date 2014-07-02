#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from engine.simulator import Circuit
import engine

class IO(QtGui.QGraphicsPathItem):
    """We represent an I pin as a graphic square path,
    and a O pin as a circle.
    """
    
    DIAMETER = 25
    
    def __init__(self, isInput):
        super(IO, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        # Creating a engine.simulator.Plug
        
        path = QtGui.QPainterPath()
        if isInput:
            path.addEllipse(0, 0, self.DIAMETER, self.DIAMETER)
        else:
            path.addRect(0,0, self.DIAMETER, self.DIAMETER)
        self.setPath(path)

class CircuitItem(QtGui.QGraphicsPathItem):
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

    def __init__(self, gate):
        super(CircuitItem, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        # Creating a circuit from our engine, using dynamic class lookup.
        self.circuit = getattr(engine.gates, gate + "Gate")(None)
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
        path = QtGui.QPainterPath()
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
        if gate in ['Nand', 'Not', 'Nor', 'Xnor']:
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
                if gate in ['Nand', 'Not', 'Nor', 'Xnor']
                else self.O_LEFT)
            path.moveTo(
                self.left, i * self.IO_HEIGHT + self.oOffset +
                self.BODY_OFFSET + self.DIAMETER / 2.)
            path.lineTo(
                self.O_RIGHT, i * self.IO_HEIGHT + self.oOffset +
                self.BODY_OFFSET + self.DIAMETER / 2.)
        # Vertical line for these gates.
        if gate in ['Nand', 'Not', 'And']:
            path.moveTo(self.I_RIGHT + 1, 0)
            path.lineTo(self.I_RIGHT + 1, height * self.IO_HEIGHT)
        if gate == 'Not':
            path.lineTo(self.O_LEFT - 1, height * self.IO_HEIGHT / 2)
        elif gate in ['Xor', 'Xnor']:
            path.moveTo(self.XOR_LEFT + self.ARC_BOX, 0)
            path.arcTo(
                self.XOR_LEFT, 0, self.ARC_BOX, height * self.IO_HEIGHT,
                90, -180)
        if gate in ['Or', 'Nor', 'Xor', 'Xnor']:
            path.moveTo(self.OR_LEFT + self.ARC_BOX, 0)
            path.arcTo(
                self.OR_LEFT, 0, self.ARC_BOX, height * self.IO_HEIGHT,
                90, -180)
        if gate in ['And', 'Nand', 'Or', 'Nor', 'Xor', 'Xnor']:
            path.lineTo(self.AND_LEFT,  height * self.IO_HEIGHT)
            path.arcTo(
                self.AND_LEFT,  0, self.ARC_BOX, height * self.IO_HEIGHT,
                -90, 180)
        path.closeSubpath()
        self.setPath(path)
