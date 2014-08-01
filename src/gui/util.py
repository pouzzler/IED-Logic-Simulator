from os.path import dirname, realpath


def filePath(relPath):
    """Returns the absolute path of a path relative to the app's
    installation folder.
    """
    return dirname(realpath(__file__)) + '/../../' + relPath
