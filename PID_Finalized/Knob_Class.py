# This script entails the class that covers the various functions which control
# the rotary encoder used to manually control the speed of the DC motor

# import required libraries
import RPi.GPIO as GPIO
import threading
from math import pi

class Knob(object):
    '''
    This class deals with setting up the rotary encoder, which is used
    to operate the speed of the DC motor manually. Note that in order 
    to ensure continuity between the speed dictated by this encoder and the
    speed dictated by the user inputs from the terminal, it is necessary to
    pass in a UserInput object.
    '''

    # instantiation function for the rotary encoder
    def __init__(self, user_input, clk=18, dt=25, sw=20):
        self.user_input = user_input        # receive UserInput object (access the speed_des variable)
        self.clk = clk                      # pin for the clock 
        self.dt = dt                        # pin for the direction
        self.sw = sw                        # pin for the push button switch
        self.step_size = 0.1                # setup default step size for the encoder (0.1 m/s)
        self.button_pressed = False         # default state for the button is false
        self.knob_lock = threading.Lock()   # lock to protect the user_input.speed des variable

        # set the GPIO mode
        GPIO.setmode(GPIO.BCM)

        # set the clk, dt, and sw pins as inputs
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #set up the interrupts for each pin
        GPIO.add_event_detect(clk, GPIO.FALLING, callback=self.__clkClicked, bouncetime=200)
        GPIO.add_event_detect(dt, GPIO.FALLING, callback=self.__dtClicked, bouncetime=200)
        GPIO.add_event_detect(sw, GPIO.FALLING, callback=self.__swClicked, bouncetime=300)

    # Callback function to be called whenever the clk pin is triggered with a falling signal
    def __clkClicked(self, channel):

        # obtain the current states of both clk and dt
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)

        # update the desired speed if we meet the following states
        if clkState == 0 and dtState == 1:
            with self.knob_lock:
                self.user_input.speed_des_mps = self.user_input.speed_des_mps - self.step_size      # speed in m/s
                self.user_input.speed_des_RPM = self.user_input.speed_des_mps*(60/pi)/(2/39.3701)   # convert to RPM

    # Callback function to be called when the dt pin is triggered with a falling signal
    def __dtClicked(self, channel):

        # check the states of the clk and dt pins
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)

        # update the desired speed if we meet the following states for the pins
        if clkState == 1 and dtState == 0:
            with self.knob_lock:
                self.user_input.speed_des_mps = self.user_input.speed_des_mps + self.step_size              # speed in m/s
                self.user_input.speed_des_RPM = self.user_input.speed_des_mps*(60/pi)/(2/39.3701)   # convert to RPM

    # Callback function that is called whenever the switch is pressed (used to update the increment size)
    def __swClicked(self, channel):

        # when the button is pressed change the state of the button variable
        self.button_pressed = not self.button_pressed

        # if the button state is True, then the step size for speed_des is 0.01 m/s
        if self.button_pressed:
            self.step_size = 0.01
        # if button state is False, then the step size for speed_des is 0.1 m/s
        else:
            self.step_size = 0.1

            