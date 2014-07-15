#!/usr/bin/env python3
# coding=utf-8

"""
####################################
## Widget for the settings window ##
####################################

This widget is called when clicking on Edit -> Settings....
The window contains some log, appearance and clock management options.
"""

from PySide import QtCore, QtGui
import sys
import configparser


class TreeWidgetItem(QtGui.QTreeWidgetItem):
    """We need to subclass QTreeWidget to reimplement setData()
    and emiting a custom signal of the logRecordsTree class
    when the item check state is modified.
    """
    def setData(self, col, role, value):
        state = self.checkState(col)
        QtGui.QTreeWidgetItem.setData(self, col, role, value)
        if role == QtCore.Qt.CheckStateRole and state != self.checkState(col):
            treewidget = self.treeWidget()
            if treewidget is not None:
                treewidget.treeItemChecked.emit(self, col)

    def setCheckStateFromOption(self, opVal):
        """Set the checkState of the item according to the boolean <opVal>"""
        if opVal is True:
            self.setCheckState(0, QtCore.Qt.Checked)
        else:
            self.setCheckState(0, QtCore.Qt.Unchecked)


class logRecordsTree(QtGui.QTreeWidget):
    """We need to subclass QTreeWidget to define a new custom signal
    in the class. This signal is emitted by the TreeWidgetItem and
    connecting to handleItemChecked() which process the signal.
    """
    treeItemChecked = QtCore.Signal(object, int)

    def __init__(self, parent, configFile, config):
        """Get the config file <configFile> and the config dictionary
        <config> from the parent class becaus createLogRecordsTreeItem
        need to access it and handleItemChecked need to modify it.
        Also define the config section used by the class.
        """
        QtGui.QTreeWidget.__init__(self, parent)
        self.config = config
        self.configFile = configFile
        self.section = 'GUILogRecords'
        self.initTree()
        self.treeItemChecked.connect(self.handleItemChecked)

    def initTree(self):
        # -+++++++----------------- tree properties -----------------+++++++- #
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setTabKeyNavigation(False)
        self.setAlternatingRowColors(False)
        self.setAnimated(True)
        self.setObjectName("logRecordsTree")
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
        item.section = self.section
        item.option = option
        if option:
            try:
                opVal = self.config.getboolean(self.section, option)
                item.setCheckStateFromOption(opVal)
            except:
                sys.stdout.write("invalid option '%s'\n" % (option))
        return item

    @QtCore.Slot()
    def handleItemChecked(self, item, column):
        """This slot is triggered by the emission of the treeItemChecked
        signal. The slot update the value of the config dictionary option
        if the item is managed by an option.
        """
        if not item.section or not item.option:
            return
        # it would be easier to toggle value but it's impossible with strings
        v = 'True' if item.checkState(column) == QtCore.Qt.Checked else 'False'
        self.config.set(item.section, item.option, v)


class SettingsWidget(QtGui.QWidget):
    """A widget for cotroling some settings of the GUI and the engine such as:
    * clock speed
    * log records and outputs
    * some GUI colors values
    """
    def __init__(self, configFile):
        """Init the parent class, the config dictionary and the window."""
        super(SettingsWidget, self).__init__()
        self.importConfigFromFile(configFile)
        self.initUI()

    def importConfigFromFile(self, configFile):
        """Create a config dictionary from <configFile>."""
        self.configFile = configFile
        self.config = configparser.ConfigParser()
        self.config.read(configFile)

    def initUI(self):
        # -+++++++--------------- the settings window ---------------+++++++- #
        self.setObjectName("Settings window")
        self.setWindowTitle("Settings")
        self.resize(562, 466)
        self.settingsGrid = QtGui.QGridLayout(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.settingsGrid.setObjectName("gridLayout")
        # -+++++++----------------- the clock group -----------------+++++++- #
        self.clockGroupBox = QtGui.QGroupBox(self)
        self.clockGroupBox.setObjectName("groupBox")
        self.clockGroupBox.setTitle("Clock")
        self.clockGrid = QtGui.QGridLayout(self.clockGroupBox)
        self.clockGrid.setObjectName("clockGrid")
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.clockGroupBox)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.clockGrid.addWidget(self.doubleSpinBox, 0, 1, 1, 1)
        self.secLabel = QtGui.QLabel(self.clockGroupBox)
        self.secLabel.setObjectName("secLabel")
        self.secLabel.setText("seconds")
        self.clockGrid.addWidget(self.secLabel, 0, 2, 1, 1)
        self.clockLabel = QtGui.QLabel(self.clockGroupBox)
        self.clockLabel.setObjectName("label")
        self.clockLabel.setText("Dafault clock speed (0 = clock stoped): ")
        self.clockGrid.addWidget(self.clockLabel, 0, 0, 1, 1)
        self.settingsGrid.addWidget(self.clockGroupBox, 1, 0, 1, 1)
        # -+++++++------------------ the log group ------------------+++++++- #
        self.logGroupBox = QtGui.QGroupBox(self)
        self.logGroupBox.setObjectName("logGroupBox")
        self.logGroupBox.setTitle("Log")
        self.logGrid = QtGui.QGridLayout(self.logGroupBox)
        self.logGrid.setObjectName("logGrid")
        # -+++++++-------------- the log outputs group --------------+++++++- #
        self.logOutputsGroupBox = QtGui.QGroupBox(self.logGroupBox)
        self.logOutputsGroupBox.setCheckable(False)
        self.logOutputsGroupBox.setObjectName("logOutputsGroupBox")
        self.logOutputsGroupBox.setTitle("Log outputs")
        self.logOutputsGrid = QtGui.QGridLayout(self.logOutputsGroupBox)
        self.logOutputsGrid.setObjectName("logOutputsGrid")
        self.GUICheckBox = QtGui.QCheckBox(self.logOutputsGroupBox)
        self.GUICheckBox.setObjectName("GUICheckBox")
        self.GUICheckBox.setText("GUI")
        self.logOutputsGrid.addWidget(self.GUICheckBox, 0, 0, 1, 1)
        self.stdoutCheckBox = QtGui.QCheckBox(self.logOutputsGroupBox)
        self.stdoutCheckBox.setObjectName("stdoutCheckBox")
        self.stdoutCheckBox.setText("stdout")
        self.logOutputsGrid.addWidget(self.stdoutCheckBox, 1, 0, 1, 1)
        self.fileCheckBox = QtGui.QCheckBox(self.logOutputsGroupBox)
        self.fileCheckBox.setObjectName("fileCheckBox")
        self.fileCheckBox.setText("File")
        self.logOutputsGrid.addWidget(self.fileCheckBox, 2, 0, 1, 1)
        self.logGrid.addWidget(self.logOutputsGroupBox, 1, 0, 1, 1)
        self.settingsGrid.addWidget(self.logGroupBox, 0, 0, 1, 1)
        # -+++++++---------------- the GUI log group ----------------+++++++- #
        self.logRecordsGroupBox = QtGui.QGroupBox(self.logGroupBox)
        self.logRecordsGroupBox.setObjectName("logRecordsGroupBox")
        self.logRecordsGroupBox.setTitle("GUI Log records")
        self.logRecordsGrid = QtGui.QGridLayout(self.logRecordsGroupBox)
        self.logRecordsGrid.setObjectName("logRecordsGrid")
        self.logRecordsLabel = QtGui.QLabel(self.logRecordsGroupBox)
        self.logRecordsLabel.setObjectName("logRecordsLabel")
        self.logRecordsLabel.setText("Print a log message upon:")
        self.logRecordsGrid.addWidget(self.logRecordsLabel, 0, 0, 1, 1)
        self.logRecordsTree = logRecordsTree(
            self.logRecordsGroupBox, self.configFile, self.config)
        self.logRecordsGrid.addWidget(self.logRecordsTree, 1, 0, 1, 1)
        self.logGrid.addWidget(self.logRecordsGroupBox, 1, 1, 1, 1)
        # -+++++++--------------- the appearance group --------------+++++++- #
        self.appearanceGroupBox = QtGui.QGroupBox(self)
        self.appearanceGroupBox.setObjectName("appearanceGroupBox")
        self.appearanceGroupBox.setTitle("Appearance")
        self.appearanceGrid = QtGui.QGridLayout(self.appearanceGroupBox)
        self.appearanceGrid.setObjectName("appearanceGrid")
        self.circBgColorLabel = QtGui.QLabel(self.appearanceGroupBox)
        self.circBgColorLabel.setObjectName("circBgColorLabel")
        self.circBgColorLabel.setText("Circuit background color:")
        self.appearanceGrid.addWidget(
            self.circBgColorLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.colorButton0 = QtGui.QToolButton(self.appearanceGroupBox)
        self.colorButton0.setCheckable(False)
        self.colorButton0.setChecked(False)
        self.colorButton0.setAutoRaise(False)
        self.colorButton0.setArrowType(QtCore.Qt.NoArrow)
        self.colorButton0.setObjectName("colorButton0")
        self.colorButton0.setToolTip(
            "<html><head/><body><p>Show a dialog for selecting a "
            "color.</p></body></html>")
        self.colorButton0.setText("choose...")
        self.appearanceGrid.addWidget(self.colorButton0, 0, 1, 1, 1)
        leftSpace = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.appearanceGrid.addItem(leftSpace, 0, 4, 1, 1)
        self.line = QtGui.QFrame(self.appearanceGroupBox)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.appearanceGrid.addWidget(self.line, 0, 3, 1, 1)
        self.colorButton1 = QtGui.QToolButton(self.appearanceGroupBox)
        self.colorButton1.setObjectName("colorButton1")
        self.colorButton1.setText("choose...")
        self.appearanceGrid.addWidget(self.colorButton1, 0, 6, 1, 1)
        self.GUIBgColorLabel = QtGui.QLabel(self.appearanceGroupBox)
        self.GUIBgColorLabel.setObjectName("GUIBgColorLabel")
        self.GUIBgColorLabel.setText("GUI log background color:")
        self.appearanceGrid.addWidget(self.GUIBgColorLabel, 0, 5, 1, 1)
        rightSpace = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.appearanceGrid.addItem(rightSpace, 0, 2, 1, 1)
        self.settingsGrid.addWidget(self.appearanceGroupBox, 2, 0, 1, 1)
        # -+++++++---------------- the Close button -----------------+++++++- #
        self.closeButtonBox = QtGui.QDialogButtonBox(self)
        self.closeButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.closeButtonBox.setObjectName("closeButtonBox")
        self.closeButtonBox.clicked.connect(self.saveAndClose)
        self.settingsGrid.addWidget(self.closeButtonBox, 3, 0, 1, 1)

    def save_config_file(self, mode='w+'):
        """Write the in-memory config structure <config> in the config
        file <configFile>. mode 'w+' for updating but not superseding.
        """
        with open(self.configFile, mode) as configfile:
            self.config.write(configfile)

    @QtCore.Slot()
    def saveAndClose(self):
        """Saves the config file and closes the widget."""
        self.save_config_file()
        self.close()

    @QtCore.Slot()
    def keyPressEvent(self, e):
        """Escape key close the window."""
        if e.key() == QtCore.Qt.Key_Escape:
            self.saveAndClose()
