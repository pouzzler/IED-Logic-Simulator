#!/usr/bin/env python3
# coding=utf-8

import time
from PySide import QtGui, QtCore

from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .docu import HelpDockWidget

from engine.gates import *                   # basic logic gates
from engine.simulator import log             # Log manager


class LoggerTextEdit(QtGui.QTextEdit):
    """A multiline text field that receives log messages."""

    def __init__(self):
        super(LoggerTextEdit, self).__init__()
        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        pal.setColor(QtGui.QPalette.Text, textc)
        self.setPalette(pal)

    def write(self, text):
        """Log handlers call a write() method."""
        self.insertPlainText(text)


class MainWindow(QtGui.QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("IED Logic Simulator")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        view = MainView(self)                       # Une zone de travail
        self.setCentralWidget(view)                 # principale.
        self.showToolBox()
        #~ self.showToolOptions()       #pas implémenté
        # a menu bar
        # the File menu
        fileMenu = QtGui.QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)
        self.menuBar().addMenu(fileMenu)
        # the Options menu
        optionsMenu = QtGui.QMenu('Options')
        optionsMenu.addAction('Toolbox', self.showToolBox)
        optionsMenu.addAction('Tool options', self.showToolOptions)
        self.logAct = QtGui.QAction(
            "&Show logs",
            self,
            checkable=True,
            shortcut="Ctrl+L",
            statusTip="Shows the log",
            triggered=self.showLogs)
        optionsMenu.addAction(self.logAct)
        self.menuBar().addMenu(optionsMenu)
        self.logAct.setChecked(True)
        # the Help menu
        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation', self.showDocumentation)
        helpMenu.addAction('About', self.about)
        self.menuBar().addMenu(helpMenu)
        # a window for the logs
        self.logWindow = LoggerTextEdit()
        handler = logging.StreamHandler(self.logWindow)
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)
        log.info("New session started on %s" % (time.strftime("%d/%m/%Y"),))
        self.logDock = QtGui.QDockWidget('Logs')
        self.logDock.setWidget(self.logWindow)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)
        self.show()

    def setStatusMessage(self, message):
        """Print a message in the statusbar."""
        self.statusBar().showMessage(message)

    def focusInEvent(self, event):
        self.setStatusMessage(u"Cette zone sert à quelque chose")

    def about(self):
        """Print a dialog about the application."""
        msgBox = QtGui.QMessageBox()
        msgBox.setText(u'v0.1\nPar Mathieu Fourcroy & Sébastien Magnien.')
        msgBox.exec_()

    def showToolBox(self):
        toolbox = ToolBox()                         # Une boîte à outils
        boxDock = QtGui.QDockWidget('Toolbox')      # dans un dock.
        boxDock.setWidget(toolbox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, boxDock)

    def showToolOptions(self):
        tooloptions = ToolOptions()        # Options de l'outil sélectionné
        optionsDock = QtGui.QDockWidget('Tool options')  # dans un dock.
        optionsDock.setWidget(tooloptions)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, optionsDock)
        tooloptions.clicked.connect(self.setStatusMessage)
        
    def showLogs(self):
        """Hide or show the log window."""
        if self.logAct.isChecked():  # if the action is checked: show the log
            self.logDock.show()      # else: hide it
        else:
            self.logDock.hide()
            
    def showDocumentation(self):
        """Shows the help dock widget."""
        self.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, HelpDockWidget('Help'))
        
