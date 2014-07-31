#!/usr/bin/env python3
# coding=utf-8

from PySide import QtCore
from PySide.QtGui import (
    QApplication, QColor, QDialogButtonBox, QFileDialog, QFrame,
    QGridLayout, QHBoxLayout, QIcon, QImage, QMessageBox, QLayout,
    QPainter, QPalette, QPen, qRgb, QScrollArea, QTransform, QToolButton,
    QWidget)
from enum import Enum
from os import dirname, realpath


class PaintArea(QWidget):
    Tools = Enum('Tools', 'pen line rect roundRect circle eraser')
    tools = {
        'pen': True,
        'line': False,
        'rect': False,
        'roundRect': False,
        'circle': False,
        'eraser': False,
    }

    def __init__(self, parent=None):
        super(PaintArea, self).__init__(parent)
        self.autoFillBackground = True
        self.myPenWidth = 3
        self.myPenColor = QColor(100, 100, 100, 255)
        self.size_w = 500
        self.size_h = 500
        imageSize = QtCore.QSize(self.size_w, self.size_h)
        self.image = QImage(imageSize, QImage.Format_RGB32)
        self.imagePreview = QImage(imageSize, QImage.Format_ARGB32)
        self.lastPoint = QtCore.QPoint()
        self.setMinimumSize(imageSize)
        self.setMaximumSize(imageSize)

    def saveImage(self, fileName, fileFormat='png'):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())
        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def clearImagePreview(self):
        self.imagePreview.fill(QtCore.Qt.transparent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.firstPoint_x = event.x()
            self.firstPoint_y = event.y()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            if self.tools['pen'] or self.tools['eraser']:
                self.draw(event.x(), event.y())
            else:
                self.flag = False
                self.drawPreview(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            self.flag = True
            self.draw(event.x(), event.y())
            self.scribbling = False

    def setTool(self, st):
        for i in self.tools:
            self.tools[i] = False
        self.tools[st] = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image)
        painter.drawImage(event.rect(), self.imagePreview)
        self.clearImagePreview()

    def draw(self, endPoint_x, endPoint_y):
        painter = QPainter(self.image)

        painter.setPen(QPen(
            self.myPenColor, self.myPenWidth, QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setClipping(True)

        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setCompositionMode(QPainter.CompositionMode())

        if self.tools['circle']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            x2 = endPoint_x
            y2 = endPoint_y
            painter.drawEllipse(x1, y1, (x2 - x1), (y2 - y1))

        if self.tools['eraser']:
            painter.setPen(QPen(QtCore.Qt.white, 10, QtCore.Qt.SolidLine))
            painter.drawLine(
                self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)
            self.firstPoint_x = endPoint_x
            self.firstPoint_y = endPoint_y

        if self.tools['pen']:
            painter.drawLine(
                self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)
            self.firstPoint_x = endPoint_x
            self.firstPoint_y = endPoint_y

        if self.tools['line'] and self.flag:
            painter.drawLine(
                self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)

        if self.tools['rect']:
            dx = endPoint_x - self.firstPoint_x
            dy = endPoint_y - self.firstPoint_y
            painter.drawRect(self.firstPoint_x, self.firstPoint_y, dx, dy)

        if self.tools['roundRect']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            dx = endPoint_x - self.firstPoint_x
            dy = endPoint_y - self.firstPoint_y
            if x1 > endPoint_x and y1 > endPoint_y:
                painter.drawRoundedRect(
                    endPoint_x, endPoint_y, -dx, -dy, 20, 20, 0)
            else:
                painter.drawRoundedRect(x1, y1, dx, dy, 20., 20.)

        self.modified = True
        self.update()

    def drawPreview(self, endPoint_x, endPoint_y):
        painter = QPainter(self.imagePreview)
        painter.setPen(QPen(
            self.myPenColor,
            self.myPenWidth,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin))
        painter.setClipping(True)

        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.setOpacity(0.5)

        if self.tools['circle']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            x2 = endPoint_x
            y2 = endPoint_y
            painter.drawEllipse(x1, y1, (x2 - x1), (y2 - y1))

        if self.tools['line']:
            painter.drawLine(
                self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)

        if self.tools['rect']:
            painter.drawRect(
                self.firstPoint_x, self.firstPoint_y,
                endPoint_x - self.firstPoint_x,
                endPoint_y - self.firstPoint_y)

        if self.tools['roundRect']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            dx = endPoint_x - self.firstPoint_x
            dy = endPoint_y - self.firstPoint_y
            if x1 > endPoint_x and y1 > endPoint_y:
                painter.drawRoundedRect(
                    endPoint_x, endPoint_y, -dx, -dy, 20, 20, 0)
            else:
                painter.drawRoundedRect(x1, y1, dx, dy, 20., 20.)

        self.update()

    def rotate(self):
        myTransform = QTransform()
        myTransform.rotate(90)
        self.image = self.image.transformed(myTransform)
        self.update()

    def mirror_h(self):
        self.image = self.image.mirrored(False, True)
        self.update()

    def mirror_w(self):
        self.image = self.image.mirrored(True, False)
        self.update()

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return
        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)

        self.image = newImage

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class CustomCircuitCreator(QWidget):

    def __init__(self):
        super(CustomCircuitCreator, self).__init__()
        self.PaintArea = PaintArea(self)
        self.PaintArea.clearImage()
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.PaintArea, 1, 0, 1, 9)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.createToolsButtons()
        self.createButtons()
        self.setWindowTitle("Custom circuit creator")
        self.resize(self.PaintArea.size_w, self.PaintArea.size_h + 85)

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def createButtons(self):
        buttonsDialog = QDialogButtonBox(self)
        buttonsDialog.setStandardButtons(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Reset)
        self.grid.addWidget(buttonsDialog, 3, 0, 3, 9)
        buttonsDialog.button(QDialogButtonBox.Save).clicked.connect(
            self.saveFile)
        buttonsDialog.button(QDialogButtonBox.Reset).clicked.connect(
            self.PaintArea.clearImage)
        buttonsDialog.button(QDialogButtonBox.Cancel).clicked.connect(
            self.close)

    def createToolsButtons(self):
        buttonsFrame = QFrame()
        buttonsLayout = QHBoxLayout(buttonsFrame)
        buttonsLayout.setSizeConstraint(QLayout.SetDefaultConstraint)

        iconPath = (dirname(realpath(__file__)) + '/../../icons/')
        self.penButton = QToolButton(
            self,
            icon=QIcon(iconPath + 'pen_w.png'))
        self.penButton.setToolTip('freehand drawing')
        self.penButton.clicked.connect(lambda: self.PaintArea.setTool('pen'))
        buttonsLayout.addWidget(self.penButton)

        self.lineButton = QToolButton(
            self,
            icon=QIcon(iconPath + 'line_w.png'))
        self.lineButton.setToolTip('draw lines')
        self.lineButton.clicked.connect(lambda: self.PaintArea.setTool('line'))
        buttonsLayout.addWidget(self.lineButton)

        self.rect = QToolButton(
            self,
            icon=QIcon(iconPath + 'rect_w.png'))
        self.rect.setToolTip('create rectangle')
        self.rect.clicked.connect(lambda: self.PaintArea.setTool('rect'))
        buttonsLayout.addWidget(self.rect)

        self.roundRect = QToolButton(
            self,
            icon=QIcon(iconPath + 'roundrect_w.png'))
        self.roundRect.setToolTip('create a round-corner rectanlge')
        self.roundRect.clicked.connect(
            lambda: self.PaintArea.setTool('roundRect'))
        buttonsLayout.addWidget(self.roundRect)

        self.circle = QToolButton(
            self,
            icon=QIcon(iconPath + 'ellipse_w.png'))
        self.circle.setToolTip('create circle')
        self.circle.clicked.connect(lambda: self.PaintArea.setTool('circle'))
        buttonsLayout.addWidget(self.circle)

        self.eraser = QToolButton(
            self,
            icon=QIcon(iconPath + 'eraser_w.png'))
        self.eraser.setToolTip('erase parts of the drawing')
        self.eraser.clicked.connect(lambda: self.PaintArea.setTool('eraser'))
        buttonsLayout.addWidget(self.eraser)

        self.mirror_w = QToolButton(
            self,
            icon=QIcon(iconPath + 'mirror-w_w.png'))
        self.mirror_w.setToolTip('vertical symmetric inversion')
        self.mirror_w.clicked.connect(self.PaintArea.mirror_w)
        buttonsLayout.addWidget(self.mirror_w)

        self.mirror_h = QToolButton(
            self,
            icon=QIcon(iconPath + 'mirror-h_w.png'))
        self.mirror_h.setToolTip('horizontal symmetric inversion')
        self.mirror_h.clicked.connect(self.PaintArea.mirror_h)
        buttonsLayout.addWidget(self.mirror_h)

        self.rotate = QToolButton(
            self,
            icon=QIcon(iconPath + 'rotate_w.png'))
        self.rotate.setToolTip('rotate')
        self.rotate.clicked.connect(self.PaintArea.rotate)
        buttonsLayout.addWidget(self.rotate)

        self.grid.addWidget(buttonsFrame, 0, 0, QtCore.Qt.AlignLeft)

    def maybeSave(self):
        if self.PaintArea.isModified():
            ret = QMessageBox.warning(
                self, "Save your work",
                "The drawing has been modified.\n"
                "Do you want to save your changes ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat='png'):
        initialPath = QtCore.QDir.currentPath() + '/customCirc.' + fileFormat
        fileName = QFileDialog.getSaveFileName(
            self, "Save As", initialPath, "%s Files (*.%s);;All Files (*)"
            % (fileFormat.upper(), fileFormat))
        if fileName:
            if self.PaintArea.saveImage('customCirc.' + fileFormat):
                self.close()


def main():
    import sys

    app = QApplication(sys.argv)
    window = CustomCircuitCreator()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
