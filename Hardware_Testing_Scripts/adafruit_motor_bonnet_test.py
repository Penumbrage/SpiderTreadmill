# Script used to test the Adafruit Bonnet motor driver
# NOTE: This script includes code for both the DC motor and stepper motors
# Comment out the right script for any tests

# import relevant libraries
import time
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

#----- Code for the DC motor ---------#
# # create driver object
# kit = MotorKit(i2c=board.I2C())

# # run motor at full speed for 0.5 seconds
# kit.motor1.throttle = 1.0
# time.sleep(0.5)

# # stop the motor
# kit.motor1.throttle = 0

# # run motor at 3/10 speed for 10 seconds
# kit.motor1.throttle = 0.30
# time.sleep(10)

# # stop the motor
# kit.motor1.throttle = 0
#-------------------------------------#

#----------Code for the stepper motor--------#
# Create motor driver object
kit = MotorKit(i2c=board.I2C())

# Step 1000 steps
for i in range(15*2048):
    position = kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    # time.sleep(0.001)     # NOTE: this command dictates the speed at which the steps are executed
    print(position)
#--------------------------------------------#

#TODO: Figure out how to increase the speed of rotation