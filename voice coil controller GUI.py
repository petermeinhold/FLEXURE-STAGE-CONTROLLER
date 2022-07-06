
from PyQt5 import QtCore, uic, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QAction
import serial
import serial.tools.list_ports
import sys
import time
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QIODevice

qtCreatorFile = "Voice_Coil_GUI.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
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
        self.connect_button.toggled.connect(self.connection_toggle)
        self.send_button.clicked.connect( self.send_text_from_box )
        
        #signal generator connections
        self.square_checkBox.clicked.connect( self.square_checkBox_toggled )
        self.amp_enable_checkBox.clicked.connect( self.amp_enable_check_clicked )
        self.drv_enable_checkBox.clicked.connect( self.drv_enable_check_clicked )
        #self.gradient_ascent_checkBox.clicked.connect( self.gradient_ascent_clicked )
        self.sine_checkBox.clicked.connect(self.sine_checkBox_toggled )
        self.Signal_generator_start_pushButton.clicked.connect( self.SG_start )
        self.dither_start_pushButton.clicked.connect( self.dither_start )
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
        #serial port combo box setup
        try:
            port_list = list(serial.tools.list_ports.comports())
            for port in port_list:
                self.port_combo_box.addItem( str(port).split()[0] )
                self.port_combo_box.setCurrentIndex(self.port_combo_box.count() - 1) 
        except Exception as e:
            print("Error getting connected serial devices!\nError message:" + str(e))
            
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)   



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

    def move_z(self):
        message = 'move_z,' + self.n_steps_lineEdit.text() + ','  + self.step_delay_lineEdit.text()
        print('message: ', message)
        self.send( message ) 
        return 0
    
    def home_z(self):
        self.send( 'home_z' )
        return 0
        
    def stop(self):   
        self.send('stop')
    def get_serial_number(self):
        self.send('get_serial_number')
    
    def SG_start(self):   
        message = 'signal_generator,'
        message += str( int(self.square_checkBox.isChecked() ) )+ ','
        message += str( int(self.X_checkBox.isChecked() )) + ','
        message += str( int(self.Y_checkBox.isChecked() )) + ','
        message += self.Signal_generator_f_lineEdit.text() + ','
        message += self.Signal_generator_A_lineEdit.text() 
        print('message: ', message)
        #square, x, y, f, A
        self.send( message )
        
    def dither_start(self):   
        #frequency, amplitude, gradient ascent on/off, gradient ascent step size, ascent threshold
        message = 'dither_start,'
        message += self.dither_f_lineEdit.text() + ','
        message += self.dither_A_lineEdit.text() + ','
        if self.gradient_ascent_checkBox.isChecked():
            message += '1,'
        else:
            message += '0,'
        message += self.ascent_distance_lineEdit.text() + ','  + self.ascent_threshold_lineEdit.text()
        
        print('message: ', message)
        self.send( message )
    
    
    @QtCore.pyqtSlot(bool)
    def connection_toggle(self, checked):
        print("connection_toggle pressed")  
        self.connect_button.setText("Disconnect" if checked else "Connect")
        if checked:
            self.port = self.port_combo_box.currentText()
            print("connecting to port", self.port )
            self.serial = QtSerialPort.QSerialPort(self.port, baudRate=QtSerialPort.QSerialPort.Baud115200, readyRead=self.receive)
 
            if self.serial.open(QIODevice.ReadWrite):
                self.serial.setBaudRate(115200)
            else:
                print('Cannot connect to device')
                raise IOError( "Cannot connect to device" )
            
            self.serial.setDataTerminalReady(True)
            print('serial: ',  self.serial)
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.connect_button.setChecked(False)
        else:
            print('closing serial port')
            self.serial.close()


         
    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            print('serial receive')
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.received_text.setPlainText( self.received_text.toPlainText() +   '>>>  ' + text  + '\r\n' )
            #self.received_text.setPlainText( text )
            #self.output_te.append(text)
            #self.received_text.setText( text )
            all_data_list = text.split(sep=',')   
            
         
                
            if ((all_data_list[0]=='params') and (all_data_list[-1]=='end')):
                for i in range(10):
                    self.adc_vals[i] = float(all_data_list[i+1])
                    
                self.dac1_read = float(all_data_list[11])
                self.dac2_read = float(all_data_list[12])
                
                self.pre_good = int(all_data_list[13])
                self.pwr_good = int(all_data_list[14])
                self.tec_t_good = int(all_data_list[15])
                self.pre_ext_en = int(all_data_list[16])
                self.pwr_ext_en = int(all_data_list[17])
        
                
                self.ADCVAL1.setText( str( self.adc_vals[0] ) ) 
                self.ADCVAL2.setText( str( self.adc_vals[1] ) ) 
                self.ADCVAL3.setText( str( self.adc_vals[2] ) ) 
                self.ADCVAL4.setText( str( self.adc_vals[3] ) ) 
                self.ADCVAL5.setText( str( self.adc_vals[4] ) ) 
                self.ADCVAL6.setText( str( self.adc_vals[5] ) ) 
                self.ADCVAL7.setText( str( self.adc_vals[6] ) ) 
                self.ADCVAL8.setText( str( self.adc_vals[7] ) ) 
                self.ADCVAL9.setText( str( self.adc_vals[8] ) ) 
                self.ADCVAL10.setText( str( self.adc_vals[9] ) )  
                
                self.pre_good_text.setText( str( self.pre_good ) ) 
                self.pwr_good_text.setText( str( self.pwr_good  ) ) 
                self.tec_t_good_text.setText( str( self.tec_t_good  ) )
                self.pre_ext_en_text.setText( str( self.pre_ext_en ) ) 
                self.pwr_ext_en_text.setText( str( self.pwr_ext_en ) )  
                
                self.DAC1_text.setText( str( self.dac1_read ) )          
                self.DAC2_text.setText( str( self.dac2_read ) )    
            print(all_data_list)
        
        #save samples to CSV
        if self.record_button.isChecked():
            for i in range(12):
                self.file.write(all_data_list[i+1] + ',') 
            self.file.write('\n')          


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
        

    def closeEvent(self, event):
        print('closeEvent')
        try:
            self.serial.close()
        except:
            pass
        try:
            self.file.close()
        except:
            pass
           
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
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

