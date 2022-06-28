# This script entails a class that covers the various functionalities of the Adafruit IR break beam sensor

# import required libraries
import RPi.GPIO as GPIO
import threading

class IRBreakBeam(object):
    '''
    This class deals with setting up and operating the IR break beam sensor.
    '''

    # instantiation function
    def __init__(self, beam_pin=21):
        self.beam_pin = beam_pin        # store the pin the IR sensor is on
        self.triggered = False          # variable that indicates whether the IR sensor has been triggered
        self.beam_lock = threading.Lock()   # create a lock so that the main thread and the callback function aren't accessing the self.triggered pin at once

        # set up the RPi as BCM numbering
        GPIO.setmode(GPIO.BCM)

        # change the pin to an input
        GPIO.setup(beam_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # have the IR sensor also operate as an interrupt function so that we don't miss any triggers
        GPIO.add_event_detect(beam_pin, GPIO.FALLING, callback = self.beam_triggered)        

    # create a function that checks the beam pin (this checks for a state, not an event)
    def beam_broken(self):
        # function returns True if the beam is broken because a broken beam is set LOW
        return not GPIO.input(self.beam_pin)
        
    # create a callback function that triggers whenever the IR sensor is triggered to be falling
    def beam_triggered(self):
        with self.beam_lock:            # make sure main thread and callback thread aren't racing
            self.triggered = True
        print("The beam has been triggered!")