#!/usr/bin/env python3
# coding=utf-8

from time import gmtime, strftime

from PySide import QtGui, QtCore
from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions

from engine.gates import *              # basic logic gates
from engine.simulator import myLog, date      # log manager


#================================== CLASSES ==================================#
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
            "&Show logs", self, checkable=True,
            shortcut="Ctrl+L", statusTip="Shows the log",
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
        self.logWindow = BlackTextBox()
        self.logDock = QtGui.QDockWidget('Logs')
        self.logDock.setWidget(self.logWindow)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)
        myLog.toggle_gui_signal(True)  # set the log to emit a signal with mess
        # signals connexions
        tooloptions.clicked.connect(self.setStatusMessage)
        myLog.newLogMessage.connect(self.printLogMessage)
        # print a message on the logs
        myLog.print_message("New session started on %s" % (date(),))
        self.show()

    def setStatusMessage(self, message):
        """Prints a message in the statusbar."""
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

    def printLogMessage(self, message):
        """Append a message on the next line of the log field."""

        self.logWindow.append(message)
