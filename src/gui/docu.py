#!/usr/bin/env python3
# coding=utf-8

from PySide.QtCore import Qt
from PySide.QtGui import QDockWidget, QSplitter, QTextBrowser
from PySide.QtHelp import QHelpEngine
from .util import filePath


class HelpTextBrowser(QTextBrowser):
    """Overload QTextBrowser to enable communication with QHelpEngine."""

    def __init__(self, helpEngine):
        super(HelpTextBrowser, self).__init__()
        self.helpEngine = helpEngine

    def loadResource(self, type, url):
        if url.scheme() == "qthelp":
            return self.helpEngine.fileData(url)
        else:
            return super(HelpTextBrowser, self).loadResource(type, url)


class HelpDockWidget(QDockWidget):
    """A dock widget providing inline application help."""

    def __init__(self):
        super(HelpDockWidget, self).__init__(self.str_helpDockTitle)
        helpEngine = QHelpEngine(filePath('help/collection.qhc'))
        helpEngine.setupData()
        helpPanel = QSplitter(Qt.Vertical)
        helpBrowser = HelpTextBrowser(helpEngine)
        helpEngine.contentWidget().linkActivated.connect(helpBrowser.setSource)
        helpPanel.insertWidget(0, helpEngine.contentWidget())
        helpPanel.insertWidget(1, helpBrowser)
        helpPanel.setStretchFactor(1, 1)
        self.setWidget(helpPanel)
