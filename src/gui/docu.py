#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore, QtHelp


class HelpTextBrowser(QtGui.QTextBrowser):
    """A simple overload to enable communication between the help
    engine and a QTextBrowser.
    """

    def __init__(self, helpEngine):
        super(HelpTextBrowser, self).__init__()
        self.helpEngine = helpEngine

    def loadResource(self, type, url):
        if url.scheme() == "qthelp":
            return self.helpEngine.fileData(url)
        else:
            return super(HelpTextBrowser, self).loadResource(type, url)


class HelpDockWidget(QtGui.QDockWidget):
    """A dock widget integrating all the necessary widgets for our help
    and documentation system.
    """

    def __init__(self, title):
        super(HelpDockWidget, self).__init__(title)
        # http://doc.qt.digia.com/qq/qq28-qthelp.html
        helpEngine = QtHelp.QHelpEngine('collection.qhc')
        print(helpEngine.setupData())
        helpPanel = QtGui.QSplitter(QtCore.Qt.Vertical)
        helpBrowser = HelpTextBrowser(helpEngine)
        helpEngine.contentWidget().linkActivated.connect(helpBrowser.setSource)
        helpPanel.insertWidget(0, helpEngine.contentWidget())
        helpPanel.insertWidget(1, helpBrowser)
        helpPanel.setStretchFactor(1, 1)
        self.setWidget(helpPanel)
