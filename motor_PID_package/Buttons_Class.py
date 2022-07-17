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

        ARGS: NONE

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
    which needs to be accessed in order to update the desired speed)
    '''
    def __init__(self, button_pin, user_input):
        # initializaition function for the StartStopButton class

        # obtain original init function
        super().__init__(button_pin)

        self.user_input = user_input        # store the user_input object to update speed_des

        # setup an interrupt on the desired pin 
        GPIO.add_event_detect(button_pin, GPIO.RISING, callback=self.__set_preset_speed, bouncetime=100)

    def __set_preset_speed(self):
        '''
        DESCRIPTION: Callback function that saves the current speed_des_mps as the preset speed for any 
        future experiments. This function also ramps the speed back down to zero.

        ARGS: NONE

        RETURN: NONE
        '''

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
        