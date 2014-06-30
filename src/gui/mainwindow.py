#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions

from engine.simulator import _TC  # le circuit du "top-level"
from engine.gates import *        # portes logiques de base
from engine.circuits import *     # circuits logiques avancés
from engine.clock import *        # horloge

class MainWindow(QtGui.QMainWindow):
    """La fenêtre principale de notre application"""
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("IED Logic Simulator")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        view = MainView(self)                       # Une zone de travail
        self.setCentralWidget(view)                 # principale.
        toolbox = ToolBox()                         # Une boîte à outils
        boxDock = QtGui.QDockWidget('Toolbox')      # dans un dock.
        boxDock.setWidget(toolbox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, boxDock)
        tooloptions = ToolOptions()        # Options de l'outil sélectionné
        optionsDock = QtGui.QDockWidget('Tool options')  # dans un dock.
        optionsDock.setWidget(tooloptions)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, optionsDock)
        # un menu
        fileMenu = QtGui.QMenu('File')
        fileMenu.addAction('Quit', self.close)
        self.menuBar().addMenu(fileMenu)
        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation')
        helpMenu.addAction('About', self.about)
        
        helpMenu.addAction('Gros test qui pue', self.testquipue)
        self.menuBar().addMenu(helpMenu)

        # connexion des signaux
        tooloptions.clicked.connect(self.setStatusMessage)

        self.show()

    def setStatusMessage(self, message):
        """Affiche un message dans la barre de status"""
        self.statusBar().showMessage(message)

    def focusInEvent(self, event):
        self.setStatusMessage(u"Cette zone sert à quelque chose")

    def about(self):
        """Affiche un dialogue d'informations sur le programme"""
        msgBox = QtGui.QMessageBox()
        msgBox.setText(u'v0.1\nPar Mathieu Fourcroy & Sébastien Magnien.')
        msgBox.exec_()

    def testquipue(self):
        AND = add_circuit(AndGate('AND'))
        add_input('A')
        add_input('B')
        add_output('C')
        # on connecte les entrées et la sortie de _TC à celles du circuit AndGate
        _TC.inputList[0].connect(_TC.circuitList[0].inputList[0])
        _TC.inputList[1].connect(_TC.circuitList[0].inputList[1])
        _TC.circuitList[0].outputList[0].connect(_TC.outputList[0])
        # on affiche les valeurs de la sortie de la porte AND et de celle de _TC
        print(_TC.circuitList[0].outputList[0].value)    # => False
        print(_TC.outputList[0].value)                   # => False
        # on positionne les entrées de _TC à 1
        _TC.inputList[0].set(1)
        _TC.inputList[1].set(1)
        # on réaffiche les valeurs de la sortie de _TC et de celle du AndGate
        print(_TC.circuitList[0].outputList[0].value)   # => True
        print(_TC.outputList[0].value)                  # => True
        return
