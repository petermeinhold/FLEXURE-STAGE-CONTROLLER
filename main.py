# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 14:58:13 2021

@author: phoo
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 16:17:03 2021
3d raster main
@author: phoo
"""

# -*- coding: utf-8 -*-

import pyb
import machine 
import time
from pyb import Pin

#stepper motor config#
step_pin = Pin('X9', Pin.OUT) 
dir_pin = Pin('X10', Pin.OUT)
stepper_enable = Pin('X8', Pin.OUT)
amp_enable = Pin('X4', Pin.OUT)


# limit switch for z axis
z_limit_switch = machine.Pin('X12', machine.Pin.IN, machine.Pin.PULL_UP) 


dac1= pyb.DAC(1, bits=12) #pin X5
dac2= pyb.DAC(2, bits=12) #pin X6 
dac2.write(0) 
dac1.write(0) 
sn_0 = Pin('X18', Pin.IN, Pin.PULL_DOWN) #serial number pins
sn_1 = Pin('X19', Pin.IN, Pin.PULL_DOWN)
sn_2 = Pin('X20', Pin.IN, Pin.PULL_DOWN)
sn_3 = Pin('X21', Pin.IN, Pin.PULL_DOWN)
sn_4 = Pin('X22', Pin.IN, Pin.PULL_DOWN)

#conn = pyb.USB_VCP(id = 21)
conn = pyb.USB_VCP()
#conn.setinterrupt(-1) 

photodiode_ADC = pyb.ADC(pyb.Pin.board.Y12)  #machine.ADC(pyb.Pin.board.Y12)



    
def move_z(steps, direction):
    pyb.LED(1).on()
    ms_sleep = 3
    stepper_enable.value(1)
    dir_pin.value( direction )
    for i in range(steps): 
        pyb.LED(2).toggle()
        step_pin.value(0)
        time.sleep_ms(ms_sleep) 
        step_pin.value(1)
        time.sleep_ms(ms_sleep) 
    stepper_enable.value(0)
    pyb.LED(1).off()

def home_z():
    dir_pin.value( 0 )
    ms_sleep = 3
    stepper_enable.value(1)
    for i in range(1000): #set this number later, 1000 is a guess
        #check limit switch
        #when switch is hit, z_limit_switch.value() is 0 (normally open switch to ground with pulled up input pin)
        if z_limit_switch.value():
            pyb.LED(1).on()
        else:
            pyb.LED(1).off()
            conn.write("done homing z\r\n".encode('utf-8')) 
            stepper_enable.value(0)
            return
        pyb.LED(2).toggle()
        step_pin.value(0)
        time.sleep_ms(ms_sleep) 
        step_pin.value(1)
        time.sleep_ms(ms_sleep) 
    conn.write("timeout, switch not hit\r\n".encode('utf-8')) 
    stepper_enable.value(0) 
        
            
def advance_y_pos():
    global y_pos, y_step, y_direction
    y_pos = y_pos + y_step*y_direction
    if y_pos > 4095:
        y_pos = 4095
        y_direction = -1
        conn.write(b"raster_end\r\n")
    if y_pos <0:
        y_pos = 0
        y_direction = 1
        conn.write(b"raster_end\r\n")    

def raster_scan():
    x_step = 100 #loops over x then y
    y_step = 200
    raster_delay = 0
    oversample = 10

    global y_pos, x_pos
    #scans back and forth on x
    #after each one way traversal on x, y increments
    #when y > 4095 the whole rectangle is scanned

    x_direction = 1
    x_pos = 0
    y_pos = 0
    conn.write(b"raster_start\r\n") 
    while 1: #this loop is the whole rectangular scan
        #set dacs to current position
        dac2.write(x_pos) 
        dac1.write(y_pos) 

        #read photodiode
        photodiode_val = 0
        for i in range(oversample):
            photodiode_val += photodiode_ADC.read() #photodiode_ADC.read_u16()  # photodiode_ADC.read_core_vref() 
        photodiode_val = photodiode_val/oversample
        
        #advance to next position 
        x_pos = x_pos + x_step*x_direction
        if x_pos > 4095:
            x_pos = 4095
            x_direction = -1
            y_pos = y_pos + y_step
        if x_pos < 0:
            x_pos = 0
            x_direction = 1
            y_pos = y_pos + y_step
        if y_pos > 4095:
            break
        dframe = b""
        dframe +=  bytes( str(photodiode_val), 'utf-8')
        dframe +=  bytes( ',', 'utf-8')
        dframe +=  bytes( str( x_pos ), 'utf-8')
        dframe +=  bytes( ',', 'utf-8')
        dframe +=  bytes( str( y_pos ), 'utf-8')
        dframe +=  b'\r\n'
        conn.write(dframe)
        time.sleep_ms(raster_delay)    

    dac2.write(0) 
    dac1.write(0) 
    conn.write(b"raster_end\r\n")
    return 1
def square():
    led = pyb.LED(2)
    i = 1
    conn.write(b"square\r\n")
    while True:
        dac2.write((i) * 4095) 
        dac1.write((i) * 4095) 
        led.toggle()

    i = not i
    time.sleep_ms(10)      
    
    
        
def dither():
    global y_pos, x_pos
    oversample = 40
    dither_delay = 500
    dither_magnitude = 50
    dither_pattern = [ [0,0], [-1,0], [0,1], [1,0], [0,-1] ]
    conn.write(b"dither_start\r\n") 
    #dac2.write(x_pos) 
    #dac1.write(y_pos)  
    time.sleep_us(dither_delay)    
    #get samples at all dithering positions in dither_pattern
    photodiode_readings = []
    for dither_position in dither_pattern: #single dither motion (sample around current position)
        dac2.write(x_pos + dither_position[0]*dither_magnitude) 
        dac1.write(y_pos + dither_position[1]*dither_magnitude)  
        time.sleep_us(dither_delay)    
        photodiode_val = 0
        for sub_sample in range(oversample):
            photodiode_val += photodiode_ADC.read_u16()  # photodiode_ADC.read_core_vref() #photodiode_ADC.read() 
        photodiode_val = photodiode_val/oversample
        photodiode_readings.append(photodiode_val) 
    best = 0
    best_offset = [0, 0]
    for i in range( len(dither_pattern ) ):
        if photodiode_readings[i] > best:
            best = photodiode_readings[i]
            best_offset = dither_pattern[i]
    x_pos += best_offset[0]*dither_magnitude
    y_pos += best_offset[1]*dither_magnitude
    dframe = b"sample,"
    dframe +=  bytes( str(best), 'utf-8')
    dframe +=  bytes( ',', 'utf-8')
    dframe +=  bytes( str( x_pos ), 'utf-8')
    dframe +=  bytes( ',', 'utf-8')
    dframe +=  bytes( str( y_pos ), 'utf-8')
    dframe +=  b'\r\n'
    conn.write(dframe)
    #conn.write(b"dither_end\r\n") 
    return 1


#Always homes z at startup
#home_z()
#MAIN LOOP WHICH NEVER EXITS
while True:
    data_read = conn.readline()
    if data_read:
        data_read = str(data_read, 'utf-8')
        data_read = data_read.rstrip('\r\n')
        recognized = 0
        pyb.LED(2).on()
        pyb.LED(3).on()
        
        if data_read == 'hello':
            recognized = 1
            pyb.LED(1).on()
            conn.write( b"hi there\r\n")  
            
        if data_read == 'raster_scan':
            recognized = 1
            raster_scan()
            
        if data_read == 'dither':
            recognized = 1
            dither() 
            
        if data_read == 'square':
            recognized = 1
            square() 
            
        if data_read == 'maxout': #set analog outputs to max
            recognized = 1
            dac2.write(4095) 
            dac1.write(4095) 
            conn.write( b"max_out_done\r\n")  
        
        if data_read == 'min_out': #set analog outputs to max
            recognized = 1
            dac2.write(0) 
            dac1.write(0) 
            conn.write( b"min_out_done\r\n")  
            
        

        if data_read[0:7] == 'setDAC1':
            value = data_read[7:]
            value = int( value )
            amp_enable.value(1)
            dac1.write( value ) 
            recognized = 1
            conn.write( ("DAC 1 set to " + str(value) + "\r\n").encode('utf-8') ) 
        
        if data_read[0:7] == 'setDAC2':
            value = data_read[7:]
            value = int( value )
            amp_enable.value(1)
            dac2.write( value ) 
            recognized = 1
            conn.write( ("DAC 2 set to " + str(value) + "\r\n").encode('utf-8') ) 
            
        if  data_read == 'amp_off':
            amp_enable.value(0)
            recognized = 1
            conn.write("Amp has been disabled\r\n".encode('utf-8')) 
            
        
        if data_read[0:6] == 'move_z':
            #conn.write("DOOOT\r\n".encode('utf-8')) 
            steps = data_read[6:]
            steps = int( steps )
            #convert signed steps to step, dir
            if steps > 0:
                direction = 1
            else:
                steps = -steps
                direction = 0
            recognized = 1
            move_z(steps, direction)
            conn.write("done moving z\r\n".encode('utf-8')) 
            
        if  data_read == 'read_serial_number':
                recognized = 1
                b = bytes(  str(sn_0.value()) + str(sn_1.value()) +str(sn_2.value()) +str(sn_3.value()) + str(sn_4.value()) + '\r\n', 'utf-8')
                conn.write( b )  
        
        if data_read == 'home_z':
            recognized = 1
            home_z() 
 
        if not recognized:
            response = "command is not recognized: " + data_read + "\r\n"
            conn.write(response.encode('utf-8')) 
            























