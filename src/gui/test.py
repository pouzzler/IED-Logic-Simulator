#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from configparser import ConfigParser


class SettingsDialog(QtGui.QDialog):
    """A dialog for choosing clock speed, log verbosity and GUI colors"""

    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.setWindowTitle("Settings")

        self.configFile = "settings.cfg"
        self.config = ConfigParser()
        self.config.read(self.configFile)

        logOutputs = QtGui.QGroupBox("Output logs to :")
        logOutputsLayout = QtGui.QVBoxLayout()
        logOutputs.setLayout(logOutputsLayout)
        for setting in self.config.options('LogOutputs'):
            box = QtGui.QCheckBox(setting)
            box.setChecked(self.config.getboolean('LogOutputs', setting))
            box.setObjectName(setting)
            box.stateChanged.connect(self.settingsChanged)
            logOutputsLayout.addWidget(box)

        logVerbosity = QtGui.QGroupBox("Select log verbosity :")
        logVerbosityLayout = QtGui.QHBoxLayout()
        logVerbosity.setLayout(logVerbosityLayout)
        verbosityOptions = QtGui.QTreeWidget()
        verbosityOptions.itemClicked.connect(self.settingsChanged)
        for k, v in {
                'Item addition & removal': [
                    'adding_io', 'adding_circ', 'removing_io',
                    'removing_circ', 'detailed_rm'],
                'conn_discon_io': [],
                'I/O value modification': [
                    'input_chang', 'output_chang']}.items():
            node = QtGui.QTreeWidgetItem(verbosityOptions, [k])
            node.setCheckState(0, QtCore.Qt.Checked)
            for val in v:
                item = QtGui.QTreeWidgetItem(node, [val])
                item.setCheckState(
                    0,
                    QtCore.Qt.CheckState.Checked
                        if self.config.getboolean('GUILogRecords', val)
                        else QtCore.Qt.CheckState.Unchecked)
        logVerbosityLayout.addWidget(verbosityOptions)
        
        clock = QtGui.QGroupBox("Clock :")
        clockLayout = QtGui.QHBoxLayout()
        clock.setLayout(clockLayout)
        clockLayout.addWidget(
            QtGui.QLabel("Default Clock Speed (0 = clock stopped)"))
        spin = QtGui.QDoubleSpinBox()
        spin.setValue(self.config.getfloat('Clock', 'speed'))
        spin.valueChanged.connect(self.settingsChanged)
        clockLayout.addWidget(spin)

        appearance = QtGui.QGroupBox("Appearance :")
        appearanceLayout = QtGui.QHBoxLayout()
        appearance.setLayout(appearanceLayout)
        appearanceLayout.addWidget(
            QtGui.QLabel("Circuit background color"))
        cbcButton = QtGui.QPushButton("Select")
        cbcButton.clicked.connect(self.colorDialog)
        cbcButton.setObjectName('circ_bg_color')
        appearanceLayout.addWidget(cbcButton)
        appearanceLayout.addWidget(
            QtGui.QLabel("Logs background color"))
        lbcButton = QtGui.QPushButton("Select")
        lbcButton.clicked.connect(self.colorDialog)
        lbcButton.setObjectName('log_bg_color')
        appearanceLayout.addWidget(lbcButton)

        close = QtGui.QPushButton('Close')
        close.clicked.connect(self.close)
        
        layout = QtGui.QGridLayout(self)
        layout.addWidget(logOutputs, 0, 0, 1, 1)
        layout.addWidget(logVerbosity, 0, 1, 1, 1)
        layout.addWidget(clock, 1, 0, 1, 2)
        layout.addWidget(appearance, 2, 0, 1, 2)
        layout.addWidget(close, 3, 1, 1, 1)
        self.setLayout(layout)

    def settingsChanged(self, item):
        sender = self.sender()
        if isinstance(sender, QtGui.QCheckBox):
            self.config.set(
                'LogOutputs',
                sender.objectName(),
                str(sender.isChecked()))
        elif isinstance(sender, QtGui.QDoubleSpinBox):
            self.config.set('Clock', 'speed', str(sender.value()))
        elif isinstance(sender, QtGui.QTreeWidget):
            sender.blockSignals(True)
            for i in range(item.childCount()):
                self.config.set(
                    'GUILogRecords',
                    item.child(i).text(0),
                    str(bool(item.checkState(0))))
                item.child(i).setCheckState(0, item.checkState(0))
            self.config.set(
                'GUILogRecords', item.text(0), str(bool(item.checkState(0))))
            if isinstance(item.parent(), QtGui.QTreeWidgetItem):
                siblings = [
                    item.parent().child(i).checkState(0) 
                    for i in range(item.parent().childCount())]
                if all(siblings):
                    item.parent().setCheckState(0, QtCore.Qt.CheckState.Checked)
                elif any(siblings):
                    item.parent().setCheckState(0, QtCore.Qt.CheckState.PartiallyChecked)
                else:
                    item.parent().setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            sender.blockSignals(False)
        with open(self.configFile, 'w+') as configfile:
            self.config.write(configfile)

    def colorDialog(self):
        old = QtGui.QColor()
        old.setNamedColor(self.config.get('Appearance', self.sender().objectName()))
        new = QtGui.QColorDialog.getColor()
        color = old if not new.isValid() else new
        self.config.set('Appearance', self.sender().objectName(), color)
        with open(self.configFile, 'w+') as configfile:
            self.config.write(configfile)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Button, color)
        self.sender().setPalette(palette)
        self.sender().setAutoFillBackground(True)
