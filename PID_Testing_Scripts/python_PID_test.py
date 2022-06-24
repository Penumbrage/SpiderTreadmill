# This script is a script that implements the PID control algorithm on the Raspberry Pi

# import required libraries
import time
import RPi.GPIO as GPIO
from single_tb9051ftg_rpi import Motor, Motors, MAX_SPEED

# Ensure the GPIO is using BCM numbering
GPIO.setmode(GPIO.BCM)

# Create the Motor and Motors objects
motor1 = Motor(pwm1_pin=12, pwm2_pin=13, en_pin=4, enb_pin=5, diag_pin=6)
motors = Motors(motor1)

# Define and set up pins for the encoder
ENCA = 23
ENCB = 24
GPIO.setup(ENCA, GPIO.IN)
GPIO.setup(ENCB, GPIO.IN)

# Create global variables required for the script
pos_i = 0           # variable that stores the encoder position from the interrupt function
pos_prev = 0        # variable that stores the previous position of the motor shaft (used to calculate motor vel)
time_prev = time.time()       # variable that stores the previous time for the motor speed calculation

# Create function to calculate the motor velocity
def calcMotorVelocity():
    global pos_prev, pos_i, time_prev

    # calculate motor velocity (in counts/second)
    pos_curr = pos_i
    time_curr = time.time()
    deltaT = time_curr - time_prev
    velocity = (pos_curr - pos_prev)/deltaT

    # change the velocity into RPM
    velocity = velocity/116.16*60.0

    # update the previous time and position variables
    pos_prev = pos_curr
    time_prev = time_curr

    return velocity

# Create function to execute the PID controller
def motorPID():
    global 

    # tuning constants
    k_p = 0.01
    k_i = 0.0001
    k_d = 0

    return u

# Callback function for the encoder
def readEncoder(channel):
    global pos_i

    # read ENCB when ENCA has been triggered with a rising signal
    b = GPIO.input(ENCB)
    increment = 0
    if (b > 0):
        # if ENCB is HIGH when ENCA is HIGH, motor is moving in negative (CCW) direction
        increment = -1
    else:
        # if ENCB is LOW when ENCA is HIGH, motor is moving in the positive (CW) direction
        increment = 1

    pos_i = pos_i + increment

# Create interrupt to ENCA
GPIO.add_event_detect(ENCA, GPIO.RISING, callback = readEncoder)

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
            raiseIfFault()
            motors.motor1.setSpeed(MAX_SPEED/4)
            m_vel = calcMotorVelocity()
            print(m_vel)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        motors.forceStop()

    except DriverFault as e:
        print("Driver %s fault!" % e.driver_num)
        motors.forceStop()

    finally:
        print("Program Exited")
        GPIO.cleanup()
        motors.forceStop()
