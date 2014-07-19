#!/usr/bin/env python3
# coding=utf-8

import time
import configparser
from PySide import QtGui, QtCore

from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .docu import HelpDockWidget
from .guilog import LoggerTextEdit
from .settings import SettingsWidget, configFile

from engine.gates import *                   # basic logic gates
from engine.simulator import log, formatter, Plug


class MainWindow(QtGui.QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("IED Logic Simulator")
        self.centerAndResize()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.view = MainView(self)
        self.setCentralWidget(self.view)

        self.toolbox = ToolBox()
        self.boxDock = QtGui.QDockWidget('Tool box')
        self.boxDock.setWidget(self.toolbox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.boxDock)

        self.tooloptions = ToolOptions()
        self.optionsDock = QtGui.QDockWidget('Tool options')
        self.optionsDock.setWidget(self.tooloptions)
        self.optionsDock.setMaximumSize(QtCore.QSize(524287, 161))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.optionsDock)

        self.logWindow = LoggerTextEdit()

        handler = logging.StreamHandler(self.logWindow)
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)
        handler.setFormatter(formatter)
        log.info("New session started on %s" % (time.strftime("%d/%m/%Y"),))
        self.logDock = QtGui.QDockWidget('Logs')
        self.logDock.setWidget(self.logWindow)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)

        self.settings = SettingsWidget(configFile)
        # TODO : il devrait décider sa géométrie tout seul
        self.settings.setGeometry(100, 100, 600, 500)

        fileMenu = QtGui.QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)

        editMenu = QtGui.QMenu(u'Edit')
        self.settingAct = QtGui.QAction('&Settings...', self)
        self.settingAct.setStatusTip('Open the settings window.')
        self.settingAct.triggered.connect(self.settings.show)
        editMenu.addAction(self.settingAct)

        self.toolBoxAct = self.boxDock.toggleViewAction()
        self.toolBoxAct.setShortcut("Ctrl+Shift+T")
        self.toolBoxAct.setStatusTip("Shows the tool box")
        self.toolBoxAct.setChecked(True)

        self.toolOptionsAct = self.optionsDock.toggleViewAction()
        self.toolOptionsAct.setShortcut("Ctrl+Shift+O")
        self.toolOptionsAct.setStatusTip("Shows the item options")
        self.toolOptionsAct.setChecked(True)

        self.logAct = self.logDock.toggleViewAction()
        self.logAct.setShortcut("Ctrl+Shift+L")
        self.logAct.setStatusTip("Shows the logs messages dock")
        self.logAct.setChecked(True)

        windowsMenu = QtGui.QMenu('Windows')
        windowsMenu.addAction(self.toolBoxAct)
        windowsMenu.addAction(self.toolOptionsAct)
        windowsMenu.addAction(self.logAct)

        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation', self.showDocumentation)
        helpMenu.addAction('Test', self.Test)
        helpMenu.addAction('About', self.about)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(windowsMenu)
        self.menuBar().addMenu(helpMenu)

        self.tooloptions.clicked.connect(self.setStatusMessage)
        # it could be possible to reload only the changed option
        # but I'm not sure that it would be simplier and faster
        self.settings.configSaved.connect(self.loadConfig)

        self.loadConfig()
        self.show()
        self.Test()

    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read(configFile)

        # background color for the scene
        circBgColor = QtGui.QColor()
        circBgColor.setNamedColor(config.get('Appearance', 'circ_bg_color'))
        # background color for the log windget
        logBgColor = QtGui.QColor()
        logBgColor.setNamedColor(config.get('Appearance', 'log_bg_color'))
        logPalette = self.logWindow.pal
        logPalette.setColor(QtGui.QPalette.Base, logBgColor)
        # log verbose
        setInputVb = config.getboolean('GUILogRecords', 'input_chang')
        setOutputVb = config.getboolean('GUILogRecords', 'output_chang')
        connectVb = config.getboolean('GUILogRecords', 'conn_discon_io')
        addPlugVb = config.getboolean('GUILogRecords', 'adding_io')
        addCircuitVb = config.getboolean('GUILogRecords', 'adding_circ')
        removePlugVb = config.getboolean('GUILogRecords', 'removing_io')
        removeCircuitVb = config.getboolean('GUILogRecords', 'removing_circ')
        detailedRemoveVb = config.getboolean('GUILogRecords', 'detailed_rm')

        # apply config values
        self.view.graphScene.setBackgroundBrush(circBgColor)
        self.logWindow.setPalette(logPalette)
        Plug.setInputVerbose = setInputVb
        Plug.setOutputVerbose = setOutputVb
        Plug.connectVerbose = connectVb
        Circuit.addPlugVerbose = addPlugVb
        Circuit.addCircuitVerbose = addCircuitVb
        Circuit.removePlugVerbose = removePlugVb
        Circuit.removeCircuitVerbose = removeCircuitVb
        Circuit.detailedRemoveVerbose = detailedRemoveVb

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

    def showDocumentation(self):
        """Shows the help dock widget."""
        self.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, HelpDockWidget('Help'))

    def Test(self):
        from .test import SettingsDialog
        settingsDialog = SettingsDialog()
        settingsDialog.exec_()
