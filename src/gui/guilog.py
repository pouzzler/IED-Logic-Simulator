#!/usr/bin/env python3
# coding=utf-8


from PySide import QtGui, QtCore


class LoggerTextEdit(QtGui.QTextBrowser):
    """A multiline text field that receives log messages."""

    def __init__(self):
        super(LoggerTextEdit, self).__init__()
        self.pal = QtGui.QPalette()
        #~ bgc = QtGui.QColor(0, 0, 0)
        #~ self.pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        self.pal.setColor(QtGui.QPalette.Text, textc)
        self.setPalette(self.pal)

    def write(self, text):
        """Log handlers call a write() method."""
        self.insertPlainText(text)
