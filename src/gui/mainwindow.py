#!/usr/bin/env python3
# coding=utf-8

from os.path import basename
import pickle
import time
from PySide.QtCore import Qt
from PySide.QtGui import (
    QAction, QBrush, QColor, QDesktopWidget, QDockWidget, QFileDialog,
    QGraphicsSimpleTextItem, QMainWindow, QMenu, QMessageBox, QPalette,
    QPixmap, QImage)
from .docu import HelpDockWidget
from .graphicitem import *
from .logwidgets import LogDockWidget
from .mainview import MainView
from .selectionoptions import SelectionOptions, SelectionOptionsDockWidget
from .settings import Settings, SettingsDialog
from .toolbox import ToolBox, ToolBoxDockWidget
from .util import filePath
from engine.gates import *
from engine.simulator import fileHandler, formatter, log, Plug, stdoutHandler


class MainWindow(QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.config = Settings()    # Initiate application settings.
        # Get application strings.
        strFile = filePath(
            'lang/strings_' + self.config.get('Appearance', 'lang'))
        f = open(strFile, 'r')
        for _, line in enumerate(f):
            exec(line)
        # Setup window.
        self.setWindowTitle(self.str_mainWindowTitle)
        self.centerAndResize()
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
        fileMenu.addAction(self.str_menuLoad, self.loadCircuit)
        fileMenu.addAction(self.str_menuSave, self.saveCircuit)
        fileMenu.addAction(self.str_menuQuit, self.close)

        editMenu = QMenu(self.str_menuEdit)
        editMenu.addAction(
            self.str_menuSettings,
            lambda: SettingsDialog(self, self.config).exec_())
        editMenu.addAction(self.str_menuClearLogs, self.logDock.widget().clear)
        editMenu.addAction(self.str_menuClearCircuit, self.view.clearCircuit)
        editMenu.addAction("TEST TEST", self.view.fillIO)

        docksMenu = QMenu(self.str_menuDocks)
        docksMenu.addAction(self.boxDock.toggleViewAction())
        docksMenu.addAction(self.optionsDock.toggleViewAction())
        docksMenu.addAction(self.logDock.toggleViewAction())

        langMenu = QMenu(self.str_menuLang)
        langMenu.addAction(self.str_langEng, lambda: self.setLang('en'))
        langMenu.addAction(self.str_langFr, lambda: self.setLang('fr'))
        helpMenu = QMenu(self.str_menuHelp)
        helpMenu.addAction(self.str_menuDoc, self.showDocumentation)
        helpMenu.addAction(self.str_menuAbout, self.about)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(docksMenu)
        self.menuBar().addMenu(langMenu)
        self.menuBar().addMenu(helpMenu)
        # WARNING logs will be shown in the MainView.
        self.toastHandler = logging.StreamHandler(self.view)
        self.toastHandler.setLevel(logging.WARNING)
        log.addHandler(self.toastHandler)
        # Every widget is created, we can now apply settings.
        self.setSettings()
        self.show()

    def about(self):
        """Print a dialog about the application."""
        msgBox = QMessageBox()
        msgBox.setText(self.str_aboutDialog)
        msgBox.exec_()

    def centerAndResize(self):
        """Set up reasonable dimensions for our main window."""
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() / 1.2, screen.height() / 1.2)
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) / 2,
            (screen.height() - size.height()) / 2)

    def loadCircuit(self):
        """Load a user circuit."""
        ret = QFileDialog.getOpenFileName(
            self, self.str_loadCircuit, filePath('user'), self.str_circuitFile)
        if len(ret[0]):
            self.view.clearCircuit()
            f = open(ret[0], 'rb')
            items = pickle.load(f)
            f.close()
            for item in items:
                if isinstance(item[0], dict):
                    i = WireItem(
                        item[0]['startIO'], item[0]['points'],
                        item[0]['endIO'])
                else:
                    self.view.mainCircuit.add(item[0])
                    if isinstance(item[0], Plug):
                        i = PlugItem(item[0])
                    else:
                        i = CircuitItem(item[0])
                self.view.scene().addItem(i)
                i.setPos(item[1])
                i.setRotation(item[2])
                i.setupPaint()

    def saveCircuit(self):
        """Save a user circuit."""
        ret = QFileDialog.getSaveFileName(
            self, self.str_saveCircuit, filePath('user'), self.str_circuitFile)
        if len(ret[0]):
            items = []
            for item in self.view.scene().items():
                if not isinstance(item, QGraphicsSimpleTextItem):
                    items.append([item.data, item.pos(), item.rotation()])
            name = ret[0] if ret[0][-4:] != '.crc' else ret[0][:-4]
            f = open(name + '.crc', 'wb')
            pickle.dump(items, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            for i in range(self.boxDock.widget().userheader.childCount()):
                if (
                        self.boxDock.widget().userheader.child(i).text(0)
                        == basename(name)):
                    return
            self.boxDock.widget().addUserCircuit(basename(name))

    def setLang(self, lang):
        """Sets the UI language. Warns a restart is required."""
        old = self.config.get('Appearance', 'lang')
        if old != lang:
            self.config.set('Appearance', 'lang', lang)
            with open(self.config.configFile, 'w+') as f:
                self.config.write(f)
            msgBox = QMessageBox()
            msgBox.setText(self.str_langChanged)
            msgBox.exec_()

    def setSettings(self):
        """Set color, verbosity and logging options."""
        self.logDock.setBgColor(self.config.get('Appearance', 'log_bg_color'))
        image = QImage(10, 10, QImage.Format_RGB32)
        image.fill(QColor(self.config.get('Appearance', 'circ_bg_color')))
        image.setPixel(0, 0, QColor(0, 0, 0).rgb())
        self.view.scene().setBackgroundBrush(QBrush(QPixmap.fromImage(image)))
        Plug.setInputVerbose = self.config.getboolean(
            'LogVerbosity', 'input_chang')
        Plug.setOutputVerbose = self.config.getboolean(
            'LogVerbosity', 'output_chang')
        Plug.connectVerbose = self.config.getboolean(
            'LogVerbosity', 'conn_discon_io')
        Plug.addPlugVerbose = self.config.getboolean(
            'LogVerbosity', 'adding_io')
        Circuit.addCircuitVerbose = self.config.getboolean(
            'LogVerbosity', 'adding_circ')
        Circuit.removePlugVerbose = self.config.getboolean(
            'LogVerbosity', 'removing_io')
        Circuit.removeCircuitVerbose = self.config.getboolean(
            'LogVerbosity', 'removing_circ')
        Circuit.detailedRemoveVerbose = self.config.getboolean(
            'LogVerbosity', 'detailed_rm')
        if self.config.getboolean('LogHandlers', 'gui'):
            log.addHandler(self.logDock.handler)
        else:
            log.removeHandler(self.logDock.handler)
        if self.config.getboolean('LogHandlers', 'stdout'):
            log.addHandler(stdoutHandler)
        else:
            log.removeHandler(stdoutHandler)
        if self.config.getboolean('LogHandlers', 'file'):
            log.addHandler(fileHandler)
        else:
            log.removeHandler(fileHandler)

    def showDocumentation(self):
        """Shows the help dock widget."""
        self.addDockWidget(Qt.RightDockWidgetArea, HelpDockWidget())
