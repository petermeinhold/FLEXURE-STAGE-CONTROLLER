# -*- coding: utf-8 -*-

import serial
import time
import numpy as np
import seaborn as sns
import serial.tools.list_ports
import threading

from PyQt5 import QtWidgets, uic
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        self.ser = None
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi(r'flexure controller rev A.ui', self) # Load the .ui file
        #ASSIGN FUNCTIONS TO BUTTONS
        self.pushButton_Connect.clicked.connect( self.pushButton_Connect_Pressed ) 
        self.pushButton_Step.clicked.connect( self.move_z )
        self.pushButton_Home_Z.clicked.connect( self.home_z )
        self.pushButton_hello.clicked.connect( self.hello )   
        self.pushButton_Set_DAC_1.clicked.connect( self.set_DAC_1 )  
        self.pushButton_Set_DAC_2.clicked.connect( self.set_DAC_2 )  
        self.pushButton_amp_off.clicked.connect( self.amp_off )
        self.pushButton_read_serial_number.clicked.connect( self.read_serial_number )
        self.pushButton_DAC1_square.clicked.connect( self.DAC1_square )
        self.pushButton_DAC2_square.clicked.connect( self.DAC2_square ) 
        self.pushButton_Square_Stop.clicked.connect( self.Square_Stop ) 
        self.pushButton_recording_on.clicked.connect( self.recording_on ) 
        self.file = None
        self.is_recording = 0
        
        #find ports and populate combo box
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.comboBox_Port_Select.addItem(p.name, p)
        self.show() # Show the GUI
        
    
    def recording_on(self):
        if not self.is_recording:
            self.is_recording = 1
            self.pushButton_recording_on.setText( "Stop Recording" )
            f = float(  self.lineEdit_recording_frequency.text()  ) 
            filename =  self.lineEdit_filename.text()  
            self.file = open( filename , "a")
            test_str = 'record_on'  
            test_str += str( f  )    +  '\r\n'
            self.textBrowser.append("OUT: " + test_str)
            self.ser.write( test_str.encode('ascii') ) 
            
            
        else:
            self.is_recording = 0
            self.pushButton_recording_on.setText("Start Recording")
            test_str = 'record_off'  
            self.ser.write( test_str.encode('ascii') ) 
            self.file.close()
            
            
    
    def Square_Stop(self):
        test_str = 'Square_Stop'  
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        
        
    def DAC1_square(self):
        f = float(  self.lineEdit_f.text()  )
        test_str = 'DAC1_square'  
        test_str += str( f  )    +  ','   
        test_str += str(self.lineEdit_min.text()  )  +  ','  
        test_str += str( self.lineEdit_max.text()  )  +  '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
    
    def DAC2_square(self):
        f = float(  self.lineEdit_f.text()  )
        test_str = 'DAC2_square'  
        test_str += str( f  )    +  ','   
        test_str += str(self.lineEdit_min.text()  )  +  ','  
        test_str += str( self.lineEdit_max.text()  )  +  '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
  
        
    def home_z(self):
        test_str = 'home_z\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
     
    def read_serial_number(self):
        test_str = 'read_serial_number\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        
    def amp_off(self):
        test_str = 'amp_off\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        
        
    def set_DAC_1(self):
        value = int( self.lineEdit_DAC1.text() )
        test_str = 'setDAC1'  + str(value) + '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 

     
    def set_DAC_2(self):
        value = int( self.lineEdit_DAC2.text() )
        test_str = 'setDAC2'  + str(value) + '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        

           
    def move_z(self):
        steps = int( self.lineEdit_steps.text() )
        test_str = 'move_z'  + str(steps) + '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
    
    
    def hello(self):

        test_str = 'hello\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        
    
    def read_from_port(self):
        while True:
            try:
               serial_in = self.ser.readline().decode()
               if serial_in:
                   print( "IN: " + serial_in )
                   if serial_in[:5] == 'state':
                       self.file.write( serial_in )
                   else:
                       self.textBrowser.append( "IN : " + serial_in )
            except:
                pass
    
    def pushButton_Connect_Pressed(self) :
        selected_port = self.comboBox_Port_Select.itemData( self.comboBox_Port_Select.currentIndex())
        self.ser = serial.Serial( selected_port.device, 115200, timeout=1)
        #self.ser.isOpen()
        self.ser.flushInput()
        self.ser.flushOutput()
        self.pushButton_Connect.setText(str( self.ser.isOpen() )) 
        
        thread = threading.Thread( target = self.read_from_port )
        thread.start()


        

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()

