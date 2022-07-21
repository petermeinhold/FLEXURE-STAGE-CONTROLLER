
from PyQt5 import QtCore, uic, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QAction
import serial
import serial.tools.list_ports
import sys
import time
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QIODevice, QObject

qtCreatorFile = "Voice_Coil_GUI.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Fiber_actuator( QObject ): #subclass of QObject so it has its own port, signals, and slots
    def __init__(self, port_name = 0):
        super(Fiber_actuator, self).__init__()
        self.port_name = port_name #name of serial port
        self.serial= None #actual serial port object
        self.serial_number = -1 #serial number as read from pyboard 
        self.received_text = ''
        print('Fiber_actuator init with  port_name = ', port_name )
        if port_name: 
            self.connect_to_port( port_name ) 
            self.get_serial_number()
            
    #@QtCore.pyqtSlot()
    def connect_to_port(self, port_name):
        print("connecting to port", port_name )
        self.serial= QtSerialPort.QSerialPort( port_name, baudRate=QtSerialPort.QSerialPort.Baud115200, readyRead = self.receive)    
        print('serial: ',  self.serial)
        if self.serial.open(QIODevice.ReadWrite):
            self.serial.setBaudRate(115200)
        else:
            #print('Cannot connect to device')
            raise IOError( "Cannot connect to device" )
        
        self.serial.setDataTerminalReady(True)
        if not self.serial.isOpen():
            if not self.serial.open(QtCore.QIODevice.ReadWrite):
                self.connect_button.setChecked(False)
        return 1
    
    def get_serial_number(self):
        self.send('get_serial_number')
        self.serial.waitForReadyRead( 500 )
        #time.sleep(.5)
    
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            print('text received: ', text)
            text = text.rstrip('\r\n')
            #self.received_text.setPlainText( self.received_text.toPlainText() +   '>>>  ' + text  + '\r\n' )
            #self.received_text.setPlainText( text )
            #self.output_te.append(text)
            #self.received_text.setText( text )
            all_data_list = text.split(sep=',')   
            
            if ((all_data_list[0]=='serial_number') and (all_data_list[-1]=='end')):
                self.serial_number = all_data_list[1]
                print('serial number received:' , self.serial_number)

    def send(self, text):
        to_send = ( text  + '\r\n').encode()
        print("sending" , to_send)
        #self.received_text.setPlainText( self.received_text.toPlainText() +   '<<<  ' + text + '\r\n' )
        self.serial.write( to_send )     
        

        
    
    def move_z(self, steps, delay):
        message = 'move_z,' + steps + ',' + delay
        self.send( message )        
    def dac_set(self, x, y):
        message = 'DAC_set,'+  x + ',' + y
        self.send( message )
    
    def stop(self):
        self.send('stop')
        
    def dither_start( self, frequency, amplitude, ascent_on, ascent_step_size, ascent_threshold, adc_delay):
        message = 'dither_start,'
        message += frequency  + ','
        message += amplitude + ','
        if ascent_on:
            message += '1,'
        else:
            message += '0,'
        message += ascent_step_size + ','  
        message += ascent_threshold + ','   
        message += adc_delay + ','   
        
        print('message: ', message)
        self.send( message )
    def SG_start(self, square, x, y, f, a):
        message = 'signal_generator,'
        message += str( int(square) )+ ','
        message += str( int( x ) )+ ','
        message += str( int( y ) )+ ','
        message += f + ','
        message += a
        print('message: ', message)
        #square, x, y, f, A
        self.send( message )
    def disconnect(self):
        try:
            self.serial.close()
        except:
            pass
        self.serial = None
        
    """
    def SG_start(self):
    def dither_start(self):   
    """
    
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        #the whole device is always in a mode, which determines what it does in the callback 
        self.Mode = 0 
        #0 stand by
        #1 signal generator
        #2 dither and lock
        
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('Fiber Actuator Controller')

        self.port = None
        self.connect_button.setCheckable(True)
        self.connect_all_button.setCheckable(True)
        
        self.connect_button.toggled.connect(self.connection_toggle) 
        self.connect_all_button.toggled.connect(self.connect_all_toggle)
        self.actuators_combo_box.currentTextChanged.connect( self.actuators_combo_change )
        
        self.send_button.clicked.connect( self.send_text_from_box )
        self.DAC_set_pushButton.clicked.connect( self.DAC_set )
        
        #signal generator connections
        self.square_checkBox.clicked.connect( self.square_checkBox_toggled )
        self.amp_enable_checkBox.clicked.connect( self.amp_enable_check_clicked )
        self.drv_enable_checkBox.clicked.connect( self.drv_enable_check_clicked )
        #self.gradient_ascent_checkBox.clicked.connect( self.gradient_ascent_clicked )
        self.sine_checkBox.clicked.connect(self.sine_checkBox_toggled )
        self.Signal_generator_start_pushButton.clicked.connect( self.SG_start )
        self.dither_start_pushButton.clicked.connect( self.dither_start ) 
        self.refresh_ports_pushButton.clicked.connect( self.refresh_ports )
        self.get_serial_number_pushButton.clicked.connect( self.get_serial_number )
        
        self.move_z_pushButton.clicked.connect( self.move_z )############
        self.home_z_pushButton.clicked.connect( self.home_z )
        
        self.Signal_generator_stop_pushButton.clicked.connect( self.stop )   
        self.square_checkBox.setChecked(True)
        self.X_checkBox.setChecked(True)
        self.Y_checkBox.setChecked(True)
        self.gradient_ascent_checkBox.setChecked(True)


        self.fileName = "" #full path to csv file
        self.filename_button.clicked.connect( self.browse_file )
        
        
        self.record_button.setCheckable(True)
        self.record_button.toggled.connect(self.record_toggle)
        self.file  = None
        self.record_button.setStyleSheet("background-color: green")
        
        self.refresh_ports()
        self.fiber_actuators_list = [] # [Fiber_actuator()]
        self.selected_actuator = 0
        
        
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)   
        

        
#GUI FUNCTIONS       
    def refresh_ports(self):
        #serial port combo box setup
        self.port_combo_box.clear()
        try:
            port_list = list(serial.tools.list_ports.comports())
            for port in port_list:
                self.port_combo_box.addItem( str(port).split()[0] )
                self.port_combo_box.setCurrentIndex(self.port_combo_box.count() - 1) 
        except Exception as e:
            print("Error getting connected serial devices!\nError message:" + str(e))
    def amp_enable_check_clicked(self):
        if self.amp_enable_checkBox.isChecked():
            self.amp_enable_checkBox.setChecked(True)
            self.send('amp_enable')        
        else:
            self.amp_enable_checkBox.setChecked(False)  
            self.send('amp_disable')
    def drv_enable_check_clicked(self):
        if self.drv_enable_checkBox.isChecked():
            self.drv_enable_checkBox.setChecked(True)
            self.send('drv_enable')       
        else:
            self.drv_enable_checkBox.setChecked(False)  
            self.send('drv_disable')
    #signal generator functions
    def square_checkBox_toggled(self):   
        self.sine_checkBox.setChecked(False)
        self.square_checkBox.setChecked(True)     
    def sine_checkBox_toggled(self):   
        self.sine_checkBox.setChecked(True)
        self.square_checkBox.setChecked(False) 
        
#SINGLE ELEMENT FUNCTIONS     
    def SG_start(self):  
        self.selected_actuator.SG_start( self.square_checkBox.isChecked(), int( self.X_checkBox.isChecked() ),
             int(self.Y_checkBox.isChecked()) , self.Signal_generator_f_lineEdit.text(), self.Signal_generator_A_lineEdit.text() )

        
    def DAC_set(self):
        self.selected_actuator.DAC_set( self.x_value_lineEdit.text(),  self.y_value_lineEdit.text())       
        #frequency, amplitude, gradient ascent on/off, gradient ascent step size, ascent threshold

        
    def move_z(self):
        self.selected_actuator.move_z( self.n_steps_lineEdit.text(),  self.step_delay_lineEdit.text() ) 
        return 0
    
    def home_z(self):
        self.selected_actuator.move_z(-2000)
        return 0
        
    def stop(self):   
        self.selected_actuator.stop()
        
    def get_serial_number(self):
        self.selected_actuator.get_serial_number()
        return 0
    

        
    def dither_start(self):   
        #frequency, amplitude, gradient ascent on/off, gradient ascent step size, ascent threshold
        self.selected_actuator.dither_start(self.dither_f_lineEdit.text(), self.dither_A_lineEdit.text(), 
                         self.gradient_ascent_checkBox.isChecked(), self.ascent_distance_lineEdit.text(),
                         self.ascent_threshold_lineEdit.text(), self.ADC_delay_lineEdit.text()  )

    
#serial port management   
    def actuators_combo_change(self):
        self.selected_actuator = self.fiber_actuators_list[ self.actuators_combo_box.currentIndex()   ]
        print( 'changing selected actuator to ',  self.actuators_combo_box.currentIndex())
    
    def disconnect_and_remove_actuator(self, i):
        actuator = self.fiber_actuators_list[i]
        actuator.disconnect()
        self.fiber_actuators_list.pop( i )
        self.actuators_combo_box.removeItem( i )
        del actuator
        
        
    def add_element_from_port_name(self, port_name):
        this_actuator = Fiber_actuator( port_name )
        print( ' this_actuator.serial_number',  this_actuator.serial_number)
        if this_actuator.serial_number is not -1:
            self.fiber_actuators_list.append(this_actuator)
            self.actuators_combo_box.addItem( this_actuator.serial_number ) 
            self.selected_actuator = this_actuator
            print('actuator added to list, serial number ', this_actuator.serial_number )
        else:
            print('unable to get serial number')
        print('serial: ',  this_actuator.serial)
        if not this_actuator.serial.isOpen():
            if not this_actuator.serial.open(QtCore.QIODevice.ReadWrite):
                self.connect_button.setChecked(False)

        
        
    @QtCore.pyqtSlot(bool)
    def connection_toggle(self, checked):
        print("connection_toggle pressed")  
        self.connect_button.setText("Disconnect" if checked else "Connect")
        if checked:
            #create a new actuator connected to the port named in the port selection combo box   
            self.port_name = self.port_combo_box.currentText() #self port is the port of the currently selected fiber array
            self.add_element_from_port_name( self.port_name )
        else:        
            self.disconnect_and_remove_actuator( self.port_combo_box.currentIndex()  )
    
    @QtCore.pyqtSlot(bool)
    def connect_all_toggle(self, checked):
        print("connect_all_toggle pressed")  
        self.connect_all_button.setText("Disconnect All" if checked else "Connect All")
        if checked:
            #get a list of available ports
            self.port_names = [ self.port_combo_box.itemText(i) for i in range(self.port_combo_box.count()) ]
            #loop through all ports, creating a fiber actuator object for each and connecting it to that port
            for port_name in self.port_names:
                self.add_element_from_port_name( port_name )
            #else:
            #   self.disconnect_actuator( self.port_combo_box.currentIndex()  )
        else:
            while len( self.fiber_actuators_list ) > 0:
                self.disconnect_and_remove_actuator( 0 )
        self.port = self.ports[0]
            


    @QtCore.pyqtSlot()
    def send(self, text):     
        to_send = ( text  + '\r\n').encode()
        print("sending" , to_send)
        self.received_text.setPlainText( self.received_text.toPlainText() +   '<<<  ' + text + '\r\n' )
        self.serial.write( to_send )     
        
    @QtCore.pyqtSlot()
    def send_text_from_box(self):
        text = self.send_lineEdit.text()
        self.send(text)

#called when main window is closed          
    def closeEvent(self, event):
        while len( self.fiber_actuators_list ) > 0:
                self.disconnect_and_remove_actuator( 0 )

    #File saving stuff
    @QtCore.pyqtSlot()
    def browse_file(self):
        self.fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Single File', '', '*.csv')
        print("FILE NAME", self.fileName)
        self.filename_text.setText( self.fileName )
    @QtCore.pyqtSlot(bool)
    def record_toggle(self, checked):
        print("record_toggle pressed")  
        self.record_button.setText("Stop" if checked else "Record")
        if checked:
            self.file = open(self.fileName ,'w')
            self.file.write('\n') 
            print("recording to file")
            self.record_button.setStyleSheet("background-color: red")
        else:
            self.record_button.setStyleSheet("background-color: green")
            self.file.close()
            print("closing file")
     #end of file saving stuff  
     

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

