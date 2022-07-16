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
import time

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
        self.button_start_time = 0          # start times to figure out how long the button has been pressed     

        # set the GPIO mode
        GPIO.setmode(GPIO.BCM)

        # set the clk, dt, and sw pins as inputs
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #set up the interrupts for each pin
        GPIO.add_event_detect(clk, GPIO.FALLING, callback=self.__clkClicked, bouncetime=100)
        GPIO.add_event_detect(dt, GPIO.FALLING, callback=self.__dtClicked, bouncetime=100)
        GPIO.add_event_detect(sw, GPIO.FALLING, callback=self.__swClicked, bouncetime=500)

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
        DESCRIPTION: Callback function that is called whenever the switch is pressed (used to update the increment size or preset speeds)

        ARGS: channel (pin number for the sw pin)

        RETURN: NONE
        '''
        
        # start the timer to see how long the button has been held
        self.button_start_time = time.perf_counter()

        # check the button state
        button_state = GPIO.input(self.sw)

        while button_state == False:
            # check how long the button has been held
            time_held = time.perf_counter() - self.button_start_time

            # if the time is greater than 5 seconds, then set the preset speed and send the current motor speed back to zero
            if (time_held >= 5):
                with self.user_input.speed_des_lock:
                    # set the preset speed (for both m/s and RPM)
                    self.user_input.preset_speed_mps = self.user_input.speed_des_mps
                    self.user_input.preset_speed_RPM = self.user_input.preset_speed_mps*(60/pi)/(2/39.3701)

                    # send the motor back to zero velocity (in preparation for any trials with the preset speed)
                    self.user_input.speed_des_mps = 0
                    self.user_input.speed_des_RPM = 0
                    self.user_input.user_changed_velocity = True        # allows the system to ramp the speed down

                # send message to LCD and terminal notifying of preset speed update
                msg="Preset speed of:\n%.2f m/s" % self.user_input.preset_speed_mps
                print(msg)
                self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)

                # break form the while loop to prevent any further updates to the preset speed
                break

            # update the button_state
            button_state = GPIO.input(self.sw)

            print(time_held)

        else:
            # NOTE: above, button_state will remain true as long as we hold it, if the time_held surpasses 5 seconds
            #       we update the preset speed. However, if the user lets go before 5 seconds is up, then the else 
            #       statement below is executed where the increments are updated instead

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
