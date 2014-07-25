#!/usr/bin/env python3
# coding=utf-8

import time
import configparser
from PySide.QtCore import Qt
from PySide.QtGui import (
    QAction, QColor, QDesktopWidget, QDockWidget, QMainWindow, QMenu,
    QMessageBox, QPalette)
from .mainview import MainView
from .toolbox import ToolBoxDockWidget
from .tooloptions import ToolOptionsDockWidget
from .docu import HelpDockWidget
from .logwidgets import LogDockWidget
from .settings import SettingsDialog, configFile
from engine.gates import *
from engine.simulator import log, fileHandler, stdoutHandler, formatter, Plug


class MainWindow(QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("IED Logic Simulator")
        self.centerAndResize()
        self.setFocusPolicy(Qt.StrongFocus)
        # A graphical view in which the user can draw circuits.
        self.view = MainView(self)
        self.setCentralWidget(self.view)
        # Gates and circuits to be dragged in the main view.
        self.boxDock = ToolBoxDockWidget()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.boxDock)
        # Used to modify selected items properties.
        self.optionsDock = ToolOptionsDockWidget(self.view)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.optionsDock)
        # A log window.
        self.logDock = LogDockWidget()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logDock)

        self.toastHandler = logging.StreamHandler(self.view)
        self.toastHandler.setLevel(logging.WARNING)
        log.addHandler(self.toastHandler)

        self.settings = SettingsDialog(configFile)

        fileMenu = QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)

        editMenu = QMenu(u'Edit')
        settingAct = QAction('&Settings...', self)
        settingAct.setStatusTip('Open the settings window.')
        settingAct.triggered.connect(self.settings.show)
        editMenu.addAction(settingAct)

        toolBoxAct = self.boxDock.toggleViewAction()
        toolBoxAct.setShortcut("Ctrl+Shift+T")
        toolBoxAct.setStatusTip("Shows the tool box")
        toolBoxAct.setChecked(True)

        toolOptionsAct = self.optionsDock.toggleViewAction()
        toolOptionsAct.setShortcut("Ctrl+Shift+O")
        toolOptionsAct.setStatusTip("Shows the item options")
        toolOptionsAct.setChecked(True)

        logAct = self.logDock.toggleViewAction()
        logAct.setShortcut("Ctrl+Shift+L")
        logAct.setStatusTip("Shows the logs messages dock")
        logAct.setChecked(True)

        windowsMenu = QMenu('Windows')
        windowsMenu.addAction(toolBoxAct)
        windowsMenu.addAction(toolOptionsAct)
        windowsMenu.addAction(logAct)

        helpMenu = QMenu('Help')
        helpMenu.addAction('Documentation', self.showDocumentation)
        helpMenu.addAction('About', self.about)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(windowsMenu)
        self.menuBar().addMenu(helpMenu)

        # this is easier than reloading one setting only
        self.settings.configSaved.connect(self.loadConfig)

        self.loadConfig()
        self.show()

    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read(configFile)

        # background color for the scene
        circBgColor = QColor()
        circBgColor.setNamedColor(config.get('Appearance', 'circ_bg_color'))
        # background color for the log widget
        logBgColor = QColor()
        logBgColor.setNamedColor(config.get('Appearance', 'log_bg_color'))
        logPalette = self.logDock.widget().pal
        logPalette.setColor(QPalette.Base, logBgColor)
        # log verbose
        setInputVb = config.getboolean('GUILogRecords', 'input_chang')
        setOutputVb = config.getboolean('GUILogRecords', 'output_chang')
        connectVb = config.getboolean('GUILogRecords', 'conn_discon_io')
        addPlugVb = config.getboolean('GUILogRecords', 'adding_io')
        addCircuitVb = config.getboolean('GUILogRecords', 'adding_circ')
        removePlugVb = config.getboolean('GUILogRecords', 'removing_io')
        removeCircuitVb = config.getboolean('GUILogRecords', 'removing_circ')
        detailedRemoveVb = config.getboolean('GUILogRecords', 'detailed_rm')
        guiLogOutput = config.getboolean('LogOutputs', 'gui')
        stdoutLogOutput = config.getboolean('LogOutputs', 'stdout')
        fileLogOutput = config.getboolean('LogOutputs', 'file')

        # apply config values
        self.view.scene().setBackgroundBrush(circBgColor)
        self.logDock.widget().setPalette(logPalette)
        Plug.setInputVerbose = setInputVb
        Plug.setOutputVerbose = setOutputVb
        Plug.connectVerbose = connectVb
        Circuit.addPlugVerbose = addPlugVb
        Circuit.addCircuitVerbose = addCircuitVb
        Circuit.removePlugVerbose = removePlugVb
        Circuit.removeCircuitVerbose = removeCircuitVb
        Circuit.detailedRemoveVerbose = detailedRemoveVb
        if guiLogOutput:
            log.addHandler(self.logDock.handler)
        else:
            log.removeHandler(self.logDock.handler)
        if stdoutLogOutput:
            log.addHandler(stdoutHandler)
        else:
            log.removeHandler(stdoutHandler)
        if fileLogOutput:
            log.addHandler(fileHandler)
        else:
            log.removeHandler(fileHandler)

    def centerAndResize(self):
        """Set up reasonable dimensions for our main window."""
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() / 1.2, screen.height() / 1.2)
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) / 2,
            (screen.height() - size.height()) / 2)

    def about(self):
        """Print a dialog about the application."""
        msgBox = QMessageBox()
        msgBox.setText(u'v0.1\nPar Mathieu Fourcroy & Sébastien Magnien.')
        msgBox.exec_()

    def showDocumentation(self):
        """Shows the help dock widget."""
        self.addDockWidget(
            Qt.RightDockWidgetArea, HelpDockWidget('Help'))
