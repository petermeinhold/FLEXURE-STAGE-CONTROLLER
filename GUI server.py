# -*- coding: utf-8 -*-

import serial
import time
import numpy as np
import seaborn as sns
import serial.tools.list_ports


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
        self.pushButton_amp_on.clicked.connect( self.amp_on )  
        
        self.pushButton_stepper_on.clicked.connect( self.stepper_on ) 
        self.pushButton_stepper_off.clicked.connect( self.stepper_off )    
        
        self.pushButton_read_settings.clicked.connect( self.read_settings ) 
        
        self.pushButton_read_serial_number.clicked.connect( self.read_serial_number )
        #find ports and populate combo box
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.comboBox_Port_Select.addItem(p.name, p)
        self.show() # Show the GUI
    
    
    def read_settings(self):
        test_str = 'read_settings\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
        
    def stepper_on(self):
        test_str = 'stepper_on\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
    def stepper_off(self):
        test_str = 'stepper_off\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
        
    def home_z(self):
        test_str = 'home_z\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
     
    def read_serial_number(self):
        test_str = 'read_serial_number\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
    def amp_off(self):
        test_str = 'amp_off\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
    def amp_on(self):
        test_str = 'amp_on\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
    def set_DAC_1(self):
        value = int( self.lineEdit_DAC1.text() )
        test_str = 'setDAC1'  + str(value) + '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
     
    def set_DAC_2(self):
        value = int( self.lineEdit_DAC2.text() )
        test_str = 'setDAC2'  + str(value) + '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
        
    def pushButton_Connect_Pressed(self) :
        selected_port = self.comboBox_Port_Select.itemData( self.comboBox_Port_Select.currentIndex())
        self.ser = serial.Serial( selected_port.device, 115200, timeout=1)
        #self.ser.isOpen()
        self.ser.flushInput()
        self.ser.flushOutput()
        self.pushButton_Connect.setText(str( self.ser.isOpen() )) 
        
        
    def move_z(self):
        steps = int( self.lineEdit_steps.text() )
        test_str = 'move_z'  + str(steps) + '\r\n'
        self.textBrowser.append("OUT: " + test_str)
        self.ser.write( test_str.encode('ascii') ) 
        line =  self.ser.readline().decode('utf-8') 
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
        self.textBrowser.append( "In : " + line )
    
    
    def hello(self):
        print( 'doot' )
        test_str = 'hello\r\n'
        self.textBrowser.append("OUT: " + test_str)
        print( 'doot' )
        self.ser.write( test_str.encode('ascii') ) 
        print( 'doot' )
        line =  self.ser.readline().decode('utf-8') 
        print( 'line' , line)
        while not line: #wait for pyboard to respond
            line =  self.ser.readline().decode('utf-8') 
            print( 'line' , line)
        self.textBrowser.append( "In : " + line )

        

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()


###############################################
#THINGS BELOW THIS LINE ARE FROM BEFORE THE GUI VERSION AND
#NEED TO BO MODIFIED AND INCLUDED ABOVE



n_samples = 4000#1700
bottom_clip = 0 #ignore incoming samples with values below bottom_clip
samples = []
x_pos = []
y_pos = []

def raster_scan():
    print("Begin function raster_scan")
    start_time = time.time()
    ser.write(b'raster_scan\r\n') 
    line =  ser.readline().decode('utf-8') 
    if not line:
        print("no response from pyboard")
        print("End function raster_scan\r\n")
        return 0
    if line == 'raster_start\r\n':
        print('Correct response received: ', line.strip("\r\n"))
    else:
        print("Wrong response: ", line.strip("\r\n"))
        print("End function raster_scan\r\n")
        return 0
    samples = []
    x_pos = []
    y_pos = []
    i = 0
    while 1:
        if i%1000 == 0:
            print("n_samples so far: ", i)
        i += 1
        line = ser.readline().decode('utf-8')   #this line should be photodiode value, x_pos, y_pos or 'raster_end\r\n'
        if line == 'raster_end\r\n':
            print('received raster end from board')
            break
        print('received line: ', line)
        
        if line[0:5] == 'sample':
            print('SAMPLE')
            line = line[5:]
            print( line )
            break

        received_values = line.split(",")
        received_values[-1] = received_values[-1].strip("\r\n")
        #print(x)
        #if float(received_values[0])*3.3/2**16 > bottom_clip: #ignore incoming samples with values below bottom_clip
        samples.append(float(received_values[0])*3.3/2**16)
        x_pos.append(float(received_values[1]))
        y_pos.append(float(received_values[2]))
    end_time = time.time()
    print("raster scan sample count: ", len( x_pos ))
    print("raster scan elapsed time = " , end_time - start_time)  

    
    print("End function raster_scan\r\n")
    return x_pos, y_pos, samples


def start_dither(n_samples = 400): 
    print("Begin function start_dither")
    start_time = time.time()
    samples = []
    x_pos = []
    y_pos = []
    
    for i in range( n_samples ): #request dithers one at a time
        if i%100 == 0:
            print("n_samples so far: ", i)

        ser.write(b'dither\r\n')  #request one pass through dither and gradient ascent
        line = ser.readline() #this line should be confirmation: 'dither_start\r\n'
        #print("------------", line) #line is b'dither_start\r\n'
        if line:
            line = line.decode('utf-8') 
        else:
            print("no response from pyboard")
            print("End function start_dither")
            return 0
        if line == 'dither_start\r\n':
            #print('Correct response received: ', line.strip("\r\n"))
            pass
        else:
            print("Wrong response: ", line.strip("\r\n"))
            print("End function start_dither")
            return 0

        line = ser.readline().decode('utf-8')  #this line should be photodiode value, x_pos, y_pos
        #print("line", line)
        received_values = line.split(",")
        received_values[-1] = received_values[-1].strip("\r\n")
        if float(received_values[0])*3.3/2**16 > bottom_clip: #ignore incoming samples with values below bottom_clip
            samples.append(float(received_values[0])*3.3/2**16)
            x_pos.append(float(received_values[1]))
            y_pos.append(float(received_values[2]))
        
            
    end_time = time.time()
    print("dither steps: ", len( x_pos ))
    print("dither time = " , end_time - start_time)
    #ax.plot(x_pos, y_pos, samples, linewidth=7.0, c='g', zorder=2)
    
    
    print("End function start_dither\r\n")
    print('max value:', max(samples))
 

    return x_pos, y_pos, samples

def square():
    ser.write(b'square\r\n') 
    line =  ser.readline().decode('utf-8') 
    if line == 'square\r\n':
        print('Correct response received: ', line.strip("\r\n"))
        return 1
    else:
        print("Wrong response: ", line.strip("\r\n"))
        line =  ser.readline().decode('utf-8') 
        return 0













