from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QLabel,
    QPushButton,
    QCheckBox,
    QRadioButton,
    QComboBox
    )
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFont,
    QPalette,
    QPen
    )
from PyQt5.QtCore import Qt
from UI_flag import *

class StatusBox (QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize(40,18)

        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText,QColor(0,255,0))

        self.indicator = QLabel(self)
        self.indicator.resize(self.width(),self.height())
        self.indicator.move(0,0)
        self.indicator.setFont(QFont("Sans Serif", 9, QFont.Bold))
        self.indicator.setAlignment(Qt.AlignCenter)
        self.indicator.setPalette(self.palette)
        
        self.set(None)

    def set(self,value):
        if value:
            self.indicator.setText(str(value))
            self.color = QColor (0,0,0)
        elif value == 0:
            self.indicator.setText(str(value))
            self.color = QColor (0,0,0)
        elif value == None:
            self.indicator.setText("")
            self.color = QColor (192,192,192)
            
    def paintEvent (self,Event):
        p = QPainter(self)
        p.setBrush(self.color)
        p.setPen(QPen(self.color,1))
        p.drawRect(0,0,self.width(),self.height())

    def text(self):
        return self.indicator.text()

class LineEditPM (QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize (60,20)

        self.box=QLineEdit(self)
        self.box.move(0,0)
        self.box.resize(45,20)
        self.box.setText("0.000")

        b_plus=QPushButton('+',self)
        b_plus.setStyleSheet('font-size: 9px')
        b_plus.resize(12,12)
        b_plus.move(45,-1)
        b_plus.clicked.connect(self.add)

        b_minus=QPushButton('-',self)
        b_minus.setStyleSheet('font-size: 9px')
        b_minus.resize(12,12)
        b_minus.move(45,9)
        b_minus.clicked.connect(self.substract)

    def add(self):
        value = float(self.box.text())
        value += 0.5
        self.box.setText("{:.3f}".format(value))

    def substract(self):
        value = float(self.box.text())
        value -= 0.5
        self.box.setText("{:.3f}".format(value))

    def text(self):
        return self.box.text()

    def setText(self,value):
        return self.box.setText(value)

    def setValue(self,value):
        self.box.setText("{:.3f}".format(value))


class FlagEntry(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize (430,20)
        self.channel = None

        self.prefix = ""

        self.flag = Flag(self)
        self.flag.move(0,5)

        self.kz_label = QLabel (self)
        self.kz_label.move(self.flag.x() + 15,0)
        self.kz_label.resize(self.width()-self.flag.x()-self.flag.width(),20)
        
    def paintEvent(self,Event):
        if self.channel is not None:
            self.kz_label.setText(self.prefix + str(self.channel))
        else:
            self.kz_label.setText(self.prefix)

    def setText(self,text):
        self.prefix = text

    def set(self,value):
        if value:
            self.flag.setTrue()
        else:
            self.flag.setFalse()


class Address(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize(95,65)

        self.label = QLabel(self)
        self.label.setText("Адрес")
        self.label.move(0,0)
        self.label.resize(self.width(),15)
        self.label.setAlignment(Qt.AlignCenter)

        self.label1 = QLabel(self)
        self.label1.setText("ON")
        self.label1.move(0,17)
        self.label1.resize(20,15)
        self.label1.setAlignment(Qt.AlignCenter)
        
        self.flag = []
        self.flag_label = []
        for i in range(3):
            self.flag.append(DIPswitch(self))
            self.flag[i].move(20+25*i,20)
            self.flag_label.append(QLabel(self))
            self.flag_label[i].move(22+25*i,45)
            self.flag_label[i].setText(str(i+1))

    def set(self,value1,value2,value3):
            self.flag[0].set(value1)
            self.flag[1].set(value2)
            self.flag[2].set(value3)
            self.update()       


class TextEntry (QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)

        self.is_modified = False

        self.header = QLabel(self)
        self.header.move(25,5)
        self.header.resize(100,20)

        self.lineedit = QLineEdit(self)
        self.lineedit.move(self.header.x()+self.header.width()+5,5)
        self.lineedit.resize(50,20)

        self.resize(self.lineedit.x()+self.lineedit.width()+5,30)

    def setName(self,text):
        self.header.setText(text)

    def setText(self,text):
        self.lineedit.setText(text)

    def text(self):
        return self.lineedit.text()
        

class AbstractModule (QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize (430,200)

        self.header = QLabel(self)
        self.header.move(0,0)
        self.header.resize(330,20)
        self.header.setAlignment(Qt.AlignCenter)

        self.entry = []

        self.address = Address(self)
        self.address.move(330,60)
        
        self.connect_b = QPushButton(self)
        self.connect_b.setText("Опрос")
        self.connect_b.move(340,125)
        self.connect_b.resize(80,30)
        self.connect_b.clicked.connect(self.connect_b_clicked)

        self.reset_b = QPushButton(self)
        self.reset_b.setText("Сброс")
        self.reset_b.move(340,160)
        self.reset_b.resize(80,30)
        self.reset_b.clicked.connect(self.reset_b_clicked)

    def connect_b_clicked(self):
        pass

    def reset_b_clicked(self):
        pass        
    
class BTSAP_Entry (QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize (310,20)

        self.channel = QLabel(self)
        self.channel.move(0,0)
        self.channel.resize(10,20)

        self.input_box = LineEditPM(self)
        self.input_box.move(self.channel.x()+self.channel.width()+3,0)

        self.V_label = QLabel (self)
        self.V_label.setText("В")
        self.V_label.move(self.input_box.x()+self.input_box.width()+3,0)
        self.V_label.resize(10,20)
        self.V_label.setAlignment(Qt.AlignCenter)

        self.input2_box = QLineEdit(self)
        self.input2_box.move(self.V_label.x()+self.V_label.width()+3,0)
        self.input2_box.resize(self.input_box.width(),self.input_box.height())

        self.V2_label = QLabel (self)
        self.V2_label.setText("В")
        self.V2_label.move(self.input2_box.x()+self.input2_box.width()+3,0)
        self.V2_label.resize(10,20)

        self.deltaX = QLabel(self)
        self.deltaX.move(self.V2_label.x()+self.V2_label.width()+3,0)
        self.deltaX.resize(50,20)
        self.deltaX.setAlignment(Qt.AlignCenter)

        self.delta = QLabel (self)
        self.delta.move(self.deltaX.x()+self.deltaX.width()+3,0)
        self.delta.resize(50,20)
        self.delta.setAlignment(Qt.AlignCenter)

        self.KZ = FlagEntry(self)
        self.KZ.move(self.delta.x()+self.delta.width()+3,0)
        self.KZ.setText("КЗ")

    def setChannel(self,channel):
        self.channel.setText(str(channel))

    def value(self):
        return float(self.input_box.box.text())


    def paintEvent(self,Event):
        s = self.input_box.text()
        s = s.replace(",",".")
        self.input_box.setText(s)

        s = self.input2_box.text()
        s = s.replace(",",".")
        self.input2_box.setText(s)

        try:
            value = float(self.input_box.text())
        except Exception:
            self.input_box.setText("")

        try:
            base = float(self.input2_box.text())
        except Exception:
            self.input2_box.setText("")
           
        try:
            deltaX = value - base
            delta = (value - base) / base *100

            if (deltaX > 0):
                self.deltaX.setText("+"+"{:.2f}".format(deltaX)+" B")
                self.delta.setText("+"+"{:.2F}".format(delta)+"%")
            else:
                self.deltaX.setText("{:.2f}".format(deltaX)+" B")
                self.delta.setText("{:.2F}".format(delta)+"%")
        except Exception as e:         
            self.deltaX.setText("-")
            self.delta.setText("-")

class BPAS_Entry (QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize (340,20)

        self.channel = QLabel(self)
        self.channel.move(0,0)
        self.channel.resize(13,20)
        self.channel.setAlignment(Qt.AlignCenter)

        self.ADC_box = StatusBox(self)
        self.ADC_box.move(self.channel.x()+self.channel.width()+0,0)

        self.V_label = QLabel (self)
        self.V_label.setText("")
        self.V_label.move(self.ADC_box.x()+self.ADC_box.width()+0,0)
        self.V_label.resize(1,20)
        self.V_label.setAlignment(Qt.AlignCenter)

        self.ADC_ma_box = StatusBox(self)
        self.ADC_ma_box.move(self.V_label.x()+self.V_label.width()+3,0)

        self.ma_label = QLabel (self)
        self.ma_label.setText("мА")
        self.ma_label.move(self.ADC_ma_box.x()+self.ADC_ma_box.width()+3,0)
        self.ma_label.resize(15,20)
        self.ma_label.setAlignment(Qt.AlignCenter)

        self.input_box = QLineEdit(self)
        self.input_box.move(self.ma_label.x()+self.ma_label.width()+3,0)
        self.input_box.resize(40,20)

        self.ma2_label = QLabel (self)
        self.ma2_label.setText("мA")
        self.ma2_label.move(self.input_box.x()+self.input_box.width()+3,0)
        self.ma2_label.resize(15,20)

        self.deltaX = QLabel(self)
        self.deltaX.move(self.ma2_label.x()+self.ma2_label.width()+0,0)
        self.deltaX.resize(55,20)
        self.deltaX.setAlignment(Qt.AlignCenter)

        self.delta = QLabel (self)
        self.delta.move(self.deltaX.x()+self.deltaX.width()+0,0)
        self.delta.resize(55,20)
        self.delta.setAlignment(Qt.AlignCenter)

        self.KZ = FlagEntry(self)
        self.KZ.move(self.delta.x()+self.delta.width()+0,0)
        self.KZ.setText("КЗ")

        self.channel.setText("16")
        self.set(None)

    def set(self,value):
        if value is not None:
            self.ADC_box.set(value)
            #self.ADC_ma_box.set("{:.2f}".format(value/4096*3.3*6.666666666666))
            #self.ADC_ma_box.set("{:.2f}".format(5.722701*value/1000 - 0.496))
            self.ADC_ma_box.set("{:.2f}".format(5.369684*value/1000))

        else:
            self.ADC_box.set(None)
            self.ADC_ma_box.set(None)
            self.deltaX.setText("-")
            self.delta.setText("-")
            
    def setChannel(self,channel):
        self.channel.setText(str(channel))

    def paintEvent(self,Event):
        s = self.input_box.text()
        s = s.replace(",",".")
        self.input_box.setText(s)

        try:
            base = float(self.input_box.text())
        except Exception:
            self.input_box.setText("")
           
        try:
            value = float(self.ADC_ma_box.text())
            deltaX = value - base
            delta = (value - base) / base *100

            if (deltaX > 0):
                self.deltaX.setText("+"+"{:.2f}".format(deltaX)+" мА")
                self.delta.setText("+"+"{:.2F}".format(delta)+"%")
            else:
                self.deltaX.setText("{:.2f}".format(deltaX)+" мА")
                self.delta.setText("{:.2F}".format(delta)+"%")
        except Exception as e:         
            self.deltaX.setText("-")
            self.delta.setText("-")
        pass

class BPLS_Entry(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize(50,20)

        self.label= QLabel(self)
        self.indicator = QLabel(self)

        self.label.resize(15,18)
        self.label.move(0,0)
        self.label.setAlignment(Qt.AlignCenter)
        

        self.indicator.resize(35,18)
        self.indicator.move(15,0)
        self.indicator.setFont(QFont("Sans Serif", 9, QFont.Bold))
        self.indicator.setAlignment(Qt.AlignCenter)

        self.palette_L = QPalette()
        self.palette_L.setColor(QPalette.WindowText,QColor(0,255,0))

        self.palette_H = QPalette()
        self.palette_H.setColor(QPalette.WindowText,QColor(255,0,0))
        self.set(None)

    def setChannel(self,channel):
        self.label.setText(str(channel))

    def set(self,value):
        if value:
            self.indicator.setText("1 (L)")
            self.indicator.setPalette(self.palette_L)
            self.color = QColor (0,0,0)
        elif value == 0:
            self.indicator.setText("0 (H)")
            self.indicator.setPalette(self.palette_H)
            self.color = QColor (0,0,0)
        elif value == None:
            self.indicator.setText("")
            self.color = QColor (192,192,192)
            
    def paintEvent (self,Event):
        p = QPainter(self)
        p.setBrush(self.color)
        p.setPen(QPen(self.color,1))
        p.drawRect(self.indicator.x(),self.indicator.y(),self.indicator.width()-1,self.indicator.height()-1)
          
class BPSK_Entry(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent=parent)
        self.resize(55,20)

        self.label= QLabel(self)
        self.indicator = QLabel(self)

        self.label.resize(25,18)
        self.label.move(0,2)
        self.label.setAlignment(Qt.AlignCenter)
        

        self.indicator.resize(25,18)
        self.indicator.move(30,0)
        self.indicator.setFont(QFont("Sans Serif", 9, QFont.Bold))
        self.indicator.setAlignment(Qt.AlignCenter)

        self.palette_L = QPalette()
        self.palette_L.setColor(QPalette.WindowText,QColor(0,255,0))

        self.palette_H = QPalette()
        self.palette_H.setColor(QPalette.WindowText,QColor(255,0,0))
        self.set(None)

    def setChannel(self,channel):
        self.label.setText(str(channel))

    def set(self,value):
        if value:
            self.indicator.setText("1")
            self.indicator.setPalette(self.palette_L)
            self.color = QColor (0,0,0)
        elif value == 0:
            self.indicator.setText("0")
            self.indicator.setPalette(self.palette_H)
            self.color = QColor (0,0,0)
        elif value == None:
            self.indicator.setText("")
            self.color = QColor (192,192,192)
            

    def paintEvent (self,Event):
        p = QPainter(self)
        p.setBrush(self.color)
        p.setPen(QPen(self.color,1))
        p.drawRect(self.indicator.x(),self.indicator.y(),self.indicator.width()-1,self.indicator.height()-1)        
        
            
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = BPAS_Entry()
    w.show()
    w.set(445)
    cleanup = app.exec() 
    """Все строки кода между app.exec() и sys.exit выполняются при закрытии окна. Как это работает - хз, но это классно."""

    sys.exit(cleanup)
