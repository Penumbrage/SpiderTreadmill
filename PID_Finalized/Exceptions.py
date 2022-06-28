# This script stores various custom classes that raise exceptions in the main script

# import required libraries
# NONE

# ----------------- Various exception classes ----------------------- #
# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault(motors):
    if motors.motor1.getFault():
        raise DriverFault(driver_num=1)

# Custom class break beam exception
class BeamFault(Exception):
    def __init__(self, pin_num):
        self.pin_num = pin_num

# fault function function for the break beam sensor
def raiseIfBeamBroken(IR_sen):
    # if the BEAM_RECEIVER pin is low, then the beam is broken
    if IR_sen.beam_broken():
        raise BeamFault(pin_num=IR_sen.beam_pin)