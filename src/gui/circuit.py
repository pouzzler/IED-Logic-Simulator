#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore

class Plug():
    def __init__(self, parent, isInput):
        self.parent = parent
        self.isInput = isInput

class Circuit(QtGui.QGraphicsPathItem, QtCore.QObject):
    """Un circuit est représenté par un QGraphicsPathItem. 
    TODO: en créant les E/S comme objets indépendants, et en faisant des
    itemGroups()?"""
    
    ioHeight = 25   # pixels par E/S
    diameter = 5    # pour les négations et les pins
    bodyOffset = 5  # le corps dépasse des entrées extrêmes de 5 pixels
    iLeft = 5       # limite gauche des entrées
    iRight = 24     # limite droite des entrées
    oLeft = 50      # pareil pour les sorties
    oRight = 69
    xorLeft = -3    # les index gauches des trois courbes possibles )) ) xor
    orLeft = 2      # )  ) or
    andLeft = 31    # |  ) and
    arcBox = 18     # la largeur du rectangle dans lequel l'arc s'inscrit

    requestConnection = QtCore.Signal(list)
    
    def __init__(self, inputs, outputs, gate):
        super(Circuit, self).__init__()
        QtCore.QObject.__init__(self)
        self.nInputs = inputs
        self.nOutputs = outputs
        self.inputList = []
        self.outputList = []
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)     # on peut déplacer
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)  # et sélectionner
        offset = self.ioHeight * abs(self.nInputs - self.nOutputs) / 2.
        height = max(self.nInputs, self.nOutputs)
        if self.nInputs > self.nOutputs:
            self.oOffset = offset + self.bodyOffset
            self.iOffset = self.bodyOffset
        else:
            self.oOffset = self.bodyOffset
            self.iOffset = offset + self.bodyOffset
        path = QtGui.QPainterPath()
        # On crée les entrées, et on les représente
        for i in range(self.nInputs):     
            self.inputList.append(Plug(self, True))          
            path.addEllipse(
                0, i * self.ioHeight + self.iOffset + self.bodyOffset,
                self.diameter, self.diameter)
            path.moveTo(
                self.iLeft,
                i * self.ioHeight + self.iOffset + self.bodyOffset +
                self.diameter / 2.)
            path.lineTo(
                self.iRight, i * self.ioHeight + self.iOffset +
                self.bodyOffset + self.diameter / 2.)
        # le cercle représentant la négation
        if gate in ['Nand', 'Not', 'Nor', 'Xnor']:
            path.addEllipse(
                self.oLeft, height * self.ioHeight / 2. - self.diameter / 2.,
                self.diameter, self.diameter)

        for i in range(self.nOutputs):               # les pins de sortie
            self.outputList.append(Plug(self, False))    
            path.addEllipse(
                self.oRight + 1, i * self.ioHeight + self.oOffset +
                self.bodyOffset, self.diameter, self.diameter)
            left = (
                self.oLeft + self.diameter
                if gate in ['Nand', 'Not', 'Nor', 'Xnor']
                else self.oLeft)
            path.moveTo(
                left, i * self.ioHeight + self.oOffset +
                self.bodyOffset + self.diameter / 2.)
            path.lineTo(
                self.oRight, i * self.ioHeight + self.oOffset +
                self.bodyOffset + self.diameter / 2.)

        if gate in ['Nand', 'Not', 'And']:           # la ligne verticale
            path.moveTo(self.iRight + 1, 0)
            path.lineTo(self.iRight + 1, height * self.ioHeight)
        if gate == 'Not':
            path.lineTo(self.oLeft - 1, height * self.ioHeight / 2)
        elif gate in ['Xor', 'Xnor']:
            path.moveTo(self.xorLeft + self.arcBox, 0)
            path.arcTo(
                self.xorLeft, 0, self.arcBox, height * self.ioHeight, 90, -180)
        if gate in ['Or', 'Nor', 'Xor', 'Xnor']:
            path.moveTo(self.orLeft + self.arcBox, 0)
            path.arcTo(
                self.orLeft, 0, self.arcBox, height * self.ioHeight, 90, -180)
        if gate in ['And', 'Nand', 'Or', 'Nor', 'Xor', 'Xnor']:
            path.lineTo(self.andLeft,  height * self.ioHeight)
            path.arcTo(
                self.andLeft,  0, self.arcBox, height * self.ioHeight,
                -90, 180)
        path.closeSubpath()
        self.setPath(path)

    def shape(self):
        """Renvoie le rectangle englobant le chemin plutôt que le chemin,
        afin de pouvoir cliquer n'importe ou pour sélectionner."""
        path = QtGui.QPainterPath()
        rect = self.boundingRect()
        # TODO: on ne veut pas sélectionner notre objet mais cliquer une E/S
        path.addRect(rect.left(), rect.top(), rect.width(), rect.height())
        return path

    def mousePressEvent(self, e):
        """Pour détecter les clics dans les entrées/sorties"""
        for i in range(self.nInputs):
            path = QtGui.QPainterPath()
            path.addEllipse(
                - self.diameter, i * self.ioHeight + self.iOffset +
                self.bodyOffset - self.diameter, self.diameter * 3,
                self.diameter * 3)
            if path.contains(e.pos()):
                self.requestConnection.emit([self.inputList[i]])
                return
        for i in range(self.nOutputs):
            path = QtGui.QPainterPath()
            path.addEllipse(
                self.oRight + 1 - self.diameter, i * self.ioHeight +
                self.oOffset + self.bodyOffset - self.diameter,
                self.diameter * 3, self.diameter * 3)
            if path.contains(e.pos()):
                self.requestConnection.emit([self.outputList[i]])
                return
