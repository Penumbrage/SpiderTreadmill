# Script used to test the Adafruit Bonnet motor driver
# NOTE: 

# import relevant libraries
import time
import board
from adafruit_motorkit import MotorKit

# 
kit = MotorKit(i2c=board.I2C())

kit.motor1.throttle = 1.0
time.sleep(0.5)
kit.motor1.throttle = 0
