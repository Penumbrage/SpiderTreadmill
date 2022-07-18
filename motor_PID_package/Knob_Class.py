'''
 * @file    Knob_Class.py
 * @author  William Wang
 * @brief   This script entails the class that covers 
            the various functions which control the rotary 
            encoder used to manually control the speed of 
            the DC motor
'''

# import required libraries
import RPi.GPIO as GPIO
from math import pi

class Knob(object):
    '''
    DESCRIPTION: This class deals with setting up the rotary encoder, which is used
    to operate the speed of the DC motor manually. Note that in order 
    to ensure continuity between the speed dictated by this encoder and the
    speed dictated by the user inputs from the terminal, it is necessary to
    pass in a UserInput object.
    ARGS: user_input (object from User_Input_Class.py), lcd (LCD pin on encoder),
    clk (clock pin on encoder), dt (direction pin on encoder), sw (switch pin on encoder)
    '''

    def __init__(self, user_input, lcd, clk=18, dt=25, sw=20):
        # instantiation function for the rotary encoder
        
        self.user_input = user_input        # receive UserInput object (access the speed_des variable)
        self.lcd = lcd                      # receive LCD object (to be able to print to the LCD)
        self.clk = clk                      # pin for the clock
        self.dt = dt                        # pin for the direction
        self.sw = sw                        # pin for the push button switch
        self.step_size = 0.1                # setup default step size for the encoder (0.1 m/s)
        self.button_pressed = False         # default state for the button is false

        # set the GPIO mode
        GPIO.setmode(GPIO.BCM)

        # set the clk, dt, and sw pins as inputs
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #set up the interrupts for each pin
        GPIO.add_event_detect(clk, GPIO.FALLING, callback=self.__clkClicked, bouncetime=100)
        GPIO.add_event_detect(dt, GPIO.FALLING, callback=self.__dtClicked, bouncetime=100)
        GPIO.add_event_detect(sw, GPIO.FALLING, callback=self.__swClicked, bouncetime=300)

    def __clkClicked(self, channel):
        '''
        DESCRIPTION: Callback function to be called whenever the clk pin is triggered with a falling signal.
        ARGS: channel (pin number for the clk pin)
        RETURN: NONE
        '''

        # obtain the current states of both clk and dt
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)

        # update the desired speed if we meet the following states
        if clkState == 0 and dtState == 1:
            with self.user_input.speed_des_lock:         # access with lock to prevent racing with main loop
                if ((self.user_input.speed_des_mps - self.step_size) < -1.5001):    # set lower limit/warning to lcd
                    msg = "Exceeding lower\nlim of -1.5 m/s"
                    self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
                else:
                    self.user_input.speed_des_mps = self.user_input.speed_des_mps - self.step_size      # speed in m/s
                    self.user_input.speed_des_RPM = self.user_input.speed_des_mps*(60/pi)/(2/39.3701)   # convert to RPM

    def __dtClicked(self, channel):
        '''
        DESCRIPTION: Callback function to be called when the dt pin is triggered with a falling signal
        ARGS: channel (pin number for the dt pin)
        RETURN: NONE
        '''

        # check the states of the clk and dt pins
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)

        # update the desired speed if we meet the following states for the pins
        if clkState == 1 and dtState == 0:
            with self.user_input.speed_des_lock:        # access with lock to prevent racing on speed_des variables
                if ((self.user_input.speed_des_mps + self.step_size) > 1.5001):       # set upper limit/warning to lcd
                    msg = "Exceeding upper\nlim of 1.5 m/s"
                    self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
                else:
                    self.user_input.speed_des_mps = self.user_input.speed_des_mps + self.step_size              # speed in m/s
                    self.user_input.speed_des_RPM = self.user_input.speed_des_mps*(60/pi)/(2/39.3701)   # convert to RPM

    def __swClicked(self, channel):
        '''
        DESCRIPTION: Callback function that is called whenever the switch is pressed (used to update the increment size)
        ARGS: channel (pin number for the sw pin)
        RETURN: NONE
        '''

        # when the button is pressed change the state of the button variable
        self.button_pressed = not self.button_pressed

        # if the button state is True, then the step size for speed_des is 0.01 m/s
        if self.button_pressed:
            self.step_size = 0.01
            msg = "Curr step size:\n0.01 m/s"
            self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
        # if button state is False, then the step size for speed_des is 0.1 m/s
        else:
            self.step_size = 0.1
            msg = "Curr step size:\n0.1 m/s"
            self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
            