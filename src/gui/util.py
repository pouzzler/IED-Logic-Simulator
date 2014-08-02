from os.path import dirname, realpath
from PySide.QtCore import Qt


def boolToCheckState(b):
    """Translates booleans to Qt.CheckState."""
    return Qt.Unchecked if not b else Qt.Checked


def checkStateToBool(state):
    """Translates Qt.CheckState to booleans."""
    return False if state == Qt.Unchecked else True


def filePath(relPath):
    """Returns the absolute path of app data files."""
    return dirname(realpath(__file__)) + '/../../' + relPath
