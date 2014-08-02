#!/usr/bin/env python3
# coding=utf-8

import logging
from PySide.QtGui import QColor, QDockWidget, QPalette, QTextEdit
from engine.simulator import formatter


class LoggerTextEdit(QTextEdit):
    """A multiline text field showing log messages."""

    def __init__(self):
        super(LoggerTextEdit, self).__init__()
        self.pal = QPalette()
        textc = QColor(255, 255, 255)
        self.pal.setColor(QPalette.Text, textc)
        self.setPalette(self.pal)
        self.setReadOnly(True)

    def write(self, text):
        """Simulate LogHandler by having a write() method."""
        self.insertPlainText(text)


class LogDockWidget(QDockWidget):
    """A main window dockable widget showing the app logs."""

    def __init__(self):
        super(LogDockWidget, self).__init__(self.str_logDockTitle)
        self.setWidget(LoggerTextEdit())
        self.handler = logging.StreamHandler(self.widget())
        self.handler.setLevel(logging.DEBUG)
        self.handler.setFormatter(formatter)

    def setBgColor(self, color):
        """Set the background color of the log window."""
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(color))
        self.widget().setPalette(pal)
