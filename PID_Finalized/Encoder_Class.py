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

        # set the encoder as an interrupt by default (for both pins)
        GPIO.add_event_detect(ENCA, GPIO.BOTH, callback = self.__readEncoderA)
        GPIO.add_event_detect(ENCB, GPIO.BOTH, callback = self.__readEncoderB)

    # Callback function for the encoder (updates the counts/position of the encoder)
    # NOTE: this callback function is called whenever ENCA is triggered
    def __readEncoderA(self, channel):

        # read ENCB when ENCA has been triggered with a rising or falling signal
        a = GPIO.input(self.ENCA)
        b = GPIO.input(self.ENCB)

        increment = 0

        if (b > 0 and a > 0):
            # if ENCB is HIGH when ENCA is HIGH, motor is moving in the negative (CCW) direction
            increment = -1
        elif (b == 0 and a == 0):
            # if ENCB is LOW when ENCA is LOW, motor is moving in the negative (CCW) direction
            increment = -1
        else:
            # if ENCB has a different state compared to ENCA when measured, motor is moving in the
            # positive (CW) direction
            increment = 1

        # update the pos_i variable when the interrupt triggers
        # NOTE: a lock has been included so that anything trying to access the pos_i variable
        #       to get the current position is not in conflict when the interrupt pin wants to
        #       access the variable
        with self.enc_lock:
            self.pos_i = self.pos_i + increment

    # Callback function for the encoder (updates the counts/position of the encoder)
    # NOTE: this callback function is called whenever ENCB is triggered
    def __readEncoderB(self, channel):

        # read ENCA when ENCB has been triggered with a rising or falling signal
        a = GPIO.input(self.ENCA)
        b = GPIO.input(self.ENCB)

        increment = 0

        if (b > 0 and a > 0):
            # if ENCA is HIGH when ENCB is HIGH, motor is moving in the positive (CW) direction
            increment = 1
        elif (b == 0 and a == 0):
            # if ENCA is LOW when ENCB is LOW, motor is moving in the positive (CW) direction
            increment = 1
        else:
            # if ENCA has a different state compared to ENCB when measured, motor is moving in the
            # negative (CCW) direction
            increment = -1

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

        # change the velocity into RPM
        # Notes about conversion factors: 9.68 gear ratio, 48 counts/rev, 60 sec/min
        velocity = velocity/(9.68*48)*60.0

        return velocity
