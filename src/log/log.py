#!/usr/bin/env python3
# coding: utf-8

##############################################################################
## manage the log file, the input on the terminal and on the GUI log Widget ##
##############################################################################

from PySide import QtGui, QtCore
import sys
import logging
from time import gmtime, strftime


#================================= UTILITIES =================================#
def date():
    """Return the current date."""
    return str(strftime("%m:%d:%Y", gmtime()))


def time():
    """Return the current time."""
    return str(strftime("[%H:%M:%S] ", gmtime()))


#====================== CLASS FOR A SPECIAL LOG WIDGET =======================#
class BlackTextBox(QtGui.QTextEdit):
    """A QTextEdit with black background and white foreground."""
    def __init__(self):
        QtGui.QTextEdit.__init__(self)
        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        pal.setColor(QtGui.QPalette.Text, textc)
        self.setPalette(pal)


#============================= CLASS FOR LOGGING =============================#
class Log(QtCore.QObject):
    """Manage the logs by (several tasks can be performed):
    * writing log messages in logfile defined using the 'logging' module
    * writing log messages on stdout (usually a the terminal)
    * emiting a newLogMessage Qt signal carrying the message string
    Depending on the state of self.logfile, self.terminal and self.gui.
    """
    newLogMessage = QtCore.Signal(str)

    def __init__(self, logfilename, logLevel=logging.DEBUG, **kwargs):
        QtCore.QObject.__init__(self)
        self.logfile = kwargs.pop('logfile', True)
        self.terminal = kwargs.pop('terminal', False)
        self.gui = kwargs.pop('gui', False)
        # we must specify the log file
        logging.basicConfig(
            filename=logfilename,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='[%H:%M:%S]',
            level=logLevel)

    def print_message(self, message, level='info'):
        if self.logfile:
            # print in the log file
            eval('logging.%s(message)' % (level,))
        if self.terminal:
            # print in the terminal
            sys.stdout.write(time() + message + '\n')    # or use print()
        if self.gui:
            # emit a signal for printing in a widget
            self.sendLogMessage(time() + message)

    @QtCore.Slot()
    def sendLogMessage(self, message):
        self.newLogMessage.emit(message)

    def toggle_gui_signal(self, state):
        self.gui = state

    def toggle_terminal_output(self, state):
        self.terminal = state

    def toggle_logfile_output(self, state):
        self.logfile = state
