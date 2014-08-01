#!/usr/bin/env python3
# coding=utf-8

"""
####################################
## Widget for the settings window ##
####################################

This widget is called when clicking on Edit -> Settings....
The window contains some log, appearance and clock management options.
All options must be retrieved from and stored in a config file.
The config file location is defined in mainwindow.py and passed
as parameter to SettingsWidget.
"""

# TODO: add error message before return in slot functions
# TODO: in ColorSelectorButton, add a pix of the color instead of changing
#       button background color.

from configparser import ConfigParser
import sys
from PySide import QtCore
from PySide.QtGui import (
    QCheckBox, QColor, QColorDialog, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox, QLabel, QPalette,
    QPushButton, QSizePolicy, QSpacerItem, QTreeWidget, QTreeWidgetItem)
from .util import filePath


class Settings(ConfigParser):
    def __init__(self):
        super(ConfigParser, self).__init__()
        self.configFile = filePath('settings.cfg')
        self.read(self.configFile)


class ColorSelectorButton(QPushButton):
    def __init__(self, parent, config, option, text=None):
        """Get the config dictionary <config> from the parent class
        because handleStateChanged need to modify it.
        Also define the config section and option used by the class
        and a QColorDialog, a QColor and a QPalette for selecting a
        color, storing it and applying it to the button background.
        """
        QPushButton.__init__(self, parent)
        self.config = config
        self.section = 'Appearance'
        self.option = option
        self.color = QColor(0, 0, 0)
        self.palette = QPalette()
        self.colorDialog = QColorDialog()
        self.initToolButton(text)
        ## SIGNALS CONNECTIONS ##
        self.clicked.connect(self.choose_color)
        self.colorDialog.currentColorChanged.connect(self.handleColorChanged)

    def initToolButton(self, text):
        """Set object properties and define the colorDialog and palette
        then set the value retrieved from the config dictionary.
        """
        self.setText(text)
        self.color.setNamedColor(self.config.get(self.section, self.option))
        self.colorDialog.setCurrentColor(self.color)
        self.palette.setColor(QPalette.Button, self.color)
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)

    def choose_color(self):
        """Open the color chooser dialog for selecting a color and
        set the button color via the palette.
        """
        origColor = self.color      # save the current color
        self.color = self.colorDialog.getColor(origColor)
        if not self.color.isValid():
            self.color = origColor  # revert back to prev color if user cancel
        self.colorDialog.setCurrentColor(self.color)
        self.palette.setColor(QPalette.Button, self.color)
        self.setPalette(self.palette)

    @QtCore.Slot()
    def handleColorChanged(self, color):
        if not self.section or not self.option or not color.isValid():
            return
        """Change the color option when the value of the color change."""
        self.config.set(self.section, self.option, color.name())


class logOutputCheckBox(QCheckBox):
    def __init__(self, parent, config, option, text=None):
        QCheckBox.__init__(self, parent)
        self.config = config
        self.section = 'LogOutputs'
        self.option = option
        self.initCheckBox(text)
        ## SIGNALS CONNECTIONS ##
        self.stateChanged.connect(self.handleStateChanged)

    def initCheckBox(self, text):
        """Set object properties then set the value retrieved from the
        config dictionary.
        """
        self.setText(text)
        value = self.config.getboolean(self.section, self.option)
        self.setCheckState(QtCore.Qt.Checked if value else QtCore.Qt.Unchecked)

    @QtCore.Slot()
    def handleStateChanged(self):
        if not self.section or not self.option:
            return
        """Set the option value according to the item checkState"""
        v = 'True' if self.checkState() == QtCore.Qt.Checked else 'False'
        self.config.set(self.section, self.option, v)


class ClockSpeedSpinBox(QDoubleSpinBox):
    def __init__(self, parent, config):
        """Get the config dictionary <config> from the parent class
        because handleSpeedValueChanged need to modify it.
        Also define the config section used by the class.
        """
        QDoubleSpinBox.__init__(self, parent)
        self.config = config
        self.section = 'Clock'
        self.initDoubleSpinBox()
        ## SIGNALS CONNECTIONS ##
        self.valueChanged.connect(self.handleSpeedValueChanged)

    def initDoubleSpinBox(self):
        """Set object properties then set the value retrieved from the
        config dictionary.
        """
        self.setRange(0, 99.99)
        self.setSingleStep(0.5)
        self.setSuffix(' s.')
        self.setValue(self.config.getfloat('Clock', 'speed'))

    @QtCore.Slot()
    def handleSpeedValueChanged(self):
        if not self.section:
            return
        """Change the speed option when the value of the spin box change."""
        self.config.set(self.section, 'speed', str(self.value()))


class TreeWidgetItem(QTreeWidgetItem):
    """We need to subclass QTreeWidget to reimplement setData()
    and emiting a custom signal of the logRecordsTree class
    when the item check state is modified.
    """
    def setData(self, col, role, value):
        state = self.checkState(col)
        QTreeWidgetItem.setData(self, col, role, value)
        if role == QtCore.Qt.CheckStateRole and state != self.checkState(col):
            treewidget = self.treeWidget()
            if treewidget is not None:
                treewidget.treeItemStateChanged.emit(self, col)

    def setCheckStateFromOption(self, opVal):
        """Set the checkState of the item according to the boolean <opVal>"""
        if opVal is True:
            self.setCheckState(0, QtCore.Qt.Checked)
        else:
            self.setCheckState(0, QtCore.Qt.Unchecked)


class logRecordsTree(QTreeWidget):
    """We need to subclass QTreeWidget to define a new custom signal
    in the class. This signal is emitted by the TreeWidgetItem and
    connecting to handleItemStateChanged() which process the signal.
    """
    treeItemStateChanged = QtCore.Signal(object, int)

    def __init__(self, parent, config):
        """Get the config file <configFile> and the config dictionary
        <config> from the parent class because createLogRecordsTreeItem
        need to access it and handleItemStateChanged need to modify it.
        Also define the config section used by the class.
        """
        QTreeWidget.__init__(self, parent)
        self.config = config
        self.section = 'GUILogRecords'
        self.initTree()
        ## SIGNALS CONNECTIONS ##
        self.treeItemStateChanged.connect(self.handleItemStateChanged)

    def initTree(self):
        # -+++++++----------------- tree properties -----------------+++++++- #
        self.setFrameShape(QFrame.StyledPanel)
        self.setTabKeyNavigation(False)
        self.setAlternatingRowColors(False)
        self.setAnimated(True)
        # -+++++++------------------- tree headers ------------------+++++++- #
        self.header().setVisible(False)
        self.header().setDefaultSectionSize(100)
        self.header().setHighlightSections(False)
        # -+++++++-------------------- tree items -------------------+++++++- #
        ### TOP: Adding / removing an object
        self.topAddRmObj = self.createLogRecordsTreeItem(
            self, 'Adding / removing an object')
        self.topAddRmObj.setFlags(
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled |
            QtCore.Qt.ItemIsUserCheckable |
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsTristate)
        # children
        self.addingIO = self.createLogRecordsTreeItem(
            self.topAddRmObj, 'Adding an I/O', 'adding_io')
        self.addingIO = self.createLogRecordsTreeItem(
            self.topAddRmObj, 'Adding a circuit', 'adding_circ')
        self.addingIO = self.createLogRecordsTreeItem(
            self.topAddRmObj, 'Removing an I/O', 'removing_io')
        self.addingIO = self.createLogRecordsTreeItem(
            self.topAddRmObj, 'Removing a circuit', 'removing_circ')
        self.addingIO = self.createLogRecordsTreeItem(
            self.topAddRmObj, 'Detailed remove', 'detailed_rm')
        ### TOP: Connecting / disconnecting an I/O
        self.topConnDisconnIO = self.createLogRecordsTreeItem(
            self, 'Connecting / disconnecting I/O', 'conn_discon_io')
        self.topConnDisconnIO.setFlags(
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled |
            QtCore.Qt.ItemIsUserCheckable |
            QtCore.Qt.ItemIsEnabled)
        ### TOP: changing an I/O value
        self.topChangIO = self.createLogRecordsTreeItem(
            self, 'Changing an I/O value')
        self.topChangIO.setFlags(
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled |
            QtCore.Qt.ItemIsUserCheckable |
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsTristate)
        # chilren
        self.inputChang = self.createLogRecordsTreeItem(
            self.topChangIO, 'Inputs changes', 'input_chang')
        self.outputChang = self.createLogRecordsTreeItem(
            self.topChangIO, 'Outputs changes', 'output_chang')
        ### TOP: Advces (not yet implemented)
        self.topAdvices = self.createLogRecordsTreeItem(
            self, 'Advices (not yet implemented)', 'advices')
        self.topAdvices.setFlags(
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled |
            QtCore.Qt.ItemIsUserCheckable)

    def createLogRecordsTreeItem(self, parent, text, option=None):
        """Create a TreeWidgetItem object, set its first column text
        and if an option name <option> is passed to the function, retrieve
        the option value from the 'GUILogRecords' section of the config
        dictionary. Set the checkState of the item according to the value.
        """
        item = TreeWidgetItem(parent)
        item.setText(0, text)
        item.option = option
        if option:
            try:
                opVal = self.config.getboolean(self.section, option)
                item.setCheckStateFromOption(opVal)
            except:
                sys.stdout.write("invalid option '%s'\n" % (option))
        return item

    @QtCore.Slot()
    def handleItemStateChanged(self, item, column):
        """This slot is triggered by the emission of the treeItemStateChanged
        signal. The slot update the value of the config dictionary option
        if the item is managed by an option.
        """
        if not self.section or not item.option:
            return
        # it would be easier to toggle value but it's impossible with strings
        v = 'True' if item.checkState(column) == QtCore.Qt.Checked else 'False'
        self.config.set(self.section, item.option, v)


class SettingsDialog(QDialog):
    """A widget for cotroling some settings of the GUI and the engine such as:
    * clock speed
    * log records and outputs
    * some GUI colors values
    """
    configSaved = QtCore.Signal()

    def __init__(self, parent, config):
        """Init the parent class, the config dictionary and the window."""
        super(SettingsDialog, self).__init__()
        self.config = config
        self.configSaved.connect(parent.setSettings)
        self.initUI()
        ## SIGNALS CONNECTIONS ##
        self.closeButtonBox.clicked.connect(self.saveAndClose)

    def initUI(self):
        # -+++++++--------------- the settings window ---------------+++++++- #
        self.setWindowTitle("Settings")
        self.resize(562, 466)
        self.settingsGrid = QGridLayout(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        # -+++++++----------------- the clock group -----------------+++++++- #
        self.clockGroupBox = QGroupBox(self)
        self.clockGroupBox.setTitle("Clock")
        self.clockGrid = QGridLayout(self.clockGroupBox)
        ######################### CLOCK SPINBOX OBJECT ########################
        self.clockDoubleSpinBox = ClockSpeedSpinBox(
            self.clockGroupBox, self.config)
        #######################################################################
        self.clockGrid.addWidget(self.clockDoubleSpinBox, 0, 1, 1, 1)
        self.clockLabel = QLabel(self.clockGroupBox)
        self.clockLabel.setText("Default clock speed (0 = clock stopped): ")
        self.clockGrid.addWidget(self.clockLabel, 0, 0, 1, 1)
        self.settingsGrid.addWidget(self.clockGroupBox, 1, 0, 1, 1)
        # -+++++++------------------ the log group ------------------+++++++- #
        self.logGroupBox = QGroupBox(self)
        self.logGroupBox.setTitle("Log")
        self.logGrid = QGridLayout(self.logGroupBox)
        # -+++++++-------------- the log outputs group --------------+++++++- #
        self.logOutputsGroupBox = QGroupBox(self.logGroupBox)
        self.logOutputsGroupBox.setCheckable(False)
        self.logOutputsGroupBox.setTitle("Log outputs")
        self.logOutputsGrid = QGridLayout(self.logOutputsGroupBox)
        ##################### LOG OUTPUT CHECK BOX OBJECT #####################
        self.GUICheckBox = logOutputCheckBox(
            self.logOutputsGroupBox, self.config, 'gui', 'GUI')
        #######################################################################
        self.logOutputsGrid.addWidget(self.GUICheckBox, 0, 0, 1, 1)
        ##################### LOG OUTPUT CHECK BOX OBJECT #####################
        self.stdoutCheckBox = logOutputCheckBox(
            self.logOutputsGroupBox, self.config, 'stdout', 'stdout')
        #######################################################################
        self.logOutputsGrid.addWidget(self.stdoutCheckBox, 1, 0, 1, 1)
        ##################### LOG OUTPUT CHECK BOX OBJECT #####################
        self.fileCheckBox = logOutputCheckBox(
            self.logOutputsGroupBox, self.config, 'file', 'File')
        #######################################################################
        self.logOutputsGrid.addWidget(self.fileCheckBox, 2, 0, 1, 1)
        self.logGrid.addWidget(self.logOutputsGroupBox, 1, 0, 1, 1)
        self.settingsGrid.addWidget(self.logGroupBox, 0, 0, 1, 1)
        # -+++++++---------------- the GUI log group ----------------+++++++- #
        self.logRecordsGroupBox = QGroupBox(self.logGroupBox)
        self.logRecordsGroupBox.setTitle("GUI Log records")
        self.logRecordsGrid = QGridLayout(self.logRecordsGroupBox)
        self.logRecordsLabel = QLabel(self.logRecordsGroupBox)
        self.logRecordsLabel.setText("Print a log message upon:")
        self.logRecordsGrid.addWidget(self.logRecordsLabel, 0, 0, 1, 1)
        ####################### LOG RECORDS TREE OBJECT #######################
        self.logRecordsTree = logRecordsTree(
            self.logRecordsGroupBox, self.config)
        #######################################################################
        self.logRecordsGrid.addWidget(self.logRecordsTree, 1, 0, 1, 1)
        self.logGrid.addWidget(self.logRecordsGroupBox, 1, 1, 1, 1)
        # -+++++++--------------- the appearance group --------------+++++++- #
        self.appearanceGroupBox = QGroupBox(self)
        self.appearanceGroupBox.setTitle("Appearance")
        self.appearanceGrid = QGridLayout(self.appearanceGroupBox)
        self.circBgColorLabel = QLabel(self.appearanceGroupBox)
        self.circBgColorLabel.setText("Circuit background color:")
        self.appearanceGrid.addWidget(
            self.circBgColorLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        ######################## COLOR SELECTOR OBJECT ########################
        self.colorButton0 = ColorSelectorButton(
            self.appearanceGroupBox, self.config, 'circ_bg_color', 'choose...')
        #######################################################################
        self.appearanceGrid.addWidget(self.colorButton0, 0, 1, 1, 1)
        leftSpace = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.appearanceGrid.addItem(leftSpace, 0, 4, 1, 1)
        self.line = QFrame(self.appearanceGroupBox)
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.appearanceGrid.addWidget(self.line, 0, 3, 1, 1)
        ######################## COLOR SELECTOR OBJECT ########################
        self.colorButton1 = ColorSelectorButton(
            self.appearanceGroupBox, self.config, 'log_bg_color', 'choose...')
        #######################################################################
        self.appearanceGrid.addWidget(self.colorButton1, 0, 6, 1, 1)
        self.GUIBgColorLabel = QLabel(self.appearanceGroupBox)
        self.GUIBgColorLabel.setText("GUI log background color:")
        self.appearanceGrid.addWidget(self.GUIBgColorLabel, 0, 5, 1, 1)
        rightSpace = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.appearanceGrid.addItem(rightSpace, 0, 2, 1, 1)
        self.settingsGrid.addWidget(self.appearanceGroupBox, 2, 0, 1, 1)
        # -+++++++---------------- the Close button -----------------+++++++- #
        self.closeButtonBox = QDialogButtonBox(self)
        self.closeButtonBox.setStandardButtons(QDialogButtonBox.Close)
        self.settingsGrid.addWidget(self.closeButtonBox, 3, 0, 1, 1)

    def saveConfigFile(self, mode='w+'):
        """Write the in-memory config structure <config> in the config
        file <configFile>. mode 'w+' for updating but not superseding.
        """
        with open(self.config.configFile, mode) as configfile:
            self.config.write(configfile)

    @QtCore.Slot()
    def saveAndClose(self):
        """Saves the config file and closes the widget."""
        self.saveConfigFile()
        self.configSaved.emit()
        self.close()

    @QtCore.Slot()
    def keyPressEvent(self, e):
        """Escape key close the window."""
        if e.key() == QtCore.Qt.Key_Escape:
            self.saveAndClose()
