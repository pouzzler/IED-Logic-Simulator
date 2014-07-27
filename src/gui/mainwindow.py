#!/usr/bin/env python3
# coding=utf-8

import pickle, time
from configparser import ConfigParser
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

from .graphicitem import *


class MainWindow(QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("IED Logic Simulator")
        self.centerAndResize()
        self.setFocusPolicy(Qt.StrongFocus)
        # Initialize sub-widgets :
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
        # Initialize application menu :
        fileMenu = QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)
        fileMenu.addAction(u'Save circuit', self.saveCircuit)

        editMenu = QMenu(u'Edit')
        settingAct = QAction('&Settings...', self)
        settingAct.setStatusTip('Open the settings window.')
        settingAct.triggered.connect(lambda: SettingsDialog(self).exec_())
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

        self.toastHandler = logging.StreamHandler(self.view)
        self.toastHandler.setLevel(logging.WARNING)
        log.addHandler(self.toastHandler)

        self.loadConfig()
        self.show()

    def loadConfig(self):
        """Load color, verbosity and logging options."""
        cfg = ConfigParser()
        cfg.read(configFile)

        self.logDock.setBgColor(cfg.get('Appearance', 'log_bg_color'))
        self.view.scene().setBackgroundBrush(
            QColor(cfg.get('Appearance', 'circ_bg_color')))
        Plug.setInputVerbose = cfg.getboolean('GUILogRecords', 'input_chang')
        Plug.setOutputVerbose = cfg.getboolean('GUILogRecords', 'output_chang')
        Plug.connectVerbose = cfg.getboolean('GUILogRecords', 'conn_discon_io')
        Circuit.addPlugVerbose = cfg.getboolean('GUILogRecords', 'adding_io')
        Circuit.addCircuitVerbose = cfg.getboolean('GUILogRecords', 'adding_circ')
        Circuit.removePlugVerbose = cfg.getboolean('GUILogRecords', 'removing_io')
        Circuit.removeCircuitVerbose = cfg.getboolean('GUILogRecords', 'removing_circ')
        Circuit.detailedRemoveVerbose = cfg.getboolean('GUILogRecords', 'detailed_rm')
        if cfg.getboolean('LogOutputs', 'gui'):
            log.addHandler(self.logDock.handler)
        else:
            log.removeHandler(self.logDock.handler)
        if cfg.getboolean('LogOutputs', 'stdout'):
            log.addHandler(stdoutHandler)
        else:
            log.removeHandler(stdoutHandler)
        if cfg.getboolean('LogOutputs', 'file'):
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

    def saveCircuit(self):
        f = open('save', 'wb')
        items = []
        selection = self.view.scene().items()
        for item in selection:
            if isinstance(item, PlugItem):
                items.append([item, item.pos()])
            elif isinstance(item, CircuitItem):
                items.append([item.circuit, item.pos()])
            self.view.scene().removeItem(item)
        pickle.dump(selection, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        f = open('save', 'rb')
        items = pickle.load(f)
        for item in items:
            print(item.name)
            #~ if isinstance(item[0], PlugItem):
                #~ plugItem = PlugItem(item[0].isInput, item[0].owner)
                #~ plugItem.setName(item[0].name)
                #~ plugItem.setPos(item[1])
                #~ self.view.scene().addItem(plugItem)
            #~ else:
                #~ for k, v in item[0].__dict__.items():
                    #~ print(k, v)
                    #~ if isinstance(v, list):
                        #~ for x in v:
                            #~ print('    ', x.__dict__)
        
        
    def showDocumentation(self):
        """Shows the help dock widget."""
        self.addDockWidget(
            Qt.RightDockWidgetArea, HelpDockWidget('Help'))
