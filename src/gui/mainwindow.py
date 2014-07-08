#!/usr/bin/env python3
# coding=utf-8

"""Ne pas oublié d'ajouter style=GTK+ dans le paragraphe [Qt] de
~/.config/Trolltech.conf pour utiliser le style GTK+.
Puis installer le paquet gtk2-engines-pixbuf.
"""

import time
from PySide import QtGui, QtCore

from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions

from engine.gates import *                   # basic logic gates
from engine.simulator import log, formatter  # Log manager and log formatter


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
        # -+++++++----------------- the main window -----------------+++++++- #
        self.setWindowTitle("IED Logic Simulator")
        self.centerAndResize()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # -+++++++----- the view chere we can create the circuit ----+++++++- #
        view = MainView(self)
        self.setCentralWidget(view)                  # as central widget
        # -+++++++-------- a dock we can drag the gates from --------+++++++- #
        toolbox = ToolBox()
        self.boxDock = QtGui.QDockWidget('Tool box')  # in a dock
        self.boxDock.setWidget(toolbox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.boxDock)
        # -+++++++--------- a dock for gates and I/O options --------+++++++- #
        tooloptions = ToolOptions()
        self.optionsDock = QtGui.QDockWidget('Tool options')  # in a dock
        self.optionsDock.setWidget(tooloptions)
        self.optionsDock.setMaximumSize(QtCore.QSize(524287, 161))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.optionsDock)
        # -+++++++----------- a dock for the logs messages ----------+++++++- #
        self.logWindow = LoggerTextEdit()
        handler = logging.StreamHandler(self.logWindow)
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)
        handler.setFormatter(formatter)
        log.info("New session started on %s" % (time.strftime("%d/%m/%Y"),))
        self.logDock = QtGui.QDockWidget('Logs')
        self.logDock.setWidget(self.logWindow)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)
        # -+++++++------------------ the menu bar -------------------+++++++- #
        #         -+++++++---------- the file menu ----------+++++++-         #
        fileMenu = QtGui.QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)
        #         -+++++++--------- the windows menu --------+++++++-         #
        #                 -+---- toggle toolBox action ----+-                 #
        self.toolBoxAct = self.boxDock.toggleViewAction()
        self.toolBoxAct.setShortcut("Ctrl+Shift+T")
        self.toolBoxAct.setStatusTip("Shows the tool box")
        self.toolBoxAct.setChecked(True)
        #                 -+-- toggle toolOptions action --+-                 #
        self.toolOptionsAct = self.optionsDock.toggleViewAction()
        self.toolOptionsAct.setShortcut("Ctrl+Shift+O")
        self.toolOptionsAct.setStatusTip("Shows the item options")
        self.toolOptionsAct.setChecked(True)
        #                 -+------ toggle logs action -----+-                 #
        self.logAct = self.logDock.toggleViewAction()
        self.logAct.setShortcut("Ctrl+Shift+L")
        self.logAct.setStatusTip("Shows the logs messages dock")
        self.logAct.setChecked(True)
        #                 -+------- the menu itself -------+-                 #
        windowsMenu = QtGui.QMenu('Windows')
        windowsMenu.addAction(self.toolBoxAct)
        windowsMenu.addAction(self.toolOptionsAct)
        windowsMenu.addAction(self.logAct)
        #         -+++++++---------- the help menu ----------+++++++-         #
        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation')
        helpMenu.addAction('About', self.about)
        #                 -+--------- the menu bar --------+-                 #
        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(windowsMenu)
        self.menuBar().addMenu(helpMenu)
        # -+++++++--------------- signals connections ---------------+++++++- #
        tooloptions.clicked.connect(self.setStatusMessage)
        ###########
        self.show()

    def centerAndResize(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width() / 1.2, screen.height() / 1.2)
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) / 2,
            (screen.height() - size.height()) / 2)

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
