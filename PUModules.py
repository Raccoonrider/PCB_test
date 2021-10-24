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
    QFont
    )
from UI_flag import Flag
from Subclasses import *

        
class Settings(AbstractModule):
    def __init__(self, parent=None):
        AbstractModule.__init__(self,parent=parent)
###########
        self.default_channel = "COM10"
        self.default_bitrate = 500000
        self.default_bustype = "slcan"

        self.channel = self.default_channel
        self.bitrate = self.default_bitrate
        self.bustype = self.default_bustype

        self.is_modified = False
###########
        
        self.connect_b.setText("Соединение")
        self.address.hide()
        
        self.entry = []
        for i in range(3):
            self.entry.append(TextEntry(self))
            self.entry[i].move(0,15+i*35)

        self.entry[0].setName("Интерфейс")
        self.entry[1].setName("Битрейт, б/с")       
        self.entry[2].setName("Тип адаптера")

        self.entry[0].setText(self.channel)
        self.entry[1].setText(str(self.bitrate))       
        self.entry[2].setText(self.bustype)
        

    def connect_b_clicked(self):
        self.channel = self.entry[0].text()
        self.bustype = self.entry[2].text()
        try:
            self.bitrate = int(self.entry[1].text())
        except ValueError:
            self.entry[1].setText(str(self.bitrate))
        self.is_modified = True

    def reset_b_clicked(self):
        self.channel = self.default_channel
        self.bitrate = self.default_bitrate
        self.bustype = self.default_bustype      


class BTSAP (AbstractModule):
    def __init__(self, parent=None):
        AbstractModule.__init__(self,parent=parent)
        
        self.address.set(0,1,1)
        self.header.setText("Управление аналоговыми выходами")

        for i in range(4):
            self.entry.append(BTSAP_Entry(self))
            self.entry[i].move(20,60+i*30)
            self.entry[i].setChannel(i+1)
            self.entry[i].input_box.setText("10.000")


        self.values_label = QLabel(self)
        self.values_label.setText("Значения:")
        self.values_label.move(70,30)

        self.label = []
        for i in range(5):
            self.label.append(QLabel(self))
            self.label[i].setAlignment(Qt.AlignCenter)

        self.label[0].move(self.entry[0].input_box.x()+20,40)
        self.label[0].setText("заданное")
        self.label[0].resize(self.entry[0].input_box.size())

        self.label[1].move(self.entry[0].input2_box.x()+20,40)
        self.label[1].setText("измеренное")
        self.label[1].resize(self.entry[0].input2_box.size())

        self.label[2].move(self.entry[0].deltaX.x()+20,40)
        self.label[2].setText("Отклонение")
        self.label[2].resize(100,20)
        


class BPLS (AbstractModule):
    def __init__(self, parent=None):
        AbstractModule.__init__(self,parent=parent)

        self.header.setText("Состояние логических входов")
       
        self.channel_box = QComboBox(self)
        self.channel_box.addItems(["БПЛС-48/1", "БПЛС-48/2"])
        self.channel_box.move (340,20)
        self.channel_box.resize (80,20)

        self.reset_b.clicked.connect(self.setNone)

        self.entry = []
        for i in range(48):
            self.entry.append(BPLS_Entry(self))
            self.entry[i].label.setText(str(i+1))
            self.entry[i].move(10+50*(i//8),25+i%8*20)
            
    def setNone(self):
        for i in range(48):
            self.entry[i].set(None)

    def set(self,value,offset):
        if offset == 0:
            for i in range(32):
                self.entry[i].set((value>>i)&1)
        if offset == 1:
            for i in range(16):
                self.entry[i+32].set((value>>i)&1)

    def getChannel(self):
        return self.channel_box.currentIndex() + 1

    def paintEvent(self,Event):
        if self.getChannel() == 1:
            self.address.set(1,1,1)
        if self.getChannel() == 2:
            self.address.set(1,0,1)         

class BPSK (AbstractModule):
    def __init__(self, parent=None):
        AbstractModule.__init__(self,parent=parent)

        self.address.set(0,1,1)
        self.header.setText('Состояние входов типа "сухой контакт"')


        self.entry = []
        for i in range(20):
            self.entry.append(BPSK_Entry(self))
            self.entry[i].setChannel("CK"+str(i+1).zfill(2))
            self.entry[i].move(20+60*(i%4),35+20*(i//4))

    def reset_b_clicked(self):
        for i in range(20):
            self.entry[i].set(None)

    def setNone(self):
        for i in range(20):
            self.entry[i].set(None)        

class BPAS (AbstractModule):
    def __init__(self, parent=None):
        AbstractModule.__init__(self,parent=parent)
        self.resize (430,400)
        
        self.channel_box = QComboBox(self)
        self.channel_box.addItems(["БПАС-16/1", "БПАС-16/2"])
        self.channel_box.move (340,20)
        self.channel_box.resize (80,20)

        self.reset_b.clicked.connect(self.setNone)

        self.entry = []
        for i in range(16):
            self.entry.append(BPAS_Entry(self))
            self.entry[i].setChannel(i+1)
            self.entry[i].move(10,60+i*20)
        
        self.header.setText('Состояние аналоговых входов')

        self.values_label = QLabel(self)
        self.values_label.setText("Значения:")
        self.values_label.move(100,30)

        self.label = []
        for i in range(3):
            self.label.append(QLabel(self))
            self.label[i].setAlignment(Qt.AlignCenter)

        self.label[0].move(self.entry[0].ADC_box.x(),40)
        self.label[0].setText("Код АЦП")
        self.label[0].resize(50,20)

        self.label[1].move(self.entry[0].ADC_ma_box.x()+10,40)
        self.label[1].setText("полученное/измеренное")
        self.label[1].resize(125,20)

        self.label[2].move(self.entry[0].deltaX.x()+10,40)
        self.label[2].setText("Отклонение")
        self.label[2].resize(100,20)

    def setNone(self):
        for i in range(16):
            self.entry[i].set(None)
            self.entry[i].KZ.set(None)

    def getChannel(self):
        return self.channel_box.currentIndex() + 1       

    def paintEvent(self,Event):
        if self.getChannel() == 1:
            self.address.set(1,1,0)
        if self.getChannel() == 2:
            self.address.set(1,0,0)
        
class BVSK (AbstractModule):
    def __init__(self, parent=None):
        AbstractModule.__init__(self,parent=parent)

        self.address.set(0,1,0)
        self.header.setText('Управление выходами типа "сухой контакт"')

        self.entry = []
        for i in range(16):
            self.entry.append(QCheckBox(self))
            self.entry[i].setText("H"+str(i+1))
            self.entry[i].move(20+100*(i//8),25+i%8*20)

        self.entry_all = QCheckBox(self)
        self.entry_all.setText("Все")
        self.entry_all.move(220,25)
        self.entry_all.clicked.connect(self.config_all)

    def reset_b_clicked(self):
        for i in range(16):
            self.entry[i].setChecked(False)
            self.entry_all.setChecked(False)

    def config_all(self):
        if self.entry_all.isChecked():
            for i in range(16):
                self.entry[i].setChecked(1)
        else:
            for i in range(16):
                self.entry[i].setChecked(0)           

    def config_byte(self):
        value = 0
        for i in range(16):
            value |= self.entry[i].isChecked() << i
        return value.to_bytes(2, byteorder = "little", signed = False)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = BTSAP()
    w.show()
    cleanup = app.exec() 
    """Все строки кода между app.exec() и sys.exit выполняются при закрытии окна. Как это работает - хз, но это классно."""

    sys.exit(cleanup)
    
