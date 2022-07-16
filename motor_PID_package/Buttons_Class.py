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
    DESCRIPTION: This class is based of the base button class and contains various
    functions that deal with starting and stopping the main.py script via a background
    service

    ARGS: button_pin (the pin that the button is attached to)
    '''

    def __init__(self, button_pin):
        # initializaition function for the StartStopButton class

        # obtain original init function
        super().__init__(button_pin)

        self.program_started = False                # variable to store start/stop state of the program
        self.start_stop_lock = threading.Lock()     # lock for the program_started variable (because the main loop needa access to this variable)

        # setup an interrupt on the desired pin 
        GPIO.add_event_detect(button_pin, GPIO.RISING, callback=self.__start_stop_function, bouncetime=100)

    def __start_stop_function(self):
        '''
        DESCRIPTION: Function that changes the state of the program_started variable, which is used
        to control whether or not the main function should be executed

        ARGS: NONE

        RETURN: NONE
        '''

        # switch the program_started variable's state when the button is pressed
        with self.start_stop_lock:
            self.program_started = not self.program_started
