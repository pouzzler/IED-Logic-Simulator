#!/usr/bin/env python3
# coding=utf-8

import sys
from PySide.QtGui import QApplication
from gui.mainwindow import MainWindow


# La boucle principale du programme
app = QApplication(sys.argv)
win = MainWindow()
sys.exit(app.exec_())
