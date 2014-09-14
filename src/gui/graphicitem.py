#!/usr/bin/env python3
# coding=utf-8

from math import atan2, pi, pow, sqrt
from PySide.QtCore import QPointF, QRectF, Qt, QTimer
from PySide.QtGui import (
    QBrush, QColor, QCursor, QFont, QGraphicsItem, QGraphicsPathItem,
    QGraphicsSimpleTextItem, QImage, QPainterPath, QPen, QStyle)
from .util import closestGridPoint, filePath
from engine.simulator import Circuit, Plug


class WireItem(QGraphicsPathItem):
    """Represents an electrical wire connecting two items."""

    radius = 5
    """The radius of graphical handles."""

    def __init__(self, startIO, pts, endIO=None):
        super(WireItem, self).__init__()
        self.setFlags(
            QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        self.data = {
            'startIO': startIO,
            'points': pts,
            'endIO': endIO}
        """The real info. The class WireItem is just a graphical container
        around it. data is saved / loaded to / from file.
        """
        self.setZValue(-1)
        """Wire handle hovering over a Plug, MainView.mouseMove will detect
        correctly the Plug, not the wire handle.
        """
        self.complete = True if endIO else False
        """Can the wire be modified (not complete)?"""

    def addPoint(self):
        """Duplicates the end point, for use as a moving point during moves."""
        newPos = closestGridPoint(self.data['points'][-1])
        self.data['points'][-1] = newPos
        self.data['points'].append(self.data['points'][-1])
        self.setupPaint()

    def connect(self, endIO):
        """Try to connect the end points of the Wire."""
        if self.data['startIO'].connect(endIO):
            self.data['endIO'] = endIO
            self.complete = True    # Wire can't be modified anymore.
            self.setupPaint()
            return True
        return False

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?"""
        if not self.complete:
            path = QPainterPath()
            path.addEllipse(self.data['points'][-1], self.radius, self.radius)
            return path.contains(pos)

    def itemChange(self, change, value):
        """Warning view it will soon have to correct pos."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Restart till we stop moving.
            self.scene().views()[0].timer.start()
        return QGraphicsItem.itemChange(self, change, value)

    def moveLastPoint(self, endPoint):
        """Redraw the last, unfinished segment while the mouse moves."""
        sq2 = sqrt(2) / 2
        A = [[0, 1], [sq2, sq2], [1, 0], [sq2, -sq2],
            [0, -1], [-sq2, -sq2], [-1, 0], [-sq2, sq2]]
        x = self.data['points'][-2].x()
        y = self.data['points'][-2].y()
        L = sqrt(pow(endPoint.x() - x, 2) + pow(endPoint.y() - y, 2))
        angle = atan2(endPoint.x() - x, endPoint.y() - y)
        a = round(8 * angle / (2 * pi)) % 8
        self.data['points'][-1] = QPointF(x + A[a][0] * L, y + A[a][1] * L)
        self.setupPaint()

    def revert(self):
        """Undo the last segment."""
        self.data['points'][-2] = self.data['points'][-3]
        self.data['points'] = self.data['points'][:-2]
        self.setupPaint()

    def setupPaint(self):
        """Draw the wire segments and handle."""
        if not self.data['startIO'] or not self.data['endIO']:
            self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        elif self.data['startIO'].value:
            self.setPen(QPen(QBrush(QColor(QColor('green'))), 2))
        else:
            self.setPen(QPen(QBrush(QColor(QColor('red'))), 2))
        path = QPainterPath()
        path.moveTo(self.data['points'][0])
        for p in self.data['points'][1:]:
            path.lineTo(p)
        if not self.complete:   # An incomplete wire needs a handle
            path.addEllipse(self.data['points'][-1], self.radius, self.radius)
        self.setPath(path)
        self.update()

    def removeLast(self):
        """Remove the last segment (user corrects user errors)."""
        if not self.complete:
            self.data['points'] = self.data['points'][0:-2]
            if len(self.data['points']) > 1:
                self.addPoint()
                self.setupPaint()
            else:
                self.scene().removeItem(self)


class PlugItem(QGraphicsPathItem):
    """Graphical wrapper around the engine Plug class."""

    bodyW = 30
    """The width of the body of plugs."""
    pinW = 10
    """The width of the pin part of plugs."""

    def __init__(self, plug):
        super(PlugItem, self).__init__()
        self.data = plug
        """The real info. The class PlugItem is just a graphical container
        around it. data is saved / loaded to / from file.
        """
        self.showName = False
        """Is the name of the item shown on screen?"""
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptsHoverEvents(True)
        self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        # This path is needed at each mouse over event, to check if
        # the mouse is over a pin. We save it as an instance field,
        # rather than recreate it at each event.
        self.pinPath = QPainterPath()
        if self.data.isInput:
            self.pinPath.addEllipse(
                self.bodyW + self.pinW / 2, self.bodyW / 2,
                self.pinW, self.pinW)
        else:
            self.pinPath.addEllipse(
                self.pinW / 2, self.bodyW / 2, self.pinW, self.pinW)
        f = QFont('Times', 12, 75)
        # Name and value text labels.
        self.name = QGraphicsSimpleTextItem(self)
        # that won't rotate when the PlugItem is rotated by the user.
        self.name.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.name.setText(self.data.name)
        self.name.setFont(f)
        self.value = QGraphicsSimpleTextItem(self)
        self.value.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        # Or else value would get the clicks, instead of the PlugItem.
        self.value.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.value.setFont(f)
        self.setupPaint()

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?
        Also return the Plug under this handle.
        """
        return self.data if self.pinPath.contains(pos) else None

    def itemChange(self, change, value):
        """Warning view it will soon have to correct pos."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Restart till we stop moving.
            self.scene().views()[0].timer.start()
        return QGraphicsItem.itemChange(self, change, value)

    def setAndUpdate(self):
        """Change the undelying plug's value, and force updates items."""
        self.data.set(not self.data.value)
        for i in self.scene().items():
            if isinstance(i, PlugItem) or isinstance(i, WireItem):
                i.setupPaint()

    def setNameVisibility(self, isVisible):
        """Shows/Hide the item name in the graphical view."""
        self.showName = isVisible
        self.setupPaint()

    def setupPaint(self):
        """Offscreen rather than onscreen redraw (few changes)."""
        path = QPainterPath()
        if self.data.isInput:
            path.addEllipse(
                self.pinW / 2, self.pinW / 2, self.bodyW, self.bodyW)
        else:
            path.addRect(
                3 * self.pinW / 2 + 1, self.pinW / 2, self.bodyW, self.bodyW)
        path.addPath(self.pinPath)
        self.setPath(path)
        self.name.setVisible(self.showName)
        self.name.setText(self.data.name)
        br = self.mapToScene(self.boundingRect())
        w = self.boundingRect().width()
        h = self.boundingRect().height()
        realX = min([i.x() for i in br])
        realY = min([i.y() for i in br])
        self.name.setPos(self.mapFromScene(
            realX, realY + (w if self.rotation() % 180 else h) + 1))
        self.value.setText(
            str(int(self.data.value)) if self.data.value is not None else 'E')
        self.value.setPos(self.mapFromScene(realX + w / 3, realY + h / 3))
        self.value.setBrush(QColor('green' if self.data.value else 'red'))
        self.update()       # Force onscreen redraw after changes.


class CircuitItem(QGraphicsItem):
    """Graphical wrapper around the engine Circuit class."""

    textH = 12
    """Height of text."""
    ioH = 20
    """Height between to I/O pins."""
    ioW = 15
    """Length of I/O pins."""
    radius = 10
    """Radius of I/O pin heads."""

    def __init__(self, circuit):
        super(CircuitItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        imgDir = filePath('icons/')
        self.data = circuit
        """The real info. The class CircuitItem is just a graphical container
        around it. data is saved / loaded to / from file.
        """
        self.image = QImage(imgDir + circuit.__class__.__name__ + '.png')
        """The graphical representation of our item on screen."""
        if not self.image:
            self.image = QImage(imgDir + 'Default.png')
            self.showCategory = True
        self.showName = True
        """Is the item's name shown on screen?"""
        self.showCategory = False
        """Is the item's category (circuit class) shown on screen?"""
        self.name = QGraphicsSimpleTextItem(self)
        # that won't rotate when the PlugItem is rotated by the user.
        self.name.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.name.setText(self.data.name)
        self.category = QGraphicsSimpleTextItem(self)
        self.category.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.category.setText(self.data.category)
        self.setupPaint()

    def boundingRect(self):
        """Qt requires overloading this when overloading QGraphicsItem."""
        W = 2 * self.radius + 2 * self.ioW + self.imgW
        ni = self.data.nb_inputs()
        no = self.data.nb_outputs()
        t = (1 - int(max(ni, no) / 2)) * self.ioH - self.radius / 2
        b = (1 + int(max(ni, no) / 2)) * self.ioH + self.radius / 2
        return (
            QRectF(-self.ioW - self.radius, t, W, b - t) if max(ni, no) > 1
            else QRectF(-self.ioW - self.radius, 0, W, self.image.height()))

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is? Return it."""
        for i in range(self.nIn):
            if self.inputPaths[i].contains(pos):
                return self.data.inputList[i]
        for i in range(self.nOut):
            if self.outputPaths[i].contains(pos):
                return self.data.outputList[i]

    def itemChange(self, change, value):
        """Warning view it will soon have to correct pos."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Restart till we stop moving.
            self.scene().views()[0].timer.start()
        return QGraphicsItem.itemChange(self, change, value)

    def paint(self, painter, option, widget):
        """Draws the item."""
        painter.setPen(QPen(QColor('black'), 2))
        ni = self.data.nb_inputs()
        no = self.data.nb_outputs()
        for i in range(1 - int(ni / 2), 2 + int(ni / 2)):
            if i != 1 or ni % 2:
                painter.drawLine(-self.ioW, i * self.ioH, 0, i * self.ioH)
        for i in range(1 - int(no / 2), 2 + int(no / 2)):
            if i != 1 or no % 2:
                painter.drawLine(
                    self.imgW, i * self.ioH, self.imgW + self.ioW,
                    i * self.ioH)
        painter.drawImage(QRectF(0, 0, self.imgW, self.imgH), self.image)
        for i in range(ni):
            painter.drawPath(self.inputPaths[i])
        painter.drawLine(
            0, (1 - int(ni / 2)) * self.ioH, 0, (1 + int(ni / 2)) * self.ioH)
        for i in range(no):
            painter.drawPath(self.outputPaths[i])
        painter.drawLine(
            self.imgW,
            (1 - int(no / 2)) * self.ioH,
            self.imgW,
            (1 + int(no / 2)) * self.ioH)
        # Default selection box doesn't work; simple reimplementation.
        if option.state & QStyle.State_Selected:
            pen = QPen(Qt.black, 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def setCategoryVisibility(self, isVisible):
        """Show/Hide circuit category (mostly useful for user circuits)."""
        self.showCategory = isVisible
        self.setupPaint()

    def setNameVisibility(self, isVisible):
        """Shows/Hide the item name in the graphical view."""
        self.showName = isVisible
        self.setupPaint()

    def setNbInputs(self, nb):
        """Add/Remove inputs (for logical gates)."""
        if nb > self.data.nb_inputs():
            for x in range(nb - self.data.nb_inputs()):
                Plug(True, None, self.data)
        elif nb < self.data.nb_inputs():
            for x in range(self.data.nb_inputs() - nb):
                self.data.remove_input(self.data.inputList[0])
        self.setupPaint()

    def setupPaint(self):
        """Offscreen rather than onscreen redraw (few changes)."""
        self.nIn = self.data.nb_inputs()
        self.nOut = self.data.nb_outputs()
        # 3 sections with different heights must be aligned :
        self.imgH = self.image.size().height()   # central (png image)
        self.imgW = self.image.size().width()
        self.inH = (self.nIn - 1) * self.ioH + 2 * self.radius  # inputs
        self.outH = (self.nOut - 1) * self.ioH + 2 * self.radius    # outputs
        # therefore we calculate a vertical offset for each section :
        self.maxH = max(self.imgH, self.inH, self.outH)
        self.imgOff = (
            0 if self.maxH == self.imgH else (self.maxH - self.imgH) / 2.)
        self.inOff = (
            0 if self.maxH == self.inH else (self.maxH - self.inH) / 2.)
        self.outOff = (
            0 if self.maxH == self.outH else (self.maxH - self.outH) / 2.)
        # i/o mouseover detection. Create once, use on each mouseMoveEvent.
        self.inputPaths = []
        self.outputPaths = []
        ni = self.data.nb_inputs()
        no = self.data.nb_outputs()
        for i in range(1 - int(ni / 2), 2 + int(ni / 2)):
            if i != 1 or ni % 2:
                path = QPainterPath()
                path.addEllipse(
                    -self.ioW - self.radius, i * self.ioH - self.radius / 2,
                    self.radius, self.radius)
                self.inputPaths.append(path)
        for i in range(1 - int(no / 2), 2 + int(no / 2)):
            if i != 1 or no % 2:
                path = QPainterPath()
                path.addEllipse(
                    self.imgW + self.ioW, i * self.ioH - self.radius / 2,
                    self.radius, self.radius)
                self.outputPaths.append(path)
        self.name.setVisible(self.showName)
        self.category.setVisible(self.showCategory)
        if self.showName or self.showCategory:
            br = self.mapToScene(self.boundingRect())
            w = self.boundingRect().width()
            h = self.boundingRect().height()
            realX = min([i.x() for i in br])
            realY = min([i.y() for i in br])
            firstY = realY + (w if self.rotation() % 180 else h) + 1
            secondY = firstY + self.textH
            if self.showName:
                self.name.setBrush(QColor('red'))
                self.name.setText(self.data.name)
                self.name.setPos(self.mapFromScene(realX, firstY))
            if self.showCategory:
                self.category.setBrush(QColor('green'))
                self.category.setText(
                    self.data.category if self.data.category
                    else self.data.__class__.__name__)
                self.category.setPos(self.mapFromScene(
                    realX, secondY if self.showName else firstY))
        self.prepareGeometryChange()    # Must be called (cf Qt doc)
        self.update()       # Force onscreen redraw after changes.
