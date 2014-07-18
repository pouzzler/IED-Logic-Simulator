#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore


class SettingsDialog(QtGui.QDialog):
    """A dialog for choosing clock speed, log verbosity and GUI colors"""

    def __init__(self):
        super(SettingsDialog, self).__init__()
        
        self.setWindowTitle("Settings")
        
        logOutputs = QtGui.QGroupBox("Output logs to :")
        logOutputsLayout = QtGui.QVBoxLayout()
        logOutputs.setLayout(logOutputsLayout)
        logToGui = QtGui.QCheckBox("GUI")
        logOutputsLayout.addWidget(logToGui)
        logToStdout = QtGui.QCheckBox("stdout")
        logOutputsLayout.addWidget(logToStdout)
        logToFile = QtGui.QCheckBox("File")
        logOutputsLayout.addWidget(logToFile)

        logVerbosity = QtGui.QGroupBox("Select log verbosity :")
        logVerbosityLayout = QtGui.QHBoxLayout()
        logVerbosity.setLayout(logVerbosityLayout)
        verbosityOptions = QtGui.QTreeWidget()   
        for k, v in {   
                'Item addition & removal' : [
                    'I/O added', 'Circuit added', 'I/O removed',
                    'Circuit removed', 'Detailed remove'],
                'I/O (dis)connection' : [],
                'I/O value modification' : [
                    'Inputs', 'Outputs']}.items() :
            node = QtGui.QTreeWidgetItem(verbosityOptions, [k])
            node.setCheckState(0, QtCore.Qt.Checked)
            for val in v :
                item = QtGui.QTreeWidgetItem(node, [val])
                item.setCheckState(0, QtCore.Qt.Checked)  
        logVerbosityLayout.addWidget(verbosityOptions)

        clock = QtGui.QGroupBox("Clock :")
        clockLayout = QtGui.QHBoxLayout()
        clock.setLayout(clockLayout)
        clockLayout.addWidget(
            QtGui.QLabel("Default Clock Speed (0 = clock stopped)"))
        spin = QtGui.QDoubleSpinBox()
        clockLayout.addWidget(spin)

        appearance = QtGui.QGroupBox("Appearance :")
        appearanceLayout = QtGui.QHBoxLayout()
        appearance.setLayout(appearanceLayout)
        appearanceLayout.addWidget(
            QtGui.QLabel("Circuit background color"))
        appearanceLayout.addWidget(
            QtGui.QLabel("Logs background color"))

        layout = QtGui.QGridLayout(self)
        layout.addWidget(logOutputs, 0, 0, 1, 1)
        layout.addWidget(logVerbosity, 0, 1, 1, 1)
        layout.addWidget(clock, 1, 0, 1, 2)
        layout.addWidget(appearance, 2, 0, 1, 2)
        self.setLayout(layout)
