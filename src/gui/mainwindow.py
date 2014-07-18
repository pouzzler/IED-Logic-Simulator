#!/usr/bin/env python3
# coding=utf-8

"""Ne pas oublié d'ajouter style=GTK+ dans le paragraphe [Qt] de
~/.config/Trolltech.conf pour utiliser le style GTK+.
Puis installer le paquet gtk2-engines-pixbuf.
"""

import time
import configparser
from PySide import QtGui, QtCore

from .mainview import MainView
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .guilog import LoggerTextEdit
from .settings import SettingsWidget, configFile

from engine.gates import *                   # basic logic gates
from engine.simulator import log, formatter, Plug


class MainWindow(QtGui.QMainWindow):
    """Our application's main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        # -+++++++----------------- THE MAIN WINDOW -----------------+++++++- #
        self.setWindowTitle("IED Logic Simulator")
        self.centerAndResize()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # -+++++++----- THE VIEW CHERE WE CAN CREATE THE CIRCUIT ----+++++++- #
        self.view = MainView(self)
        self.setCentralWidget(self.view)  # as central widget
        # -+++++++-------- A DOCK WE CAN DRAG THE GATES FROM --------+++++++- #
        ########################### TOOL BOX OBJECT ###########################
        self.toolbox = ToolBox()
        #######################################################################
        self.boxDock = QtGui.QDockWidget('Tool box')  # in a dock
        self.boxDock.setWidget(self.toolbox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.boxDock)
        # -+++++++--------- A DOCK FOR GATES AND I/O OPTIONS --------+++++++- #
        ######################### TOOL OPTIONS OBJECT #########################
        self.tooloptions = ToolOptions()
        #######################################################################
        self.optionsDock = QtGui.QDockWidget('Tool options')  # in a dock
        self.optionsDock.setWidget(self.tooloptions)
        self.optionsDock.setMaximumSize(QtCore.QSize(524287, 161))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.optionsDock)
        # -+++++++----------- A DOCK FOR THE LOGS MESSAGES ----------+++++++- #
        ############################ LOB BOX OBJECT ###########################
        self.logWindow = LoggerTextEdit()
        #######################################################################
        handler = logging.StreamHandler(self.logWindow)
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)
        handler.setFormatter(formatter)
        log.info("New session started on %s" % (time.strftime("%d/%m/%Y"),))
        self.logDock = QtGui.QDockWidget('Logs')
        self.logDock.setWidget(self.logWindow)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logDock)
        # -+++++++--------------- THE SETTINGS WIDGET ---------------+++++++- #
        ######################## SETTINGS WIDGET OBJECT #######################
        self.settings = SettingsWidget(configFile)
        #######################################################################
        self.settings.setGeometry(100, 100, 600, 500)
        # -+++++++------------------ THE MENU BAR -------------------+++++++- #
        #         -+++++++---------- THE FILE MENU ----------+++++++-         #
        fileMenu = QtGui.QMenu(u'File')
        fileMenu.addAction(u'Quit', self.close)
        #         -+++++++---------- THE EDIT MENU ----------+++++++-         #
        editMenu = QtGui.QMenu(u'Edit')
        self.settingAct = QtGui.QAction('&Settings...', self)
        self.settingAct.setStatusTip('Open the settings window.')
        self.settingAct.triggered.connect(self.settings.show)
        editMenu.addAction(self.settingAct)
        #         -+++++++--------- THE WINDOWS MENU --------+++++++-         #
        #                 -+---- TOGGLE TOOLBOX ACTION ----+-                 #
        self.toolBoxAct = self.boxDock.toggleViewAction()
        self.toolBoxAct.setShortcut("Ctrl+Shift+T")
        self.toolBoxAct.setStatusTip("Shows the tool box")
        self.toolBoxAct.setChecked(True)
        #                 -+-- TOGGLE TOOLOPTIONS ACTION --+-                 #
        self.toolOptionsAct = self.optionsDock.toggleViewAction()
        self.toolOptionsAct.setShortcut("Ctrl+Shift+O")
        self.toolOptionsAct.setStatusTip("Shows the item options")
        self.toolOptionsAct.setChecked(True)
        #                 -+------ TOGGLE LOGS ACTION -----+-                 #
        self.logAct = self.logDock.toggleViewAction()
        self.logAct.setShortcut("Ctrl+Shift+L")
        self.logAct.setStatusTip("Shows the logs messages dock")
        self.logAct.setChecked(True)
        #                 -+------- THE MENU ITSELF -------+-                 #
        windowsMenu = QtGui.QMenu('Windows')
        windowsMenu.addAction(self.toolBoxAct)
        windowsMenu.addAction(self.toolOptionsAct)
        windowsMenu.addAction(self.logAct)
        #         -+++++++---------- THE HELP MENU ----------+++++++-         #
        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation')
        helpMenu.addAction('About', self.about)
        #                 -+--------- THE MENU BAR --------+-                 #
        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(windowsMenu)
        self.menuBar().addMenu(helpMenu)
        # -+++++++--------------- SIGNALS CONNECTIONS ---------------+++++++- #
        self.tooloptions.clicked.connect(self.setStatusMessage)
        # it could be possible to reload only the changed option
        # but I'm not sure that it would be simplier and faster
        self.settings.configSaved.connect(self.loadConfig)
        # -+++++++-------------- SET VARS AND START UI --------------+++++++- #
        self.loadConfig()
        self.show()

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
        removeCircuitVb = config.getboolean('GUILogRecords','removing_circ')
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
