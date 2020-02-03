import sys
from PyQt5.QtCore import QCoreApplication, QPointF, QTimer, QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton
from PyQt5.QtGui import QPainterPath, QPainter, QVector2D, QColor
from pyaxidraw import axidraw
import math


class Canvas(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Axidraw by Hand")
        self.setMouseTracking(True)
        self.path = QPainterPath()
        self.paper = (50.0, 35.3) # paper size in cm
        self.ad = None
        self.isConnected = False
        self.currentPos = QPointF(1,1)
        self.mousePos = QPointF(1,1)
        self.isPenDown = False
        self.start()

    def follow_cursor(self):
        if self.isPenDown:
            delta = QVector2D(self.mousePos - self.currentPos).toPointF() * 0.1
            self.currentPos = self.currentPos+delta
        else:
            self.currentPos = self.mousePos

        self.goTo(self.currentPos.x(), self.currentPos.y())

    def start(self):
        if not self.isConnected:
            print("connect to axidraw...")
            # axidraw
            self.ad = axidraw.AxiDraw()
            self.ad.interactive()
            self.ad.options.model = 2 
            self.ad.options.units = 1            # set working units to cm.
            self.ad.options.accel = 75 
            self.ad.options.const_speed = True
            # self.ad.options.speed_penup = 200
            self.ad.options.speed_pendown = 75  
            self.ad.update()                     # Process changes to options
            if self.ad.connect():
                print("connect")
                self.isConnected = True
            self.timer = QTimer()
            self.timer.start(16) #ms
            self.timer.timeout.connect(self.follow_cursor)

    def stop(self):
        if self.isConnected:
            self.ad.moveto(0,0)
            self.ad.disconnect()
            self.isConnected = False
            self.timer.stop()

    def lineTo(self, x, y):
        px, py = x/self.size().width()*self.paper[0], y/self.size().height()*self.paper[1]
        self.path.lineTo(x, y)
        self.update()
        # print("line to", px, py)
        if self.isConnected:
            self.ad.lineto(px, py)

    def moveTo(self, x, y):
        px, py = x/self.size().width()*self.paper[0], y/self.size().height()*self.paper[1]
        # print("move to", px, py)
        self.path.moveTo(x, y)
        self.update()
        if self.isConnected:
            self.ad.moveto(px, py)

    def goTo(self, x, y):
        px, py = x/self.size().width()*self.paper[0], y/self.size().height()*self.paper[1]
        # print("move to", px, py)
        if self.isPenDown:
            self.path.lineTo(x, y)
        else:
            self.path.moveTo(x, y)
        self.update()
        if self.isConnected:
            self.ad.goto(px, py)

    def mousePressEvent(self, event):
        self.ad.pendown()
        self.isPenDown = True

    def mouseReleaseEvent(self, event):
        self.ad.penup()
        self.isPenDown = False

    def mouseMoveEvent(self, event):
        self.mousePos = QPointF(event.pos())
        # self.update()
        # if self.isMouseDown:
        #     self.lineTo(x, y)
        # else:
        #     self.moveTo(x, y)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPath(self.path)
        if self.path.elementCount()>1:
            lastPoint = QPointF(self.path.elementAt(self.path.elementCount()-1))
            painter.drawEllipse(lastPoint, 5, 5)

        painter.setPen(QColor(255,0,0, 50))
        painter.drawLine(self.mousePos.x(), 0, self.mousePos.x(), self.size().height())
        painter.drawLine(0, self.mousePos.y(), self.size().width(), self.mousePos.y())

        painter.end()

    def sizeHint(self):
        return QSize(720, 576)

    def closeEvent(self, event):
        self.stop()

if __name__ == "__main__":
    import sys, os
    app = QApplication([])
    window = Canvas()
    window.show()

    app.exec()
    os._exit(0) # issue with pyside and pyqt5 wont exit propery

