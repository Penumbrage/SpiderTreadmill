'''
 * @file    Buttons_Class.py
 * @author  William Wang
 * @brief   This script contains various classes
            for different buttons used with the
            treadmill.
'''

# import the required libraries
import RPi.GPIO as GPIO
import threading
from math import pi

class Button(object):
    '''
    DESCRIPTION: This class is the base class that sets up the GPIO pins for any buttons.
    Note that this class does not contain any particular functions that will be evaluated
    when the buttons are pressed except for printing the button status

    ARGS: button_pin (pin that the button is attached to)
    '''

    def __init__(self, button_pin):
        # instantiation function for the basic button
        
        self.button_pin = button_pin        # receive the pin for the button

        # set the GPIO mode
        GPIO.setmode(GPIO.BCM)

        # set the button pin as input which is pulled down
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def button_pressed(self):
        '''
        DESCRIPTION: Function that lets the user know if the button has been pressed via
        terminal

        ARGS: NONE

        RETURN: NONE
        '''

        # Obtain the state of the button
        button_state = GPIO.input(self.button_pin)

        # evaluate the state of the button and print it to the terminal
        if button_state == True:
            print("The button has been pressed!")
        elif button_state == False:
            print("The button has been released!")

class StartStopButton(Button):
    '''
    DESCRIPTION: This class is based off the base button class and contains various
    functions that deal with starting and stopping the main.py script via a background
    service

    ARGS: button_pin (the pin that the button is attached to)
    '''

    def __init__(self, button_pin):
        # initializaition function for the StartStopButton class

        # obtain original init function
        super().__init__(button_pin)

        self.program_started = False                # variable to store start/stop state of the program
        self.start_stop_lock = threading.Lock()     # lock for the program_started variable (because the main loop needs access to this variable)

        # setup an interrupt on the desired pin 
        GPIO.add_event_detect(button_pin, GPIO.RISING, callback=self.__start_stop_function, bouncetime=100)

    def __start_stop_function(self, channel):
        '''
        DESCRIPTION: Function that changes the state of the program_started variable, which is used
        to control whether or not the main function should be executed

        ARGS: channel (the pin number the button is attached to)

        RETURN: NONE
        '''

        # switch the program_started variable's state when the button is pressed
        with self.start_stop_lock:
            self.program_started = not self.program_started

class PresetSpeedButton(Button):
    '''
    DESCRIPTION: This class is based of the base Button class and is used to define various
    functions that are used with the PresetSpeedButton. This button is used save the current 
    displayed desired speed as the preset speed for any test trials

    ARGS: button_pin (pin number that the button is connected to), user_input (User_Input_Class object
    which needs to be accessed in order to update the desired speed), lcd (lcd object from the LCD_Class
    used to allow this button to print messages to the LCD)
    '''
    def __init__(self, button_pin, user_input, lcd):
        # initializaition function for the StartStopButton class

        # obtain original init function
        super().__init__(button_pin)

        self.user_input = user_input        # store the user_input object to update speed_des
        self.lcd = lcd                      # store the lcd object to update the lcd

        # setup an interrupt on the desired pin 
        GPIO.add_event_detect(button_pin, GPIO.RISING, callback=self.__set_preset_speed, bouncetime=100)

    def __set_preset_speed(self, channel):
        '''
        DESCRIPTION: Callback function that saves the current speed_des_mps as the preset speed for any 
        future experiments. This function also ramps the speed back down to zero.

        ARGS: channel (the channel number the button is attached to)

        RETURN: NONE
        '''

        with self.user_input.speed_des_lock:
            # set the preset speed (for both m/s and RPM)
            self.user_input.preset_speed_mps = self.user_input.speed_des_mps
            self.user_input.preset_speed_RPM = self.user_input.preset_speed_mps*(60/pi)/(2/39.3701)

        # send the motor back to zero velocity (in preparation for any trials with the preset speed)
        self.user_input.sendSpeedToZero()

        # send message to LCD and terminal notifying of preset speed update
        msg="Preset speed of:\n%.2f m/s" % self.user_input.preset_speed_mps
        print(msg)
        self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
        
class ExperimentButton(Button):
    '''
    DESCRIPTION: This class is based off the base button class and contains various
    functions that allow the user to start an experiment (which the starts data collection
    and triggers an external high speed camera) and then stop the experiment when the user
    desires to.

    ARGS: button_pin (the pin that the button is attached to), camera_pin (the pin the camera will
    be attached to), data_collector (object from the Data_Collection_Class), user_input (object
    of the User_Input_Class), lcd (object of the LCD_Class)
    '''

    def __init__(self, button_pin, camera_pin, data_collector, user_input, lcd):
        # initializaition function for the StartStopButton class

        # obtain original init function
        super().__init__(button_pin)

        self.camera_pin = camera_pin            # pin that will trigger the camera to start when the button is pressed
        self.trial_started = False              # boolean flag that indicates whether a trial is started or not
        self.data_collector = data_collector    # allow access to the data_collector object to create csv files
        self.user_input = user_input            # allow access to the user_input object to allow the button to change speeds
        self.lcd = lcd                          # allow access to the lcd object to print important messages to the LCD

        # set up camera pin to be default low (safer)
        GPIO.setup(camera_pin, GPIO.OUT, initial=GPIO.LOW)

        # set up the button as an interrupt
        GPIO.add_event_detect(button_pin, GPIO.RISING, callback=self.__start_stop_experiment, bouncetime=100)

    def __start_stop_experiment(self, channel):
        '''
        DESCRIPTION: Callback function that starts/stops an experiment (triggers a boolean flag that indicates
        the trial has started or stopped, triggers the camera, and creates a new file to save data to)

        ARGS: channel (the pin number the button is attached to)

        RETURN: NONE
        '''

        # First trigger a change in the experiment boolean flag
        self.trial_started = not self.trial_started

        # if the experiment has started, perform the following
        if self.trial_started == True:
            # trigger the camera by setting the GPIO to HIGH
            GPIO.output(self.camera_pin, GPIO.HIGH)

            # create a new file to store data
            self.data_collector.create_new_file()

            # set the start time for data collected
            self.data_collector.set_start_time()

            # update the desired speeds with the preset speeds
            with self.user_input.speed_des_lock:
                self.user_input.speed_des_mps = self.user_input.preset_speed_mps
                self.user_input.speed_des_RPM = self.user_input.speed_des_mps*(60/pi)/(2/39.3701)
                self.user_input.user_changed_velocity = True            # flag used to indicate speed should be ramped

            # print important messages to the terminal and the LCD
            print("\nExperiment started")
            print("To spd: %.2f" % self.user_input.preset_speed_mps)
            msg = "Trial started\nTo spd: %.2f" % self.user_input.preset_speed_mps
            self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
        
        # if the user has stopped the experiment, execute the following
        elif self.trial_started == False:
            # reset the camera pin
            GPIO.output(self.camera_pin, GPIO.LOW)

            # NOTE: the file automatically closes after every line is saved

            # send the speed back to zero
            self.user_input.sendSpeedToZero()

            # print important messages to the terminal and LCD
            print("\nExperiment stopped")
            msg = "Trial stopped"
            self.lcd.sendtoLCDThread(target="knob", msg=msg, duration=2, clr_before=True, clr_after=True)
