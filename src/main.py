#!/usr/bin/env python
# coding=utf-8

import sys
from PySide.QtGui import QApplication
from gui.mainWindow import mainWindow


# La boucle principale du programme
app = QApplication(sys.argv)
win = mainWindow()
sys.exit(app.exec_())
