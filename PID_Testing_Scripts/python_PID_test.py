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
pos_i = 0                       # variable that stores the encoder position from the interrupt function
pos_prev = 0                    # variable that stores the previous position of the motor shaft (used to calculate motor vel)
time_prev = time.time()         # variable that stores the previous time for the motor speed calculation
deltaT = 0                      # variable that stores the difference in time between two executions of the motor velocity calculation function
err_prev = 0                    # variable that stores the error from the previous iteration of PID function (used for the integral and derivative terms)
err_sum = 0                     # variable that stores the integral sum of the error for the integral term of the PID
u_prev = 0                      # variable that stores the previous control signal sent to the motor (used to generate new control signal)         

# Create function to calculate the motor velocity
def calcMotorVelocity():
    global pos_prev, pos_i, time_prev, deltaT

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
def motorPID(desired_vel, meas_vel):
    global err_prev, err_sum, deltaT, u_prev

    # tuning constants
    k_p = 0.01
    k_i = 0.0001
    k_d = 0

    # calculate the current error between the desired and measured motor speeds
    err = desired_vel - meas_vel

    # calculate the sum of the error for the integral term for the PID
    err_sum = err_sum + (1/2)*(err + err_prev)*deltaT

    # calculate the change in error for the derivative term for the PID
    deltaErr = err - err_prev

    # calculate the control signal
    u = k_p*err + k_i*err_sum + k_d*(deltaErr/deltaT) + u_prev

    # update required global variables for the next iteration of the loop
    err_prev = err
    u_prev = u

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
        
        # set the desired speed of the motor in RPM
        speed_des = 500

        while True:
            raiseIfFault()
            # motors.motor1.setSpeed(MAX_SPEED/4)
            m_vel = calcMotorVelocity()
            control_sig = motorPID(speed_des, m_vel)
            motor1.setSpeed(control_sig)
            print(speed_des, m_vel)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")

    except DriverFault as e:
        print("Driver %s fault!" % e.driver_num)

    finally:
        print("Program Exited")
        GPIO.cleanup()
        motors.forceStop()
