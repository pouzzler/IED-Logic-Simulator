#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui


class SettingsDialog(QtGui.QDialog):
    """Manages clock speed, log functionality and GUI colors"""

    def __init__(self):
        super(SettingsDialog, self).__init__()
        
        logOutputs = QtGui.QGroupBox("Output logs to :")
        logOutputsLayout = QtGui.QVBoxLayout()
        logOutputs.setLayout(logOutputsLayout)
        logToGui = QtGui.QCheckBox("GUI")
        logOutputsLayout.addWidget(logToGui)
        logToStdout = QtGui.QCheckBox("stdout")
        logOutputsLayout.addWidget(logToStdout)
        logToFile = QtGui.QCheckBox("File")
        logOutputsLayout.addWidget(logToFile)
        
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
        
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(logOutputs)
        layout.addWidget(clock)
        layout.addWidget(appearance)
        self.setLayout(layout)
