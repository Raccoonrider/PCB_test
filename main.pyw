#Global import
import time
import sys
import can
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QTabWidget,
    QPlainTextEdit
    )
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFont
    )
from PyQt5.QtCore import QTimer
from threading import Thread, Lock, Event


#Local import
from UI_flag import *
from PUModules import *
from Subclasses import *

class Main():
    def __init__(self):

        #Time intervals in seconds
        self.exchange_timeout = 0.5
        self.exchange_rate_limiter = 0.05
        self.update_timeout = 0.01

        #Errors
        self.invalid_request = False
        self.invalid_address = False
        self.error = False
        self.no_connection = False

        #GUI init
        self.app = QApplication(sys.argv)
        self.gui = Window()
        self.gui.show()

        #GUI function binding
        self.gui.BTSAP.connect_b.clicked.connect(self.test_BTSAP)
        self.gui.BPLS.connect_b.clicked.connect(self.test_BPLS)
        self.gui.BPSK.connect_b.clicked.connect(self.test_BPSK)
        self.gui.BPAS.connect_b.clicked.connect(self.test_BPAS)
        self.gui.BVSK.connect_b.clicked.connect(self.test_BVSK)

        self.gui.BTSAP.reset_b.clicked.connect(self.drop_test_flags)
        self.gui.BPLS.reset_b.clicked.connect(self.drop_test_flags)
        self.gui.BPSK.reset_b.clicked.connect(self.drop_test_flags)        
        self.gui.BPAS.reset_b.clicked.connect(self.drop_test_flags)
        self.gui.BVSK.reset_b.clicked.connect(self.drop_test_flags)
        self.gui.settings.reset_b.clicked.connect(self.disconnect)

        #Request queue init
        self.queue = RequestQueue()

        self.message_recv = None
        self.message_sent = None
        self.last_exception = None
        
        self.connected_flag = False
        self.connected_print_flag = False
        self.gui.settings.is_modified = False
        self.drop_test_flags()



        #Exchange thread init
        self.exchange_lock = Lock()
        self.exchange_allow = Event()
        self.exchange_thread = Thread(target = self.exchange)
        self.exchange_thread.start()

        #Exchange limiter
        self.exchange_timer = QTimer()
        self.exchange_timer.setSingleShot(False)
        self.exchange_timer.timeout.connect(self.exchange_allow.set)
        self.exchange_timer.setInterval(self.exchange_rate_limiter*1000) 
        self.exchange_timer.start()        

        #GUI update
        self.gui_update_timer = QTimer()
        self.gui_update_timer.setSingleShot(False)
        self.gui_update_timer.timeout.connect(self.update)
        self.gui_update_timer.setInterval(self.update_timeout*1000) 
        self.gui_update_timer.start()
        self.gui_update_index = 0

        cleanup = self.app.exec()
        self.disconnect()
        sys.exit(cleanup)

    def update(self):        
        """Exception handling"""
        if self.last_exception != None:
            self.gui.print_exception(self.last_exception)
            self.last_exception = None
            
        self.gui.invalid_request_entry.set(self.invalid_request)
        self.gui.invalid_address_entry.set(self.invalid_address)
        self.gui.error_entry.set(self.error)
        self.gui.no_connection_entry.set(self.no_connection)
            
        """Connection indication"""
        if self.connected_print_flag:
            self.gui.print_connected()
            self.connected_print_flag = False

        """INPUT handling"""
        try:
            if self.message_recv != None:
                #General handling
                self.gui.print_package(self.message_recv,False)
                #Error handling
                if self.message_recv.data[2:3] == Command.invalid_request:
                    self.invalid_request = 1
                else:
                    self.invalid_request = 0
                if self.message_recv.data[2:3] == Command.invalid_address:
                    self.invalid_address = 1
                else:
                    self.invalid_address = 0
                if self.message_recv.data[2:3] == Command.error:
                    self.error = 1
                else:
                    self.error = 0
                #Block-specific handling
                if self.BPLS_is_tested:
                    data = int.from_bytes(self.message_recv.data[4:8],byteorder = "little", signed = True)
                    channel = self.message_recv.data[2:4]
                    if channel == b"\xf1\x02":
                        self.gui.BPLS.set(data,1)
                        self.queue.enqueue(self.BPLS_message1)
                    if channel == b"\xf1\x01":
                        self.gui.BPLS.set(data,0)
                        self.queue.enqueue(self.BPLS_message2)
                        
                if self.BVSK_is_tested: 
                    self.generate_BVSK_message()
                    self.queue.enqueue(self.BVSK_message)
                    
                if self.BPAS_is_tested:
                    data = int.from_bytes(self.message_recv.data[4:6],byteorder = "little", signed = False)
                    command = self.message_recv.data[2:3]
                    channel = int.from_bytes(self.message_recv.data[3:4],byteorder = "big", signed = False)
                    
                    if command == Command.confirm_read: #Read confirmed
                        self.gui.BPAS.entry[channel-1].set(data)
                        for i in range(16):
                            self.gui.BPAS.entry[i].KZ.set(0)
                    if command == Command.error:
                        for i in range(16):
                            self.gui.BPAS.entry[i].KZ.set((data>>i)&1)
                    if channel == 16:
                        channel = 0
                    self.queue.enqueue(self.BPAS_message[channel])

                if self.BPSK_is_tested:
                    data = int.from_bytes(self.message_recv.data[4:8],byteorder = "little", signed = False)
                    command = self.message_recv.data[2:3]

                    if command == Command.confirm_read:
                        for i in range (20):
                            self.gui.BPSK.entry[i].set((data>>i)&1)
                    self.queue.enqueue(self.BPSK_message)

                if self.BTSAP_is_tested:
                    command = self.message_recv.data[2:3]
                    data = int.from_bytes(self.message_recv.data[4:8],byteorder = "little", signed = False)
                    
                    if command == Command.error:
                        for i in range(4):
                            self.gui.BTSAP.entry[i].KZ.set((data>>i)&1)
                    else: 
                        for i in range(4):
                            self.gui.BTSAP.entry[i].KZ.set(0)                    
                    self.generate_BTSAP_message()
                    self.queue.enqueue(self.BTSAP_message)

                    
                 
                #Set None
                self.message_recv = None
            else:
                pass
            
        except Exception as e:
            print(e)
                
        """OUTPUT handling"""
        if self.message_sent != None:
            self.gui.print_package(self.message_sent,True)
            self.message_sent = None
        self.gui.update()
       

    def exchange(self): #SEPARATE THREAD!!!
        while True:
            self.exchange_allow.wait()
            self.exchange_allow.clear()
            if self.gui.settings.is_modified:
                try:
                    self.bus = None
                    self.bus = can.interface.Bus(bustype = self.gui.settings.bustype,
                                                 channel = self.gui.settings.channel,
                                                 bitrate = self.gui.settings.bitrate)
                    self.connected_flag = True
                    self.connected_print_flag = True
                except Exception as e:
                    self.last_exception = e
                    self.connected_flag = False
                finally:
                    self.gui.settings.is_modified = False    
            if self.connected_flag:
                try:
                    with self.exchange_lock:
                        if not self.queue.is_empty():
                            message_out = self.queue.dequeue()
                            self.message_sent = message_out
                            self.bus.send(message_out)
                            message_out = None
                            message = self.bus.recv(timeout = self.exchange_timeout)

                            #### No Response handling
                            if message is None:
                                self.no_connection = True
                                if self.BPLS_is_tested:
                                    self.queue.enqueue(self.BPLS_message0)
                                if self.BPAS_is_tested:
                                    self.queue.enqueue(self.BPAS_message0)
                                if self.BPSK_is_tested:
                                    self.queue.enqueue(self.BPSK_message)
                                if self.BVSK_is_tested:
                                    self.queue.enqueue(self.BVSK_message)
                                if self.BTSAP_is_tested:
                                    self.queue.enqueue(self.BTSAP_message)                                
                            else:
                                self.no_connection = False
                            self.message_recv = message
                except Exception as e:
                    self.last_exception = e
            

    def disconnect(self):
        self.drop_test_flags()
        self.gui.status_output.appendPlainText("Соединение прервано.")
        self.connected_flag = False
        time.sleep(0.6)
        self.bus = None

    def drop_test_flags(self):
        self.BTSAP_is_tested = False
        self.BPAS_is_tested = False
        self.BPLS_is_tested = False
        self.BVSK_is_tested = False
        self.BPSK_is_tested = False

        self.queue.purge()

    def test_BTSAP (self):
        self.drop_test_flags()

        self.generate_BTSAP_message()
        
        #Алгоритм проверки
        if self.connected_flag:
            self.BTSAP_is_tested = True
            self.gui.status_output.appendPlainText("")
            self.gui.status_output.appendPlainText("Проверка БЦАП-4...")
            self.gui.status_output.appendPlainText("Установите выходное напряжение на каналах 1,2,3,4. Измеренное напряжение должно соответствовать установленному.")

            self.queue.enqueue(self.BTSAP_message)
        else:
            self.gui.status_output.appendPlainText("Перед проверкой необходимо установить соединение.")

    def generate_BTSAP_message(self):
        data = b''
        data += Address.BTSAP
        data += Address.BCPU
        data += Command.write
        data += b'\x00'
        try:
            for i in range (4):
                data += int(self.gui.BTSAP.entry[i].value()/10*255).to_bytes(1, byteorder='little', signed = False)
        except Exception as e:
            print(e)
    
        self.BTSAP_message = can.Message(arbitration_id = Arbitration.BCPU, data = data)

    def test_BPLS (self):
        self.drop_test_flags()
        
        #Get initial data
        if self.gui.BPLS.getChannel() == 1:
            address = Address.BPLS1
        else:
            address = Address.BPLS2

        #Create requests            
        data = b''
        data += address
        data += Address.BCPU
        data += Command.read
        self.BPLS_message1 = can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x01\x00\x00\x00\x00")
        self.BPLS_message2 = can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x02\x00\x00\x00\x00")

        data0 = b''
        data0 += Address.BPLS0
        data0 += Address.BCPU
        data0 += Command.read
        self.BPLS_message0 = can.Message(arbitration_id = Arbitration.BCPU, data = data0+b"\x01\x00\x00\x00\x00")            


        #Алгоритм проверки
        if self.connected_flag:
            self.BPLS_is_tested = True
            self.gui.status_output.appendPlainText("")
            self.gui.status_output.appendPlainText("Проверка БПЛС-48...")
            self.gui.status_output.appendPlainText("Положение переключателей на стенде должно соответствовать изображенному на экране")

            self.queue.enqueue(self.BPLS_message1)
        else:
            self.gui.status_output.appendPlainText("Перед проверкой необходимо установить соединение.")

    def test_BPSK (self):
        self.drop_test_flags()

        #Create requests            
        data = b''
        data += Address.BPSK
        data += Address.BCPU
        data += Command.read
        self.BPSK_message = can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x00\x00\x00\x00\x00")

        #Алгоритм проверки
        if self.connected_flag:
            self.BPSK_is_tested = True
            self.gui.status_output.appendPlainText("")
            self.gui.status_output.appendPlainText("Проверка БПСК-20...")
            self.gui.status_output.appendPlainText("Положение переключателей на стенде должно соответствовать изображенному на экране")

            self.queue.enqueue(self.BPSK_message)
        else:
            self.gui.status_output.appendPlainText("Перед проверкой необходимо установить соединение.")

    def test_BPAS (self):
        self.drop_test_flags()
        
        #Get initial data
        if self.gui.BPAS.getChannel() == 1:
            address = Address.BPAS1
        else:
            address = Address.BPAS2
        try:  
            #Create requests            
            data = b''
            data += address
            data += Address.BCPU
            data += Command.read
            self.BPAS_message = []
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x01\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x02\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x03\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x04\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x05\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x06\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x07\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x08\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x09\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x0A\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x0B\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x0C\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x0D\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x0E\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x0F\x00\x00\x00\x00"))
            self.BPAS_message.append(can.Message(arbitration_id = Arbitration.BCPU, data = data+b"\x10\x00\x00\x00\x00"))

            data0 = b''
            data0 += Address.BPAS0
            data0 += Address.BCPU
            data0 += Command.read
            self.BPAS_message0 = can.Message(arbitration_id = Arbitration.BCPU, data = data0+b"\x00\x00\x00\x00\x00")            


            #Алгоритм проверки
            if self.connected_flag:
                self.BPAS_is_tested = True
                self.gui.status_output.appendPlainText("")
                self.gui.status_output.appendPlainText("Проверка БПАС-16...")
                self.queue.enqueue(self.BPAS_message[0])

            else:
                self.gui.status_output.appendPlainText("Перед проверкой необходимо установить соединение.")
        except Exception as e:
            print(e)
    def test_BVSK (self):
        self.drop_test_flags()

        #Create requests
        self.generate_BVSK_message()

        #Алгоритм проверки
        if self.connected_flag:
            self.gui.status_output.appendPlainText("")
            self.gui.status_output.appendPlainText("Проверка БВСК...")
            self.gui.status_output.appendPlainText("При установке галочек Н1...Н16 должны загораться соответствующие светодиоды.")
            self.BVSK_is_tested = True

            self.queue.enqueue(self.BVSK_message)
        else:
            self.gui.status_output.appendPlainText("Перед проверкой необходимо установить соединение.")

    def generate_BVSK_message(self):
        data = b''
        data += Address.BVSK
        data += Address.BCPU
        data += Command.write
        data += b"\x00"
        data += self.gui.BVSK.config_byte()
        data += b"\x00\x00"
        self.BVSK_message = can.Message(arbitration_id = Arbitration.BCPU, data = data)

        
            
class Window (QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(436,700)
        self.setFixedWidth(436)
        self.setMinimumHeight(700)
        self.setWindowTitle("Программа проверки блоков ПУ-180М")
        
        #Add modules
        self.settings = Settings() # not (self)!
        self.BTSAP = BTSAP() # not (self)!
        self.BPLS = BPLS()
        self.BPSK = BPSK()
        self.BPAS = BPAS()
        self.BVSK = BVSK()

        self.tabs = QTabWidget(self)
        self.tabs.resize(435,221)
        self.tabs.move(2,2)
        self.tabs.addTab(self.settings, "Связь")
        self.tabs.addTab(self.BTSAP,"БЦАП-4")
        self.tabs.addTab(self.BPLS,"БПЛС-48")
        self.tabs.addTab(self.BPSK,"БПСК-20")
        self.tabs.addTab(self.BPAS,"БПАС-16")
        self.tabs.addTab(self.BVSK,"БВСК-16")

        #Lower interface
        self.output_label = QLabel(self)
        self.output_label.setText("Журнал обмена")
        self.output_label.resize(100,15)
               
        self.status_output = QPlainTextEdit(self)
        self.status_output.setFont(QFont("Courier"))
        self.status_output.setReadOnly(True)

        self.invalid_request_entry = FlagEntry(self)
        self.invalid_request_entry.setText("Некорр.запрос")
        self.invalid_request_entry.flag.setColors(QColor(255,0,0),QColor(255,255,255))
        self.invalid_request_entry.resize(100,20)

        self.invalid_address_entry = FlagEntry(self)
        self.invalid_address_entry.setText("Некорр.адрес")
        self.invalid_address_entry.flag.setColors(QColor(255,0,0),QColor(255,255,255))
        self.invalid_address_entry.resize(100,20)

        self.error_entry = FlagEntry(self)
        self.error_entry.setText("Ошибка блока")
        self.error_entry.flag.setColors(QColor(255,0,0),QColor(255,255,255))
        self.error_entry.resize(100,20)

        self.no_connection_entry = FlagEntry(self)
        self.no_connection_entry.setText("Нет ответа")
        self.no_connection_entry.flag.setColors(QColor(255,0,0),QColor(255,255,255))
        self.no_connection_entry.resize(100,20)

    def print_package(self,message,io):
        if io:
            starter = "Отправлен пакет: "
        else:
            starter = "Принят пакет:    "
        string = message.data.hex()
        aid = message.arbitration_id
        self.status_output.appendPlainText(starter + " "
                                           + "id "+"{:2}".format(aid) + ": "
                                           + string[0:2] + " "
                                           + string[2:4] + " "
                                           + string[4:6] + " "
                                           + string[6:8] + "   "
                                           + string[8:10] + " "
                                           + string[10:12] + " "
                                           + string[12:14] + " "
                                           + string[14:16] + " "
                                           + string[16:18])
    def print_exception(self,exception):
        self.status_output.appendPlainText("Ошибка: " + str(exception))

    def print_connected(self):
        self.status_output.appendPlainText("")
        self.status_output.appendPlainText("Открыто соединение с параметрами: "
                                           + str(self.settings.channel) + "; "
                                           + str(self.settings.bitrate) + "; "
                                           + str(self.settings.bustype) + ".")
        
    def paintEvent(self,Event):
        if self.tabs.currentIndex() == 4:
            self.tabs.resize(435,421)
        else:
            self.tabs.resize(435,221)
            
        self.output_label.move(self.tabs.x()+5,self.tabs.y()+self.tabs.height()+5)
        self.status_output.move(self.tabs.x(),self.output_label.y()+self.output_label.height()+5)
        
        self.status_output.resize(433,self.height()-20-(self.output_label.y()+self.output_label.height()+5))
        self.invalid_request_entry.move(5,self.height()-20)
        self.invalid_address_entry.move(self.invalid_request_entry.x()+self.invalid_request_entry.width()+5,self.height()-20)
        self.error_entry.move(self.invalid_address_entry.x()+self.invalid_address_entry.width()+5,self.height()-20)
        self.no_connection_entry.move(self.error_entry.x()+self.error_entry.width()+5,self.height()-20)

        

class Command():
    read = b"\x01"
    write = b"\x02"
    confirm_read = b"\xF1"
    confirm_write = b"\xF2"
    invalid_request = b"\xE0"
    invalid_address = b"\xEE"
    error = b"\x0E"
        
class Address():
    BCPU  = b"\xAA"
    BPAS1 = b"\xB1"
    BPAS2 = b"\xB2"
    BPLS1 = b"\xC1"
    BPLS2 = b"\xC2"
    BVSK  = b"\xD0"
    BPSK  = b"\xE0"
    BTSAP = b"\xF0"

    BPAS0 = b"\xB0"
    BPLS0 = b"\xC0"


class Arbitration():
    BCPU  = 1
    BPAS1 = 3
    BPAS2 = 5
    BPLS1 = 7
    BPLS2 = 9
    BVSK  = 11
    BPSK  = 13
    BTSAP = 15

class Sensor():
    BK1 = b"\x06"
    BK2 = b"\x05"
    BK3 = b"\x0C"
    BK4 = b"\x0A"
    BK5 = b"\x1A"
    BK6 = b"\x0B"
    BK7 = b"\x1B"
    BK8 = b"\x0E"
    BK9 = b"\x0D"
    BK10 = b"\x09"
    BK11 = b"\x15"
    BP1 = b"\x1E"
    BP2 = b"\x1D"
    BP3 = b"\x1C"
    BP4 = b"\x03"
    DP1 = b"\x13"
    DP2 = b"\x16"
    DP3 = b"\x04"
    DP4 = b"\x08"
    DP5 = b"\x19"

class RequestQueue():   
    def __init__(self):
        self.queue = []
        self.line_default = None      

    def enqueue(self,message):
        self.queue.insert(0,message)
        
    def dequeue(self):
        if self.is_empty():
            return self.line_default
        else:
            return self.queue.pop()

    def is_empty(self):
        if len(self.queue) == 0:
            return True
        else:
            return False
    def len(self):
        return len(self.queue)

    def purge(self):
        self.queue = []

m = Main()
