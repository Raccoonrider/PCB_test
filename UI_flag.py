from PyQt5.QtWidgets import QWidget, QLabel

from PyQt5.QtGui import QPainter, QColor, QPen

class Flag (QWidget):
    def __init__(self, parent=None):
        self.is_set = False
        
        QWidget.__init__(self,parent=parent)
        self.col1 = QColor(255,0,0)
        self.col2 = QColor(255,255,255)
        self.resize(11,11)
         
    def paintEvent(self, event):
        f=QPainter(self)
        if self.is_set:
            f.setBrush(self.col1)
        else:
            f.setBrush(self.col2)
        f.drawRect(0,0,self.width()-1,self.height()-1)
        
    def set(self,value):
        self.is_set = value

    def setFalse(self):
        self.is_set = False

    def setTrue(self):
        self.is_set = True

    def setColors(self,col1,col2):
        self.col1 = col1
        self.col2 = col2

class Flag_check (QWidget):
    def __init__(self, parent=None):
        self.is_set = False
        
        QWidget.__init__(self,parent=parent)
        self.col1 = QColor(255,255,255)
        self.col2 = QColor(0,0,0)
        self.resize(11,11)
         
    def paintEvent(self, event):
        f=QPainter(self)
        f.setBrush(self.col1)
        f.drawRect(0,0,self.width()-1,self.height()-1)
        f.setPen(QPen(self.col2,2))
        if self.is_set:
            f.setPen(QPen(self.col2,2))
            f.drawLine(0,(self.height()-1)/2,(self.width()-1)/2,(self.height()-1))
            f.drawLine((self.width()-1)/2,(self.height()-1),(self.width()-1),0)
        else:
            f.drawLine(3,(self.height()-1)/2,(self.width()-3),(self.height()-1)/2)

        
    def set(self,value):
        self.is_set = value

    def setFalse(self):
        self.is_set = False

    def setTrue(self):
        self.is_set = True

    def setColors(self,col1,col2):
        self.col1 = col1
        self.col2 = col2

        
class DIPswitch (QWidget):
    def __init__(self, parent=None):
        self.is_set = False
        
        QWidget.__init__(self,parent=parent)
        self.color_main = QColor(255,255,255)
        self.color_bgr = QColor(0,0,0)
        self.resize(11,22)

    def paintEvent(self, event):
        f=QPainter(self)
        f.setBrush(self.color_bgr)
        f.drawRect(0,0,self.width()-1,self.height()-1)
        f.setBrush(self.color_main)
        f.drawEllipse(0,(not self.is_set)*(self.height()-1)/2,self.width()-1,(self.height()-1)/2)

        
    def set(self,value):
        self.is_set = value

    def setColors(self,color,background):
        self.color_main = color
        self.color_bgr = background  


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = Flag()
    w.set(1)
    w.show()
    cleanup = app.exec() 
    """Все строки кода между app.exec() и sys.exit выполняются при закрытии окна. Как это работает - хз, но это классно."""

    sys.exit(cleanup)
