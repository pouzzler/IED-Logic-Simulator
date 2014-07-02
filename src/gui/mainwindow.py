#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions

from engine.gates import *        # portes logiques de base


# for the log widget
class BlackTextBox(QtGui.QTextEdit):
    def __init__(self):
        QtGui.QTextEdit.__init__(self)
        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        pal.setColor(QtGui.QPalette.Text, textc)
        self.setPalette(pal)


class MainWindow(QtGui.QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        pixmap = QtGui.QPixmap('/home/seb/Documents/IED-Logic-Simulator/src/gui/icons/AND_mini.png')
        self.setWindowIcon(QtGui.QIcon(pixmap))
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
        fileMenu = QtGui.QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)
        self.menuBar().addMenu(fileMenu)
        optionsMenu = QtGui.QMenu('Options')
        optionsMenu.addAction(u'Show logs', self.showLogs)
        self.menuBar().addMenu(optionsMenu)
        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation')
        helpMenu.addAction('About', self.about)
        self.menuBar().addMenu(helpMenu)
        # a window for the logs
        self.logWindow = BlackTextBox()
        # connexion des signaux
        tooloptions.clicked.connect(self.setStatusMessage)
<<<<<<< HEAD
=======
        view.newLogMessage.connect(self.printLogMessage)

>>>>>>> 8258d2c3f42eb8c6fa7109b61ead7f6f73de99e4
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

    def showLogs(self):
        # ajouter test: pas ouvrir le dock s'il l'est déjà
        logDock = QtGui.QDockWidget('Logs')  # dans un dock.
        logDock.setWidget(self.logWindow)
        self.logWindow.append("hello")
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, logDock)

    def printLogMessage(self, message):
        self.logWindow.append(message)
