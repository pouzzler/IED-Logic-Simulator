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
    """Our application's main window."""

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
