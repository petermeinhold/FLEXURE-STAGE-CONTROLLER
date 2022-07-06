from pyb import Timer, Pin, LED, DAC
import micropython
import math
import machine
import time
import pyb
import array

conn = pyb.USB_VCP()
conn.setinterrupt(-1)


class Fiber_actuator_controller(object):

    def __init__(self):
        self.mode = 0
        self.sig_square_on = 0
        self.sig_x_on = 0
        self.sig_y_on = 0
        self.frequency = 0
        self.amplitude = 0


        self.dither_frequency = 0
        self.dither_amplitude = 0
        self.dither_state = 0 #counts through steps of dithering process
        self.gradient_ascent_amplitude = 0
        self.gradient_ascent_on = False
        self.gradient_ascent_threashold = 0
        self.leds = [0,0,0,1]
        self.ni_control_adc = pyb.ADC(pyb.Pin.board.X11)  
        self.adc_reading_up = 0 
        self.adc_reading_right = 0 
        self.adc_reading_down = 0 
        self.adc_reading_left = 0 

        self.x_position = 10
        self.y_position = 10
        self.X_dac = DAC(1, bits=12) #pin X5
        self.Y_dac =DAC(2, bits=12)  #pin X6
        self.drive_enable_output = Pin('X8', Pin.OUT_PP)
        self.drive_enable_output.low()
        self.amp_enable_output = Pin('X4', Pin.OUT_PP)
        self.amp_enable_output.low()
        self.x_dac = DAC(1, bits=12)
        self.x_dac.write(0)
        self.y_dac = DAC(1, bits=12)
        self.y_dac.write(0)

        self.led1 = pyb.LED(1) 
        self.led2 = pyb.LED(2) 
        self.led3 = pyb.LED(3) 
        self.led4 = pyb.LED(4)  
        
        self.sn1 = Pin('X18', Pin.IN)#Pin.PULL_UP
        self.sn2 = Pin('X19', Pin.IN)
        self.sn3 = Pin('X20', Pin.IN)
        self.sn4 = Pin('X21', Pin.IN)
        
        self.limit_switch_pin = Pin('X12', Pin.IN)
        self.dir_pin = Pin('X9', Pin.OUT_PP)
        self.step_pin = Pin('X10', Pin.OUT_PP)
        self.step_delay = 0
        self.n_steps = 0
        
        self.square_wave_state = 0
        self.sine_buffer = None
        self.sine_index = 0
        self.sine_n = 0
        self.timer = None
        #tim = pyb.Timer(3)
        #tim.init(freq=frequency)
        #tim.callback(self.cb)
    def make_sine_wave(self, n):
        self.sine_n = n
        self.sine_buffer = array.array('i',[0]*n)
        for i in range(n):
            self.sine_buffer[i] = 128 + int(127 * math.sin(2 * math.pi * i / n))
        return self.sine_buffer
        
        
    def drv_enable(self):
        self.drive_enable_output.high()
    def drv_disable(self):
        self.drive_enable_output.low()
    def amp_enable(self):
        self.amp_enable_output.high()
    def amp_disable(self):
        self.amp_enable_output.low()
        
    def DEFAULT_CB(self, tim): #not currently used
        self.led1.toggle()
  
    def sine_callback(self, tim ):
        a = 6
        
        
    def SQUARE_BOTH_CB(self, tim):
        self.led3.toggle()
        self.led4.toggle()
        if self.square_wave_state:
            self.X_dac.write( self.amplitude )    
            self.Y_dac.write( self.amplitude ) 
        else:
            self.X_dac.write( 0 )    
            self.Y_dac.write( 0 )
        self.square_wave_state = not self.square_wave_state  
    def sine_both_cb(self, tim):
        self.X_dac.write( self.sine_buffer[self.sine_index] )   
        self.Y_dac.write( self.sine_buffer[self.sine_index] )   
        self.sine_index += 1
        if self.sine_index == self.sine_n - 1:
            self.sine_index = 0
            self.led3.toggle()
            self.led4.toggle()
            
            
        
    def SQUARE_X_CB(self, tim):
        self.led3.toggle()
        #self.led4.toggle()
        if self.square_wave_state:
            self.X_dac.write( self.amplitude)    
            self.Y_dac.write( 0 ) 
        else:
            self.X_dac.write( 0 )    
            #self.Y_dac.write( 0 )
        self.square_wave_state = not self.square_wave_state  
        
    def SQUARE_Y_CB(self, tim):
        #self.led3.toggle()
        self.led4.toggle()
        if self.square_wave_state:
            self.X_dac.write( 0 )    
            self.Y_dac.write( self.amplitude) 
        else:
            #self.X_dac.write( 0 )    
            self.Y_dac.write( 0 )
        self.square_wave_state = not self.square_wave_state  
         
        #if self.mode == 1:
        #    #signal generator mode is on
        #    if self.sig_square_on:
            
    def dither_cb(self, tim):
    
        #read ni_in at up right left and down positions
        if self.dither_state == 0: #dither up (+y)
            self.leds[0] = 0
            self.leds[1] = 0
            self.leds[2] = 0
            self.leds[3] = 1
            self.x_dac.write(self.x_position)
            self.y_dac.write(self.y_position + self.dither_amplitude)
            self.adc_reading_up = self.ni_control_adc.read()
        if self.dither_state == 1: #dither right (+x)
            self.leds[0] = 0
            self.leds[1] = 0
            self.leds[2] = 1
            self.leds[3] = 0
            self.x_dac.write(0)
            self.x_dac.write(self.x_position + self.dither_amplitude)
            self.y_dac.write(self.dither_amplitude)
            self.adc_reading_right = self.ni_control_adc.read()
        if self.dither_state == 2: #dither down (-y)
            self.leds[0] = 0
            self.leds[1] = 1
            self.leds[2] = 0
            self.leds[3] = 0
            self.x_dac.write(self.x_position)
            self.y_dac.write(self.y_position - self.dither_amplitude)
            self.adc_reading_down = self.ni_control_adc.read()
        if self.dither_state == 3: #dither left (-x)
            self.leds[0] = 1
            self.leds[1] = 0
            self.leds[2] = 0
            self.leds[3] = 0
            self.x_dac.write(self.x_position - self.dither_amplitude)
            self.y_dac.write(self.y_position)
            self.adc_reading_left = self.ni_control_adc.read()
            
        #gradient ascent
        if self.adc_reading_left - self.adc_reading_right > self.gradient_ascent_threashold:
            self.x_position += self.gradient_ascent_amplitude
        if self.adc_reading_left - self.adc_reading_right < -self.gradient_ascent_threashold:
            self.x_position -= self.gradient_ascent_amplitude
        if self.adc_reading_up - self.adc_reading_down > self.gradient_ascent_threashold:
            self.y_position += self.gradient_ascent_amplitude
        if self.adc_reading_up - self.adc_reading_down < -self.gradient_ascent_threashold:
            self.y_position -= self.gradient_ascent_amplitude
        
        #keep position in bounds
        if self.x_position > 4095:
            self.x_position = 4095
        if self.x_position < 0:
            self.x_position = 0
        if self.y_position > 4095:
            self.y_position = 4095
        if self.y_position < 0:
            self.y_position = 0
        
            
        if self.leds[0]:
            self.led1.on()
        else:
            self.led1.off()
        if self.leds[1]:
            self.led2.on()
        else:
            self.led2.off()
        if self.leds[2]:
            self.led3.on()
        else:
            self.led3.off()
        if self.leds[3]:
            self.led4.on()
        else:
            self.led4.off()
            
        self.dither_state = (self.dither_state + 1) % 4
        
        if self.gradient_ascent_on:
            a = 5

    def home_z(self):  
        self.dir_pin.value( 0 )         
        for step in range(500):
            time.sleep_ms( 10 )
            self.step_pin.low()        
            time.sleep_ms( 10 )  
            self.step_pin.low()    
            self.led4.toggle()
            if self.limit_switch_pin.value():
                conn.write( 'home complete\r\n'.encode() )  
                return 1
        conn.write( 'did not hit limit switch\r\n'.encode() )  
        return 0
            
    def move_z(self):  
        direction = 0
        if self.n_steps < 0:
            self.n_steps = -self.n_steps
            direction = 1
        self.dir_pin.value( direction )         
        for step in range(self.n_steps):
            time.sleep_ms( self.step_delay ) 
            self.step_pin.low()        
            time.sleep_ms( self.step_delay ) 
            self.step_pin.low()     
            self.led4.toggle()
            if self.limit_switch_pin.value():
                conn.write( 'limit switch hit\r\n'.encode() )  
                return 0
        conn.write( 'move complete\r\n'.encode() )  
        return 1
    
    def new_timer(self):
        if self.timer is not None:
            self.timer.deinit()
        else:
            self.timer = pyb.Timer(4)    
    def stop(self):
        self.drive_enable_output.low()
        self.drive_enable_output.low()
        if self.timer is not None:
            self.timer.deinit()
            self.timer = None 
        self.X_dac.write(0)
        self.Y_dac.write(0)
        
    def get_serial_number(self):
        self.led3.toggle()
        self.led4.toggle()
        self.serial_number = str(self.sn1.value())+str(self.sn2.value())+str(self.sn3.value())+str(self.sn4.value())
        conn.write( ('serial_number,' + self.serial_number+'\r\n').encode() )


    def send_state(self):
        #create frame
        dframe=b'params'
        for i in range(10):
                adcval = my_controller.adc_vals[i] * my_controller.ADC_gain
                dframe = dframe + ',' + bytes(str(adcval),'utf-8')
        dframe=dframe +',' + str( my_controller.dac_current[0]/my_controller.DAC_gain )
        dframe=dframe +',' + str( my_controller.dac_current[1]/my_controller.DAC_gain )
        dframe = dframe +',' + str( my_controller.pre_good )
        dframe = dframe +',' + str( my_controller.pwr_good )
        dframe = dframe +',' + str( my_controller.tec_t_good )
        dframe = dframe +',' + str( my_controller.pre_ext_en )
        dframe = dframe +',' + str( my_controller.pwr_ext_en )
        dframe=dframe +',' + b'end\n'
        conn.write(dframe)
               
                
micropython.alloc_emergency_exception_buf(100)        
my_controller = Fiber_actuator_controller()
my_controller.led1.toggle()


dac1req='0000'
dac2req='0000'

while True:
    data_read = conn.readline()
    if data_read:
            my_controller.stop()   
            my_controller.led1.toggle()
            my_controller.led2.toggle()
            my_controller.led3.toggle()
            my_controller.led4.toggle()
            datalist = str(data_read,'utf-8').split(',')
            datalist[-1] = datalist[-1].rstrip('\r\n')
            understood = 0
            
            
            if datalist[0]=='amp_enable':
                my_controller.amp_enable()
                conn.write( 'amp enabled\r\n'.encode() )  
                understood = 1
            if datalist[0]=='amp_disable':
                my_controller.amp_disable()
                conn.write( 'amp disabled\r\n'.encode() )  
                understood = 1
            if datalist[0]=='drv_enable':
                my_controller.drv_enable()
                conn.write( 'drive enabled\r\n'.encode() )  
                understood = 1
            if datalist[0]=='drv_disable':
                my_controller.drv_disable()
                conn.write( 'drive disabled\r\n'.encode() )  
                understood = 1
            
            if datalist[0]=='get_serial_number':
                my_controller.get_serial_number()
                understood = 1
                
            if datalist[0]=='home_z':
                understood = 1
                my_controller.home_z()
                conn.write( 'home z completed\r\n'.encode() )  
                
            if datalist[0]=='move_z':
                understood = 1
                my_controller.n_steps = int( float(datalist[1] ))
                my_controller.step_delay = float(datalist[2])
                my_controller.move_z()
                conn.write( 'z move completed\r\n'.encode() )  
                
            
            if datalist[0]=='signal_generator':
                #square, x, y, frequency, amplitude
                understood = 1
                my_controller.sig_square_on = int( datalist[1] )
                my_controller.sig_x_on = int( datalist[2] )
                my_controller.sig_y_on = int( datalist[3] )
                my_controller.frequency = float( datalist[4] )
                my_controller.amplitude = int( float( datalist[5] ) * 4095)
    
                my_controller.led3.off()
                my_controller.led4.off()
                my_controller.square_wave_state = 0
                my_controller.X_dac.write( 0 )    
                my_controller.Y_dac.write( 0 )  
                if my_controller.sig_square_on: 
                    my_controller.new_timer()
                    my_controller.timer.init( freq = my_controller.frequency*2 )
                    if my_controller.sig_x_on and my_controller.sig_y_on:
                        my_controller.timer.callback( my_controller.SQUARE_BOTH_CB )
                    else:
                        if my_controller.sig_x_on:
                            my_controller.timer.callback( my_controller.SQUARE_X_CB )
                        if my_controller.sig_y_on:
                            my_controller.timer.callback( my_controller.SQUARE_Y_CB )
                else:
                    n_steps_in_sine_wave = 10000 // my_controller.frequency
                    if n_steps_in_sine_wave > 100:
                        n_steps_in_sine_wave = 100
                    conn.write( ('sine n_steps = ' + str(n_steps_in_sine_wave)).encode()  )
                    my_controller.make_sine_wave(int(n_steps_in_sine_wave))
                    my_controller.new_timer()
                    
                    
                    if my_controller.sig_x_on and my_controller.sig_y_on:
                            
                            my_controller.timer.init( freq = my_controller.frequency*n_steps_in_sine_wave )
                            my_controller.timer.callback( my_controller.sine_both_cb )
                        
                                    
                conn.write( (str(my_controller.frequency) + ',' + str(my_controller.amplitude) + '  signal_generator starting\r\n').encode() )  
                
      
        
            if datalist[0] == 'dither_start':
                #dither freq, dither amp, gradient ascent on/off, ascent step size
                understood = 1
                my_controller.frequency = float( datalist[1] )
                my_controller.amplitude = int( datalist[2] * 4095 )
                
                my_controller.gradient_ascent_on =  datalist[3] == '1'
                my_controller.gradient_ascent_amplitude = int( datalist[3] )
                my_controller.gradient_ascent_threashold = int( datalist[3] )
                
                conn.write( 'dither starting\r\n'.encode() )  
                my_controller.new_timer()
                my_controller.timer.init( freq = my_controller.frequency*4 )
                my_controller.timer.callback( my_controller.dither_cb )
                
                        
            if datalist[0] == 'hello':
                understood = 1
                conn.write( 'Hi there\r\n'.encode() ) 
            if datalist[0] == 'stop':
                my_controller.stop()
                understood = 1
                conn.write( 'stopped\r\n'.encode() ) 
            
            if datalist[0] == 'read_params':
                understood = 1
                #conn.write( 'Read Parameters\r\n'.encode() )  
                my_controller.send_state()


            if not understood:
                conn.write( 'Did not understand: '.encode() )
                conn.write( data_read )


    """
    #create frame
    dframe=b'start'
    for i in range(10):
            adcval = my_controller.adc_vals[i] * my_controller.ADC_gain
            dframe = dframe + ',' + bytes(str(adcval),'utf-8')

    dframe=dframe +',' + str( my_controller.dac_current[0]/my_controller.DAC_gain )
    dframe=dframe +',' + str( my_controller.dac_current[1]/my_controller.DAC_gain )
    
    dframe = dframe +',' + str( my_controller.pre_good )
    dframe = dframe +',' + str( my_controller.pwr_good )
    dframe = dframe +',' + str( my_controller.tec_t_good )
    dframe = dframe +',' + str( my_controller.pre_ext_en )
    dframe = dframe +',' + str( my_controller.pwr_ext_en )
    

    dframe=dframe +',' + b'end\n'
    conn.write(dframe)
    time.sleep_ms(500)      # sleep for 500 milliseconds
    """































    