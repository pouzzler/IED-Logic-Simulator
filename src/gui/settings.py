#!/usr/bin/env python3
# coding=utf-8

from configparser import ConfigParser
from PySide.QtCore import Qt
from PySide.QtGui import (
    QCheckBox, QColor, QColorDialog, QDialog, QDoubleSpinBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QPalette, QPushButton, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout)
from .util import boolToCheckState, checkStateToBool, filePath


class Settings(ConfigParser):
    def __init__(self):
        super(ConfigParser, self).__init__()
        self.configFile = filePath('settings.cfg')
        self.read(self.configFile)


class SettingsDialog(QDialog):
    """A dialog for choosing clock speed, log verbosity and GUI colors"""

    def __init__(self, mainwindow, config):
        super(SettingsDialog, self).__init__()
        self.setWindowTitle(self.str_title)
        self.mainwindow = mainwindow
        self.config = config

        logOutputs = QGroupBox(self.str_logHandlers)
        logOutputsLayout = QVBoxLayout()
        logOutputs.setLayout(logOutputsLayout)

        logToGui = QCheckBox(self.str_logToGui)
        logToGui.setChecked(self.config.getboolean('LogHandlers', 'gui'))
        logToGui.stateChanged.connect(
            lambda: self.chooseHandler(logToGui, 'gui'))
        logOutputsLayout.addWidget(logToGui)

        logtoStdout = QCheckBox(self.str_logToStdout)
        logtoStdout.setChecked(self.config.getboolean('LogHandlers', 'stdout'))
        logtoStdout.stateChanged.connect(
            lambda: self.chooseHandler(logtoStdout, 'stdout'))
        logOutputsLayout.addWidget(logtoStdout)

        logToFile = QCheckBox(self.str_logToFile)
        logToFile.setChecked(self.config.getboolean('LogHandlers', 'file'))
        logToFile.stateChanged.connect(
            lambda: self.chooseHandler(logToFile, 'file'))
        logOutputsLayout.addWidget(logToFile)

        logVerbosity = QGroupBox(self.str_logVerbosity)
        logVerbosityLayout = QHBoxLayout()
        logVerbosity.setLayout(logVerbosityLayout)
        self.verbosityOptions = QTreeWidget()
        self.verbosityOptions.header().setVisible(False)
        for k, v in self.str_treeItems.items():
            node = QTreeWidgetItem(self.verbosityOptions, [k])
            node.setCheckState(0, Qt.Checked)
            if isinstance(v, str):
                node.setText(1, v)
                node.setCheckState(
                    0, boolToCheckState(
                        self.config.getboolean('LogVerbosity', v)))
            else:
                for key, val in v.items():
                    item = QTreeWidgetItem(node, [key, val])
                    item.setCheckState(
                        0, boolToCheckState(
                            self.config.getboolean('LogVerbosity', val)))
        self.verbosityOptions.itemChanged.connect(self.chooseVerbosity)
        logVerbosityLayout.addWidget(self.verbosityOptions)

        clock = QGroupBox(self.str_clock)
        clockLayout = QHBoxLayout()
        clock.setLayout(clockLayout)
        clockLayout.addWidget(QLabel(self.str_clockSpeed))
        spin = QDoubleSpinBox()
        spin.setValue(self.config.getfloat('Clock', 'speed'))
        clockLayout.addWidget(spin)

        appearance = QGroupBox(self.str_appearance)
        appearanceLayout = QHBoxLayout()
        appearance.setLayout(appearanceLayout)
        appearanceLayout.addWidget(QLabel(self.str_circBgColor))
        circBgBtn = QPushButton(self.str_choose)
        circBgBtn.setPalette(QPalette(
            QColor(self.config.get('Appearance', 'circ_bg_color'))))
        circBgBtn.clicked.connect(
            lambda: self.chooseColor(circBgBtn, 'circ_bg_color'))
        appearanceLayout.addWidget(circBgBtn)
        appearanceLayout.addWidget(QLabel(self.str_logBgColor))
        logBgBtn = QPushButton(self.str_choose)
        logBgBtn.setPalette(QPalette(
            QColor(self.config.get('Appearance', 'log_bg_color'))))
        logBgBtn.clicked.connect(
            lambda: self.chooseColor(logBgBtn, 'log_bg_color'))
        appearanceLayout.addWidget(logBgBtn)
        close = QPushButton(self.str_close)
        close.clicked.connect(self.closeAndApply)
        layout = QGridLayout(self)
        layout.addWidget(logOutputs, 0, 0, 1, 1)
        layout.addWidget(logVerbosity, 0, 1, 1, 1)
        layout.addWidget(clock, 1, 0, 1, 2)
        layout.addWidget(appearance, 2, 0, 1, 2)
        layout.addWidget(close, 3, 1, 1, 1)
        self.setLayout(layout)

    def chooseColor(self, button, option):
        """The user modifies an UI background color."""
        color = QColorDialog.getColor()
        if color.isValid():
            button.setPalette(QPalette(color))
            self.config.set('Appearance', option, color.name())

    def chooseHandler(self, checkbox, option):
        self.config.set('LogHandlers', option, str(checkbox.isChecked()))

    def chooseVerbosity(self, item):
        option = item.text(1)
        if option:
            self.config.set('LogVerbosity', option, str(
                checkStateToBool(item.checkState(0))))
            if isinstance(item.parent(), QTreeWidgetItem):
                count = item.parent().childCount()
                for i in range(item.parent().childCount()):
                    if not checkStateToBool(
                            item.parent().child(i).checkState(0)):
                        count = count - 1
                self.verbosityOptions.blockSignals(True)
                if count == item.parent().childCount():
                    item.parent().setCheckState(0, Qt.Checked)
                elif count == 0:
                    item.parent().setCheckState(0, Qt.Unchecked)
                else:
                    item.parent().setCheckState(0, Qt.PartiallyChecked)
                self.verbosityOptions.blockSignals(False)
        else:
            for i in range(item.childCount()):
                self.verbosityOptions.blockSignals(True)
                item.child(i).setCheckState(0, item.checkState(0))
                self.config.set(
                    'LogVerbosity', item.child(i).text(1),
                    str(checkStateToBool(item.checkState(0))))
                self.verbosityOptions.blockSignals(False)

    def closeAndApply(self):
        self.mainwindow.setSettings()
        with open(self.config.configFile, 'w+') as f:
            self.config.write(f)
        self.close()
