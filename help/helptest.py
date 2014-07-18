#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore, QtHelp


import sys
from PySide.QtGui import QApplication

class HelpTextBrowser(QtGui.QTextBrowser):
    
    def __init__(self, helpEngine):
        super(HelpTextBrowser, self).__init__()
        self.helpEngine = helpEngine
        
    def loadResource(self, type, url):
        if url.scheme() == "qthelp":
            return self.helpEngine.fileData(url)
        else:
            return super(HelpTextBrowser, self).loadResource(type, url)


app = QApplication(sys.argv)
win = QtGui.QMainWindow()

# Le QHelpEngine est un genre de base de donnée qui contient toute l'aide écrite en html.
helpEngine = QtHelp.QHelpEngine('collection.qhc')
# Si ça renvoie False, notre aide est probablement corrompue/mal construite.
# Si ça renvoie True, on peut l'utiliser pour de bon.
helpEngine.setupData()
# Ici je fais un dock contenant un widget contenant l'index
# Et une fenêtre principale contenant le texte du manuel
# Dans notre prog il faudrait ajouter un champ de recherche
# Et il faudrait décider si on veut une fenêtre indépendante pour l'aide
# ou mettre le tout dans un (GROS!) dock
helpDock = QtGui.QDockWidget('Help')
helpDock.setWidget(helpEngine.contentWidget())
win.addDockWidget(QtCore.Qt.LeftDockWidgetArea, helpDock) 

helpBrowser = HelpTextBrowser(helpEngine)
helpEngine.contentWidget().linkActivated.connect(helpBrowser.setSource)

win.setCentralWidget(helpBrowser) 

win.show()
sys.exit(app.exec_())
