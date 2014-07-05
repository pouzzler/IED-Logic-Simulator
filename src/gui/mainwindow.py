#!/usr/bin/env python3
# coding=utf-8

import time
from PySide import QtGui, QtCore

from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions

from engine.gates import *                   # basic logic gates
from engine.simulator import log             # Top-level circuit & log manager


class LoggerTextEdit(QtGui.QTextEdit):
    """A multiline text field that receives log messages."""

    def __init__(self):
        super(LoggerTextEdit, self).__init__()

    def write(self, text):
        """Our strategy is to create a log object, associated with a
        stream handler forwarding mesages to LoggerTextEdit, even though
        it is not a stream, which works because of the write() method.
        """
        self.append(text)


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
        # a menu bar
        # the File menu
        fileMenu = QtGui.QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)
        self.menuBar().addMenu(fileMenu)
        # the Options menu
        optionsMenu = QtGui.QMenu('Options')
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
        helpMenu.addAction('Documentation')
        helpMenu.addAction('About', self.about)
        self.menuBar().addMenu(helpMenu)
        # a window for the logs
        self.logWindow = LoggerTextEdit()
        log = logging.getLogger('src.engine.simulator')
        log.addHandler(logging.StreamHandler(self.logWindow))
        log.info("New session started on %s" % (time.strftime("%d/%m/%Y"),))
        self.logDock = QtGui.QDockWidget('Logs')
        self.logDock.setWidget(self.logWindow)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)
        # signals connexions
        tooloptions.clicked.connect(self.setStatusMessage)
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

    def showLogs(self):
        """Hide or show the log window."""
        if self.logAct.isChecked():  # if the action is checked: show the log
            self.logDock.show()      # else: hide it
        else:
            self.logDock.hide()
