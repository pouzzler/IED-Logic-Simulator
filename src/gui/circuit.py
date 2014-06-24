#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore

class circuit(QtGui.QGraphicsPathItem) :
  """Un circuit est représenté par un QGraphicsPathItem"""
  ioHeight = 25       # pixels par E/S
  diameter = 5        # pour les négations et les pins
  bodyOffset = 5      # le corps dépasse des entrées extrêmes de 5 pixels
  iLeft = 5           # limite gauche des entrées
  iRight = 24         # limite droite des entrées
  oLeft = 50          # pareil pour les sorties
  oRight = 69
  xorLeft = -3        # les index gauches des trois courbes possibles )) ) xor
  orLeft = 2          # )  ) or
  andLeft = 31        # |  ) and
  arcBox = 18         # la largeur du rectangle dans lequel l'arc s'inscrit
  def __init__(self, inputs, outputs, gate) :
    super(circuit, self).__init__()
    self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)     # on peut déplacer
    self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)  # et sélectionner
    self.nInputs = inputs
    self.nOutputs = outputs
    offset = self.ioHeight * abs(self.nInputs - self.nOutputs) / 2.
    height = max(self.nInputs, self.nOutputs)
    if self.nInputs > self.nOutputs :
      self.oOffset = offset + self.bodyOffset    # + 5 pour que le corps de la porte
      self.iOffset = self.bodyOffset             # dépasse un peu des E/S extrêmes
    else :
      self.oOffset = self.bodyOffset
      self.iOffset = offset + self.bodyOffset
    path = QtGui.QPainterPath()
    for i in range(self.nInputs) :                # les pins d'entrée
      path.addEllipse(0, i * self.ioHeight + self.iOffset + self.bodyOffset, self.diameter, self.diameter)
      path.moveTo(self.iLeft, i * self.ioHeight + self.iOffset + self.bodyOffset + self.diameter / 2.)
      path.lineTo(self.iRight, i * self.ioHeight + self.iOffset + self.bodyOffset + self.diameter / 2.)
      
    if gate in ['Nand', 'Not', 'Nor', 'Xnor'] :   # le cercle représentant la négation
      path.addEllipse(self.oLeft, height * self.ioHeight / 2. - self.diameter / 2., self.diameter, self.diameter)
      
    for i in range(self.nOutputs) :               # les pins de sortie
      path.addEllipse(self.oRight + 1, i * self.ioHeight + self.oOffset + self.bodyOffset, self.diameter, self.diameter)
      left = self.oLeft + self.diameter if gate in ['Nand', 'Not', 'Nor', 'Xnor'] else self.oLeft
      path.moveTo(left, i * self.ioHeight + self.oOffset + self.bodyOffset + self.diameter / 2.)
      path.lineTo(self.oRight, i * self.ioHeight + self.oOffset + self.bodyOffset + self.diameter / 2.)
  
    if gate in ['Nand', 'Not', 'And'] :           # la ligne verticale
      path.moveTo(self.iRight + 1, 0)
      path.lineTo(self.iRight + 1, height * self.ioHeight)
    if gate == 'Not' :
      path.lineTo(self.oLeft - 1, height * self.ioHeight / 2)
    elif gate in ['Xor', 'Xnor'] :
      path.moveTo(self.xorLeft + self.arcBox, 0)
      path.arcTo(self.xorLeft, 0, self.arcBox, height * self.ioHeight, 90, -180)
    if gate in ['Or', 'Nor', 'Xor', 'Xnor'] :
      path.moveTo(self.orLeft + self.arcBox, 0)
      path.arcTo(self.orLeft, 0, self.arcBox, height * self.ioHeight, 90, -180)
    if gate in ['And', 'Nand', 'Or', 'Nor', 'Xor', 'Xnor'] :
      path.lineTo(self.andLeft,  height * self.ioHeight)
      path.arcTo(self.andLeft,  0, self.arcBox, height * self.ioHeight, -90, 180)
    path.closeSubpath()
    self.setPath(path)

  def shape(self) :
    """Renvoie le rectangle englobant le chemin plutôt que le chemin,
    afin de pouvoir cliquer n'importe ou pour sélectionner."""
    path = QtGui.QPainterPath()
    rect = self.boundingRect()
    # TODO : on ne veut pas sélectionner notre objet mais cliquer une E/S
    path.addRect(rect.left(), rect.top(), rect.width(), rect.height())
    return path
    
  def mousePressEvent(self, e) :
    """Pour détecter les clics dans les entrées/sorties"""
    for i in range(self.nInputs) : 
      path = QtGui.QPainterPath()
      path.addEllipse(- self.diameter, i * self.ioHeight + self.iOffset + self.bodyOffset - self.diameter, self.diameter * 3, self.diameter * 3)
      if path.contains(e.pos()) :
        print "in " + str(i)
        return 
    for i in range(self.nOutputs) : 
      path = QtGui.QPainterPath()
      path.addEllipse(self.oRight + 1 - self.diameter, i * self.ioHeight + self.oOffset + self.bodyOffset - self.diameter, self.diameter * 3, self.diameter * 3)
      if path.contains(e.pos()) :
        print "out " + str(i)
        return 
