from os.path import dirname, realpath
from PySide.QtCore import Qt


def filePath(relPath):
    """Returns the absolute path of a path relative to the app's
    installation folder.
    """
    return dirname(realpath(__file__)) + '/../../' + relPath


def checkStateToBool(state):
    return False if state == Qt.Unchecked else True


def boolToCheckState(b):
    return Qt.Unchecked if not b else Qt.Checked
