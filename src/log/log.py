#!/usr/bin/env python3
# coding: utf-8

##############################################################################
## manage the log file, the input on the terminal and on the GUI log Widget ##
##############################################################################

from PySide import QtCore
import sys
import logging
from time import gmtime, strftime


def time():
    return str('[' + strftime("%H:%M:%S", gmtime()) + '] ')


#============================= CLASS FOR LOGGING =============================#
class Log(QtCore.QObject):
    newLogMessage = QtCore.Signal(str)

    def __init__(self, mode, level=logging.info):
        QtCore.QObject.__init__(self)
        self.mode = mode
        self.level = level

    def print_message(self, message):
        # print in the log file
        logging.info(message)
        if self.mode is 'terminal':
            # print in the terminal
            sys.stdout.write(time() + message + '\n')    # or use print()
        if self.mode is 'gui':
            # emit a signal for printing in a widget
            self.sendLogMessage(time() + message)

    @QtCore.Slot()
    def sendLogMessage(self, message):
        self.newLogMessage.emit(message)


#================================= LOG FILE ==================================#
logging.basicConfig(
    filename='simulator.log',
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='[%H:%M:%S]',
    level=logging.DEBUG)
