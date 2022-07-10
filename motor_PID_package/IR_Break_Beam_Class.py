'''
 * @file    IR_Break_Beam_Class.py
 * @author  William Wang
 * @brief   This script entails a class that covers the 
            various functionalities of the Adafruit IR
            break beam sensor
'''

# import required libraries
import RPi.GPIO as GPIO
import threading

class IRBreakBeam(object):
    '''
    DESCRIPTION: This class deals with setting up and operating the IR break beam sensor.
    It contains various functions that are/can be called if IR sensor is tripped or broken.

    ARGS: beam_pin (the pin the IR sensor is connected to on the RPi)
    '''

    def __init__(self, beam_pin=21):
        # Instantiation function for the IR Bream Beam object

        self.beam_pin = beam_pin        # store the pin the IR sensor is on
        self.triggered = False          # variable that indicates whether the IR sensor has been triggered
        self.beam_lock = threading.Lock()   # create a lock so that the main thread and the callback function aren't accessing the self.triggered pin at once

        # set up the RPi as BCM numbering
        GPIO.setmode(GPIO.BCM)

        # change the pin to an input
        GPIO.setup(beam_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # have the IR sensor also operate as an interrupt function so that we don't miss any triggers
        GPIO.add_event_detect(beam_pin, GPIO.FALLING, callback = self.__beam_triggered, bouncetime = 100)        

    def beam_broken(self):
        '''
        DESCRIPTION: Function that checks the beam pin (this checks for a state, not an event)
        to see if the beam is broken (i.e. open loop)
        
        ARGS: NONE

        RETURN: boolean value (T if broken, F is not broken)
        '''
        # function returns True if the beam is broken because a broken beam is set LOW
        return not GPIO.input(self.beam_pin)

    def __beam_triggered(self, channel):
        '''
        DESCRIPTION: Callback function that triggers whenever the IR sensor trips with a falling signal

        ARGS: channel (channel number for the IR sensor)

        RETURN: NONE
        '''
        with self.beam_lock:            # make sure main thread and callback thread aren't racing
            self.triggered = True
        print("The beam has been triggered!")
