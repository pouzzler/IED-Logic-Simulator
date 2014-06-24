#!/usr/bin/env python
# coding=utf-8

import sys
from PySide import QtGui, QtCore
    
gates = ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']

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
  
class toolOptions(QtGui.QWidget) :
  """Contient des widgets permettant de modifier les paramètres 
  de l'objet sélectionné"""
  def __init__(self) :
    super(toolOptions, self).__init__()
    
    layout = QtGui.QVBoxLayout()
    label = QtGui.QLabel(u"Inputs number")
    layout.addWidget(label)
    nInputs = QtGui.QLineEdit(self)
    nInputs.setText('2')
    layout.addWidget(nInputs)
    self.setLayout(layout)
   
  
  @staticmethod
  def updateOptions() : 
    print 'toto'
    
class toolBox(QtGui.QListWidget) :
  """Une boîte à outils contenant les portes et circuits disponibles"""
  def __init__(self, parent) :
    super(toolBox, self).__init__(parent)
    self.insertItems(0, gates)
    self.setDragEnabled(True)

class mainView(QtGui.QGraphicsView) :
  """Une vue graphique correspondant à la scène principale"""
  def __init__(self, parent) :
    super(mainView, self).__init__(parent)
    self.setAcceptDrops(True)
    scene = QtGui.QGraphicsScene(parent)
    self.setScene(scene)
    # On veut être prévenus des changements de sélection dans la vue
    # principale afin de mettre à jour le widget des options.
    self.scene().selectionChanged.connect(toolOptions.updateOptions)
    
  def updateOptions(self) : 
    print 'toto'
    
  def dragEnterEvent(self, e): 
    e.accept()
  
  def dragMoveEvent(self, e): 
    e.accept()
  
  def dropEvent(self, e):
    model = QtGui.QStandardItemModel()
    model.dropMimeData(e.mimeData(), QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())
    item = model.item(0)
    text = item.text()
    i = circuit(2, 1, text)
    self.scene().addItem(i)
    i.setPos(e.pos())
    
  def keyPressEvent(self, e) :
    """Gère les évènements clavier : suppression, rotation, alignement"""
    # Del, suppression
    if e.key() == QtCore.Qt.Key_Delete :
      for item in self.scene().selectedItems() :
        self.scene().removeItem(item)
    # <- , rotation inverse au sens des aiguilles
    elif e.key() == QtCore.Qt.Key_Left :
      group = self.scene().createItemGroup(self.scene().selectedItems())
      #~ print group.boundingRect()
      #~ group.setTransformOriginPoint(group.boundingRect().right() / 2, group.boundingRect().bottom() / 2)
      group.setRotation(group.rotation() - 90)
      self.scene().destroyItemGroup(group)
    # -> , rotation dans le sens des aiguilles
    elif e.key() == QtCore.Qt.Key_Right :
      group = self.scene().createItemGroup(self.scene().selectedItems())
      group.setRotation(group.rotation() + 90)
      self.scene().destroyItemGroup(group)
    # L, aligner à gauche
    elif e.key() == QtCore.Qt.Key_L :
      left = min([item.scenePos().x() for item in self.scene().selectedItems()])
      for item in self.scene().selectedItems() :
        item.setPos(left, item.scenePos().y())
    # R, aligner à droite
    elif e.key() == QtCore.Qt.Key_R :
      right = max([item.scenePos().x() for item in self.scene().selectedItems()])
      for item in self.scene().selectedItems() :
        item.setPos(right, item.scenePos().y())
    # T, aligner en haut
    elif e.key() == QtCore.Qt.Key_T :
      top = min([item.scenePos().y() for item in self.scene().selectedItems()])
      for item in self.scene().selectedItems() :
        item.setPos(item.scenePos().x(), top)
    # B, aligner en bas
    elif e.key() == QtCore.Qt.Key_B :
      bottom = max([item.scenePos().y() for item in self.scene().selectedItems()])
      for item in self.scene().selectedItems() :
        item.setPos(item.scenePos().x(), bottom)
 
class mainWindow(QtGui.QMainWindow) :
  """La fenêtre principale de notre application"""
  def __init__(self) :
    super(mainWindow, self).__init__()
    self.setWindowTitle("IED Logic Simulator") 
    view = mainView(self)               # Une zone de travail
    self.setCentralWidget(view)         # principale.
    toolbox = toolBox(self)                # Une boîte à outils 
    boxDock = QtGui.QDockWidget('Toolbox') # dans un dock.
    boxDock.setWidget(toolbox)
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, boxDock)
    tooloptions = toolOptions()    # Options de l'outil sélectionné
    optionsDock = QtGui.QDockWidget('Tool options') # dans un dock.
    optionsDock.setWidget(tooloptions)
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, optionsDock)

    fileMenu = QtGui.QMenu('File')
    fileMenu.addAction('Quit', self.close)
    self.menuBar().addMenu(fileMenu)
    helpMenu = QtGui.QMenu('Help')
    helpMenu.addAction('Documentation')
    helpMenu.addAction('About', self.about)
    self.menuBar().addMenu(helpMenu)
    self.show()
    
  def about(self) :
    """Affiche un dialogue d'informations sur le programme"""
    msgBox = QtGui.QMessageBox()
    msgBox.setText(u'v0.1\nPar Mathieu Fourcroy & Sébastien Magnien.')
    msgBox.exec_()
    
# La boucle principale du programme
app = QtGui.QApplication(sys.argv)
win = mainWindow()
sys.exit(app.exec_())
