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


class SettingsWidget(QtGui.QWidget):
    """A widget for cotroling some settings of the GUI and the engine such as:
    * clock speed
    * log records and outputs
    * some GUI colors values
    """
    
    def __init__(self):
        super(SettingsWidget, self).__init__()
        self.initUI()
        
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
        #         -+++++++- the log records selector (tree) -+++++++-         #
        self.logRecordsTree = QtGui.QTreeWidget(self.logRecordsGroupBox)
        self.logRecordsTree.setFrameShape(QtGui.QFrame.StyledPanel)
        self.logRecordsTree.setTabKeyNavigation(False)
        self.logRecordsTree.setAlternatingRowColors(False)
        self.logRecordsTree.setAnimated(True)
        self.logRecordsTree.setObjectName("logRecordsTree")
        #                 -+-------- selector items -------+-                 #
        item0 = QtGui.QTreeWidgetItem(self.logRecordsTree)
        item0.setCheckState(0, QtCore.Qt.Checked)
        item0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsTristate)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item0 = QtGui.QTreeWidgetItem(self.logRecordsTree)
        item0.setCheckState(0, QtCore.Qt.Checked)
        item0 = QtGui.QTreeWidgetItem(self.logRecordsTree)
        item0.setCheckState(0, QtCore.Qt.Checked)
        item0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsTristate)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item1 = QtGui.QTreeWidgetItem(item0)
        item1.setCheckState(0, QtCore.Qt.Checked)
        item0 = QtGui.QTreeWidgetItem(self.logRecordsTree)
        item0.setCheckState(0, QtCore.Qt.Unchecked)
        item0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable)
        #                 -+---- add items to the tree ----+-                 #
        self.logRecordsTree.headerItem().setText(0, "1")
        __sortingEnabled = self.logRecordsTree.isSortingEnabled()
        self.logRecordsTree.setSortingEnabled(False)
        self.logRecordsTree.topLevelItem(0).setText(
            0,
            "Adding / removing an object")
        self.logRecordsTree.topLevelItem(0).child(0).setText(
            0,
            "Adding an I/O")
        self.logRecordsTree.topLevelItem(0).child(1).setText(
            0,
            "Adding a circuit")
        self.logRecordsTree.topLevelItem(0).child(2).setText(
            0,
            "Removing an I/O")
        self.logRecordsTree.topLevelItem(0).child(3).setText(
            0,
            "Removing a circuit")
        self.logRecordsTree.topLevelItem(0).child(4).setText(
            0,
            "Detailed remove")
        self.logRecordsTree.topLevelItem(1).setText(
            0,
            "Connecting / disconnecting I/O")
        self.logRecordsTree.topLevelItem(2).setText(
            0,
            "Changinf an I/O value")
        self.logRecordsTree.topLevelItem(2).child(0).setText(
            0,
            "Inputs changes")
        self.logRecordsTree.topLevelItem(2).child(1).setText(
            0,
            "Outputs changes")
        self.logRecordsTree.topLevelItem(3).setText(
            0,
            "Advices (not yet implemented)")
        self.logRecordsTree.setSortingEnabled(__sortingEnabled)
        #                 -+--------- tree header ---------+-                 #
        self.logRecordsTree.header().setVisible(False)
        self.logRecordsTree.header().setDefaultSectionSize(100)
        self.logRecordsTree.header().setHighlightSections(False)
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
        self.appearanceGrid.addWidget(self.circBgColorLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.colorButton0 = QtGui.QToolButton(self.appearanceGroupBox)
        self.colorButton0.setCheckable(False)
        self.colorButton0.setChecked(False)
        self.colorButton0.setAutoRaise(False)
        self.colorButton0.setArrowType(QtCore.Qt.NoArrow)
        self.colorButton0.setObjectName("colorButton0")
        self.colorButton0.setToolTip("<html><head/><body><p>Show a dialog for selecting a color.</p></body></html>")
        self.colorButton0.setText("choose...")
        self.appearanceGrid.addWidget(self.colorButton0, 0, 1, 1, 1)
        leftSpace = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
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
        rightSpace = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.appearanceGrid.addItem(rightSpace, 0, 2, 1, 1)
        self.settingsGrid.addWidget(self.appearanceGroupBox, 2, 0, 1, 1)
        # -+++++++---------------- the Close button -----------------+++++++- #
        self.closeButtonBox = QtGui.QDialogButtonBox(self)
        self.closeButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.closeButtonBox.setObjectName("closeButtonBox")
        self.closeButtonBox.clicked.connect(self.close)
        self.settingsGrid.addWidget(self.closeButtonBox, 3, 0, 1, 1)
        
    def keyPressEvent(self, e):
        """Escape key close the window."""
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
