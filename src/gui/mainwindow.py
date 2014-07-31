#!/usr/bin/env python3
# coding=utf-8

import pickle
import time
from configparser import ConfigParser
from PySide.QtCore import Qt
from PySide.QtGui import (
    QAction, QBrush, QColor, QDesktopWidget, QDockWidget, QMainWindow,
    QMenu, QMessageBox, QPalette, QPixmap, QImage)
from .mainview import MainView
from .toolbox import ToolBox, ToolBoxDockWidget
from .selectionoptions import SelectionOptions, SelectionOptionsDockWidget
from .docu import HelpDockWidget
from .logwidgets import LogDockWidget
from .settings import SettingsDialog
from engine.gates import *
from engine.simulator import log, fileHandler, stdoutHandler, formatter, Plug

from .graphicitem import *


class MainWindow(QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        # Get application strings
        self.configFile = os.path.dirname(
            os.path.realpath(__file__)) + '/../../settings.cfg'
        cfg = ConfigParser()
        cfg.read(self.configFile)
        strFile = (
            os.path.dirname(os.path.realpath(__file__))
            + '/../../strings_' + cfg.get('Appearance', 'lang') + '.txt')
        f = open(strFile, 'r')
        for _, line in enumerate(f):
            exec(line)
        self.setWindowTitle(self.str_mainWindowTitle)
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
        self.optionsDock = SelectionOptionsDockWidget(self.view)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.optionsDock)
        # A log window.
        self.logDock = LogDockWidget()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logDock)
        # Initialize application menu :
        fileMenu = QMenu(self.str_menuFile)
        fileMenu.addAction(self.str_menuSave, self.saveCircuit)
        fileMenu.addAction(self.str_menuQuit, self.close)

        editMenu = QMenu(self.str_menuEdit)
        settingAct = QAction(self.str_menuSettings, self)
        settingAct.triggered.connect(lambda: SettingsDialog(self).exec_())
        editMenu.addAction(settingAct)

        toolBoxAct = self.boxDock.toggleViewAction()
        toolBoxAct.setShortcut("Ctrl+Shift+T")
        toolBoxAct.setStatusTip("Shows the tool box")
        toolBoxAct.setChecked(True)

        SelectionOptionsAct = self.optionsDock.toggleViewAction()
        SelectionOptionsAct.setShortcut("Ctrl+Shift+O")
        SelectionOptionsAct.setStatusTip("Shows the item options")
        SelectionOptionsAct.setChecked(True)

        logAct = self.logDock.toggleViewAction()
        logAct.setShortcut("Ctrl+Shift+L")
        logAct.setStatusTip("Shows the logs messages dock")
        logAct.setChecked(True)

        windowsMenu = QMenu(self.str_menuDocks)
        windowsMenu.addAction(toolBoxAct)
        windowsMenu.addAction(SelectionOptionsAct)
        windowsMenu.addAction(logAct)

        langMenu = QMenu(self.str_menuLang)
        langMenu.addAction(self.str_langEng, lambda: self.setLang('en'))
        langMenu.addAction(self.str_langFr, lambda: self.setLang('fr'))
        helpMenu = QMenu(self.str_menuHelp)
        helpMenu.addAction(self.str_menuDoc, self.showDocumentation)
        helpMenu.addAction(self.str_menuAbout, self.about)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(windowsMenu)
        self.menuBar().addMenu(langMenu)
        self.menuBar().addMenu(helpMenu)

        self.toastHandler = logging.StreamHandler(self.view)
        self.toastHandler.setLevel(logging.WARNING)
        log.addHandler(self.toastHandler)

        self.loadConfig()
        self.show()

    def loadConfig(self):
        """Load color, verbosity and logging options."""
        cfg = ConfigParser()
        cfg.read(self.configFile)

        self.logDock.setBgColor(cfg.get('Appearance', 'log_bg_color'))
        image = QImage(10, 10, QImage.Format_RGB32)
        image.fill(QColor(cfg.get('Appearance', 'circ_bg_color')))
        image.setPixel(0, 0, QColor(0, 0, 0).rgb())
        self.view.scene().setBackgroundBrush(QBrush(QPixmap.fromImage(image)))
        Plug.setInputVerbose = cfg.getboolean(
            'GUILogRecords', 'input_chang')
        Plug.setOutputVerbose = cfg.getboolean(
            'GUILogRecords', 'output_chang')
        Plug.connectVerbose = cfg.getboolean(
            'GUILogRecords', 'conn_discon_io')
        Circuit.addPlugVerbose = cfg.getboolean(
            'GUILogRecords', 'adding_io')
        Circuit.addCircuitVerbose = cfg.getboolean(
            'GUILogRecords', 'adding_circ')
        Circuit.removePlugVerbose = cfg.getboolean(
            'GUILogRecords', 'removing_io')
        Circuit.removeCircuitVerbose = cfg.getboolean(
            'GUILogRecords', 'removing_circ')
        Circuit.detailedRemoveVerbose = cfg.getboolean(
            'GUILogRecords', 'detailed_rm')
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
        msgBox.setText(self.str_aboutDialog)
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

    def setLang(self, lang):
        cfg = ConfigParser()
        cfg.read(self.configFile)
        old = cfg.get('Appearance', 'lang')
        if old != lang:
            cfg.set('Appearance', 'lang', lang)
            with open(self.configFile, 'w+') as f:
                cfg.write(f)
            msgBox = QMessageBox()
            msgBox.setText(self.str_langChanged)
            msgBox.exec_()
        
    def showDocumentation(self):
        """Shows the help dock widget."""
        self.addDockWidget(
            Qt.RightDockWidgetArea, HelpDockWidget())
