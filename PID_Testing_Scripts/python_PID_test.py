# This script is a script that implements the PID control algorithm on the Raspberry Pi

# import required libraries
import time
import RPi.GPIO as GPIO
from single_tb9051ftg_rpi import Motor, Motors, MAX_SPEED

# Create the Motor and Motors objects
motor1 = Motor(pwm1_pin=12, pwm2_pin=13, en_pin=4, enb_pin=5, diag_pin=6)
motors = Motors(motor1)

# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(1)

# Main execution loop for the motor
if __name__ == '__main__':
    try:
        while True:
            motors.motor1.setSpeed(MAX_SPEED/2)
            raiseIfFault()
    
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        motors.forceStop()

    except DriverFault as e:
        print("Driver %s fault!" % e.driver_num)
        motors.forceStop()

    finally:
        print("Program Exited")
        motors.forceStop()