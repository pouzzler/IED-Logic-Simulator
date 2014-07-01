#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from engine.simulator import Circuit

class Plug():
    """I/Os are not drawn as separate entities, for simplicity's sake :
    it is easier to drag one  gate than at least one input, one output,
    and a gate body synchroneously.

    They are still modeled separately, to adhere to the engine's model.
    """

    def __init__(self, parent, isinput):
        self.parent = parent
        self.isinput = isinput


class CircuitItem(QtGui.QGraphicsPathItem):
    """We represent a circuit or logic gate as a graphic path."""

    IO_HEIGHT = 25   # pixels par E/S
    DIAMETER = 5    # pour les négations et les pins
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
        self.nInputs = 1
        self.nOutputs = 1
        self.inputList = []
        self.outputList = []
        

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)     # on peut déplacer
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)  # et sélectionner
        offset = self.IO_HEIGHT * abs(self.nInputs - self.nOutputs) / 2.
        height = max(self.nInputs, self.nOutputs)
        if self.nInputs > self.nOutputs:
            self.oOffset = offset + self.BODY_OFFSET
            self.iOffset = self.BODY_OFFSET
        else:
            self.oOffset = self.BODY_OFFSET
            self.iOffset = offset + self.BODY_OFFSET
        path = QtGui.QPainterPath()
        # On crée les entrées, et on les représente
        for i in range(self.nInputs):
            self.inputList.append(Plug(self, True))
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
        # le cercle représentant la négation
        if gate in ['Nand', 'Not', 'Nor', 'Xnor']:
            path.addEllipse(
                self.O_LEFT, height * self.IO_HEIGHT / 2. - self.DIAMETER / 2.,
                self.DIAMETER, self.DIAMETER)

        for i in range(self.nOutputs):               # les pins de sortie
            self.outputList.append(Plug(self, False))
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

        if gate in ['Nand', 'Not', 'And']:           # la ligne verticale
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

    #~ def shape(self):
        #~ """Renvoie le rectangle englobant le chemin plutôt que le chemin,
        #~ afin de pouvoir cliquer n'importe ou pour sélectionner.
        #~ """
        #~ path = QtGui.QPainterPath()
        #~ rect = self.boundingRect()
        #~ path.addRect(rect.left(), rect.top(), rect.width(), rect.height())
        #~ return path
