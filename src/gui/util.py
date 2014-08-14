from os.path import dirname, realpath
from PySide.QtCore import QPointF, Qt

GRIDSIZE = 10   # pixels


def boolToCheckState(b):
    """Translates booleans to Qt.CheckState."""
    return Qt.Unchecked if not b else Qt.Checked


def checkStateToBool(state):
    """Translates Qt.CheckState to booleans."""
    return False if state == Qt.Unchecked else True


def closestGridPoint(p):
    """Return the closest point on the grid."""
    return QPointF(
        int(GRIDSIZE * round(p.x() / GRIDSIZE)),
        int(GRIDSIZE * round(p.y() / GRIDSIZE)))


def filePath(relPath):
    """Returns the absolute path of app data files."""
    return dirname(realpath(__file__)) + '/../../' + relPath
