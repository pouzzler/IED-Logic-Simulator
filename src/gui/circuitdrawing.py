#!/usr/bin/env python3
# coding=utf-8

from PySide import QtCore, QtGui
import os


class paintArea(QtGui.QWidget):
    tools = {
        'pen': True,
        'line': False,
        'rect': False,
        'roundRect': False,
        'circle': False,
        'eraser': False,
        }

    def __init__(self, parent=None):
        super(paintArea, self).__init__(parent)
        self.autoFillBackground = True
        self.myPenWidth = 3
        self.myPenColor = QtGui.QColor(100, 100, 100, 255)
        self.size_w = 500
        self.size_h = 500
        imageSize = QtCore.QSize(self.size_w, self.size_h)
        self.image = QtGui.QImage(imageSize, QtGui.QImage.Format_RGB32)
        self.imagePreview = QtGui.QImage(imageSize, QtGui.QImage.Format_ARGB32)
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
        self.image.fill(QtGui.qRgb(255, 255, 255))
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
                self.draw(event.x(),event.y())
            else:
                self.flag = False                
                self.drawPreview(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            self.flag = True
            self.draw(event.x(),event.y())
            self.scribbling = False        
        
    def setTool(self, st):
        for i in self.tools:
            self.tools[i] = False            
        self.tools[st] = True                

    def paintEvent(self, event):        
        painter = QtGui.QPainter(self)        
        painter.drawImage(event.rect(), self.image)
        painter.drawImage(event.rect(), self.imagePreview)
        self.clearImagePreview()
                                    
    def draw(self, endPoint_x, endPoint_y):            
        painter = QtGui.QPainter(self.image)
        
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setClipping(True)
                    
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode())

        if self.tools['circle']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            x2 = endPoint_x
            y2 = endPoint_y
            painter.drawEllipse(x1, y1, (x2-x1), (y2-y1))            
        
        if self.tools['eraser']:
            painter.setPen(QtGui.QPen(QtCore.Qt.white, 10, QtCore.Qt.SolidLine))
            painter.drawLine(self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)
            self.firstPoint_x = endPoint_x
            self.firstPoint_y = endPoint_y
                
        if self.tools['pen']:
            painter.drawLine(self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)
            self.firstPoint_x = endPoint_x
            self.firstPoint_y = endPoint_y
                        
        if self.tools['line'] and self.flag:
            painter.drawLine(self.firstPoint_x,self.firstPoint_y, endPoint_x, endPoint_y)            
            
        if self.tools['rect']:
            dx = endPoint_x-self.firstPoint_x
            dy = endPoint_y-self.firstPoint_y
            painter.drawRect(self.firstPoint_x, self.firstPoint_y, dx, dy)
        
        if self.tools['roundRect']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            dx = endPoint_x-self.firstPoint_x
            dy = endPoint_y-self.firstPoint_y
            if x1 > endPoint_x and y1 > endPoint_y:
                painter.drawRoundedRect(endPoint_x, endPoint_y, -dx, -dy, 20, 20, 0 )
            else:
                painter.drawRoundedRect(x1, y1, dx, dy, 20., 20.)
                         
        self.modified = True
        self.update()

    def drawPreview(self, endPoint_x, endPoint_y):
        painter = QtGui.QPainter(self.imagePreview)
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setClipping(True)
                    
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)        
        
        painter.setOpacity(0.4)

        if self.tools['circle']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            x2 = endPoint_x
            y2 = endPoint_y
            painter.drawEllipse(x1, y1, (x2-x1), (y2-y1))
        
        if self.tools['line']:
            painter.drawLine(self.firstPoint_x, self.firstPoint_y, endPoint_x, endPoint_y)

        if self.tools['rect']:
            painter.drawRect(self.firstPoint_x, self.firstPoint_y, endPoint_x-self.firstPoint_x, endPoint_y-self.firstPoint_y )
        
        if self.tools['roundRect']:
            x1 = self.firstPoint_x
            y1 = self.firstPoint_y
            dx = endPoint_x-self.firstPoint_x
            dy = endPoint_y-self.firstPoint_y
            if x1 > endPoint_x and y1 > endPoint_y:
                painter.drawRoundedRect(endPoint_x, endPoint_y, -dx, -dy, 20, 20, 0 )
            else:
                painter.drawRoundedRect(x1, y1, dx, dy, 20., 20.)
                 
        self.update()
    
    def rotate(self):
        myTransform = QtGui.QTransform()
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

        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(QtGui.qRgb(255, 255, 255))
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
    
        self.image = newImage

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class CustomCircuitCreator(QtGui.QWidget):

    def __init__(self):
        super(CustomCircuitCreator, self).__init__()

        self.paintArea = paintArea(self)
        
        self.paintArea.clearImage()

        self.grid = QtGui.QGridLayout(self)
        self.grid.addWidget(self.paintArea, 1, 0, 1, 9)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)        
        
        self.createActions()
        self.createButtons()

        self.setWindowTitle("Custom circuit creator")
        self.resize(self.paintArea.size_w, self.paintArea.size_h + 85)

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()


    def createButtons(self):
        buttonsDialog = QtGui.QDialogButtonBox(self)
        buttonsDialog.setStandardButtons(
            QtGui.QDialogButtonBox.Save |
            QtGui.QDialogButtonBox.Cancel |
            QtGui.QDialogButtonBox.Reset)
        self.grid.addWidget(buttonsDialog, 3, 0, 3, 9)
        buttonsDialog.button(QtGui.QDialogButtonBox.Save).clicked.connect(
            self.saveFile)
        buttonsDialog.button(QtGui.QDialogButtonBox.Reset).clicked.connect(
            self.paintArea.clearImage)
        buttonsDialog.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(
            self.close)

    def createActions(self):
        buttonsFrame = QtGui.QFrame()
        buttonsLayout = QtGui.QHBoxLayout(buttonsFrame)
        buttonsLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)

        iconPath = os.path.dirname(os.path.realpath(__file__)) + '/icons/'
        self.penButton = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'pen_w.png'))
        self.penButton.setToolTip('freehand drawing')
        self.penButton.clicked.connect(self.setPen)
        buttonsLayout.addWidget(self.penButton)

        self.lineButton = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'line_w.png'))
        self.lineButton.setToolTip('draw lines')
        self.lineButton.clicked.connect(self.setLine)
        buttonsLayout.addWidget(self.lineButton)

        self.rect = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'rect_w.png'))
        self.rect.setToolTip('create rectangle')
        self.rect.clicked.connect(self.setRect)
        buttonsLayout.addWidget(self.rect)

        self.roundRect = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'roundrect_w.png'))
        self.roundRect.setToolTip('create a round-corner rectanlge')
        self.roundRect.clicked.connect(self.setRoundRect)
        buttonsLayout.addWidget(self.roundRect)

        self.circle = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'ellipse_w.png'))
        self.circle.setToolTip('create circle')
        self.circle.clicked.connect(self.setCircle)
        buttonsLayout.addWidget(self.circle)

        self.eraser = QtGui.QToolButton(
            self, 
            icon = QtGui.QIcon(iconPath + 'eraser_w.png'))
        self.eraser.setToolTip('erase parts of the drawing')
        self.eraser.clicked.connect(self.setEraser)
        buttonsLayout.addWidget(self.eraser)
        
        self.mirror_w = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'mirror-w_w.png'))
        self.mirror_w.setToolTip('vertical symmetric inversion')
        self.mirror_w.clicked.connect(self.setMirror_w)
        buttonsLayout.addWidget(self.mirror_w)

        self.mirror_h = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'mirror-h_w.png'))
        self.mirror_h.setToolTip('horizontal symmetric inversion')
        self.mirror_h.clicked.connect(self.setMirror_h)
        buttonsLayout.addWidget(self.mirror_h)

        self.rotate = QtGui.QToolButton(
            self,
            icon = QtGui.QIcon(iconPath + 'rotate_w.png'))
        self.rotate.setToolTip('rotate')
        self.rotate.clicked.connect(self.paintArea.rotate)
        buttonsLayout.addWidget(self.rotate)

        self.grid.addWidget(buttonsFrame, 0, 0, QtCore.Qt.AlignLeft)

    def maybeSave(self):
        if self.paintArea.isModified():
            ret = QtGui.QMessageBox.warning(self, "Save your work",
                "The drawing has been modified.\n"
                "Do you want to save your changes ?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat='png'):
        initialPath = QtCore.QDir.currentPath() + '/customCirc.' + fileFormat
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As",
            initialPath,
            "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            if self.paintArea.saveImage('customCirc.' + fileFormat):
                self.close()

    def setPen(self):
        self.paintArea.setTool('pen')
        
    def setLine(self):
        self.paintArea.setTool('line')
    
    def setRect(self):
        self.paintArea.setTool('rect')

    def setCircle(self):
        self.paintArea.setTool('circle')

    def setEraser(self):
        self.paintArea.setTool('eraser')

    def setRoundRect(self):
        self.paintArea.setTool('roundRect')
        
    def setMirror_w(self):
        self.paintArea.mirror_w()
        
    def setMirror_h(self):
        self.paintArea.mirror_h()


def main():
    import sys

    app = QtGui.QApplication(sys.argv)
    window = CustomCircuitCreator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
