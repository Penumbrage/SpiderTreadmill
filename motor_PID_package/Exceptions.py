'''
 * @file    Exceptions.py
 * @author  William Wang
 * @brief   This script stores various custom classes 
            that raise exceptions for motor faults and
            IR sensor trips in the main script
'''

# import required libraries
# NONE

# ----------------- Various exception classes ----------------------- #
# Define custom exceptions to raise if a fault is detected.
from tracemalloc import start


class DriverFault(Exception):
    '''
    DESCRIPTION: Class that defines the fault for the motor driver

    ARGS: driver_num (number for the driver that faulted)
    '''

    def __init__(self, driver_num):
        # Initialization function for the driver fault
        self.driver_num = driver_num

def raiseIfFault(motors):
    '''
    DESCRIPTION: Function that raises the DriverFault if a fault is detected
    for the motor driver

    ARGS: motors (motors object from single_tb9051ftg_motor_driver module)

    RETURN: NONE
    '''
    if motors.motor1.getFault():
        raise DriverFault(driver_num=1)

class BeamFault(Exception):
    '''
    DESCRIPTION: Class that defines the fault for the IR sensor if it is tripped

    ARGS: pin_num (number for the pin the IR sensor is on)
    '''

    def __init__(self, pin_num):
        # Initialization function for the IR sensor fault
        self.pin_num = pin_num

def raiseIfBeamBroken(IR_sen):
    '''
    DESCRIPTION: Function that raises the BeamFault if the IR sensor has been
    triggered via interrupt or via open circuit

    ARGS: IR_sen (IR_sensor object from the IR_Break_Beam_Class module)

    RETURN: NONE
    '''
    # check if the callback has been triggered (use lock to prevent race conditions with callback thread)
    with IR_sen.beam_lock:
        beam_triggered = IR_sen.triggered

    # raise the fault if the beam pin is LOW or the beam has been triggered via the callback
    if IR_sen.beam_broken() or beam_triggered:
        raise BeamFault(pin_num=IR_sen.beam_pin)

class ProgramStopped(Exception):
    '''
    DESCRIPTION: Class that defines an exception when user presses start/stop button to stop the main program

    ARGS: NONE
    '''

    def __init__(self):
        pass

def raiseIfProgramStopped(start_stop_button):
    '''
    DESCRIPTION: Function that raises the ProgramStopped exception when the user decides to stop
    the main function via the start/stop button

    ARGS: start_stop_button (StartStopButton object from the Buttons_Class.py module)

    RETURN: NONE
    '''
    # check if the callback has been triggered (use lock to prevent race conditions with callback thread)
    with start_stop_button.start_stop_lock:
        program_started = start_stop_button.program_started

    # raise the fault if the program has been stopped via the button
    if program_started == False:
        raise ProgramStopped