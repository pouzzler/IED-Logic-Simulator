#!/usr/bin/env python3
# coding=utf-8

"""There is an error message while checking or unchecking some QCheckBox
in the settings window (Gtk-CRITICAL). This is a bug from Qt4. Thos only
occure with app.setStyle() set to "gtk". Please refer to:
https://bugs.launchpad.net/ubuntu/+source/qt4-x11/+bug/805303 .
"""

import sys
from PySide.QtGui import QApplication
from gui.mainwindow import MainWindow
from gui.settings import configFile


# La boucle principale du programme
app = QApplication(sys.argv)
app.setStyle("plastique")
win = MainWindow()
sys.exit(app.exec_())
