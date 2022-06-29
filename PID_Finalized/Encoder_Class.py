# This script entails a class that covers the various functions available for the DC motor encoder

# import the required libraries
import RPi.GPIO as GPIO
import threading
import time

class Encoder(object):
    '''
    This class deals with setting up and reading the encoder pins provided to 
    the brushed DC motor. This class allows you to calculate the motor speed
    via a built-in function.
    '''

    # instantiation function (sets up the required pins for the encoer to work)
    def __init__(self, ENCA = 23, ENCB = 24):
        self.ENCA = ENCA                        # import the two encoder pins
        self.ENCB = ENCB
        self.pos_i = 0                          # variable that keeps track of encoder counts/direction
        self.enc_lock = threading.Lock()        # this lock is used to ensure that the pos_i variable isn't accessed by too many things at once

        # set the GPIO mode
        GPIO.setmode(GPIO.BCM)

        # set the encoder pins as inputs
        GPIO.setup(ENCA, GPIO.IN)
        GPIO.setup(ENCB, GPIO.IN)

        # set the encoder as an interrupt by default
        GPIO.add_event_detect(ENCA, GPIO.RISING, callback = self.__readEncoder)

    # Callback function for the encoder (updates the counts/position of the encoder)
    def __readEncoder(self, channel):

        # read ENCB when ENCA has been triggered with a rising signal
        b = GPIO.input(self.ENCB)
        increment = 0

        if (b > 0):
            # if ENCB is HIGH when ENCA is HIGH, motor is moving in negative (CCW) direction
            increment = -1
        else:
            # if ENCB is LOW when ENCA is HIGH, motor is moving in the positive (CW) direction
            increment = 1

        # update the pos_i variable when the interrupt triggers
        # NOTE: a lock has been included so that anything trying to access the pos_i variable
        #       to get the current position is not in conflict when the interrupt pin wants to
        #       access the variable
        with self.enc_lock:
            self.pos_i = self.pos_i + increment

    # Create function to calculate the motor velocity
    def calcMotorVelocity(self):

        # calculate motor velocity (in counts/second)
        time_start = time.perf_counter()            # start time for velocity calculation
        with self.enc_lock:
            pos_start = self.pos_i                  # get start position of the encoder
        time.sleep(0.1)                             # give some time for pos_i variable to update (aliasing may occur without this)
        with self.enc_lock:
            pos_stop = self.pos_i                   # read the position again
        time_stop = time.perf_counter()             # end time for velocity calculation
        deltaT = time_stop - time_start             # calculate the elapsed time
        velocity = (pos_stop - pos_start)/deltaT    # calculate the velocity

        # change the velocity into RPM (116.16 is the product of the gear ratio - 9.68 - and the encoder counts per rev - 12 - and 60 is from sec to min)
        velocity = velocity/116.16*60.0

        return velocity