# This script entails a class that covers the various functionalities of the Adafruit IR break beam sensor

# import required libraries
import RPi.GPIO as GPIO

class IRBreakBeam(object):
    '''
    This class deals with setting up and operating the IR break beam sensor.
    '''

    # instantiation function
    def __init__(self, beam_pin=21):
        self.beam_pin = beam_pin        # store the pin the IR sensor is on

        # set up the RPi as BCM numbering
        GPIO.setmode(GPIO.BCM)

        # change the pin to an input
        GPIO.setup(beam_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # create a function that checks the beam pin
    def beam_broken(self):
        # function returns True if the beam is broken because a broken beam is set LOW
        return not GPIO.input(self.beam_pin)
