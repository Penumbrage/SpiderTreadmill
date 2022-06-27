# This script is the main script running the PID controller for the DC motor

# import required modules
from single_tb9051ftg_rpi import Motor, Motors, MAX_SPEED
from Encoder_Class import Encoder
from IR_Break_Beam_Class import IRBreakBeam
from PID_Controller_Class import MotorPID
from User_Input_Class import UserInput
import RPi.GPIO as GPIO

# ---------------- Create various objects required for the script --------------------- #
# Create the Motor and Motors objects
motor1 = Motor(pwm1_pin=12, pwm2_pin=13, en_pin=4, enb_pin=5, diag_pin=6)
motors = Motors(motor1)

# Create an encoder object
encoder = Encoder(ENCA=23, ENCB=24)

# Create an IR break beam sensor object
IR_sen = IRBreakBeam(beam_pin=21)

# Create a PID control object
motor_control = MotorPID(motor=motor1, encoder=encoder)

# Create user input object
user_input = UserInput()

# ----------------- Various exception classes ----------------------- #
# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(driver_num=1)

# Custom class break beam exception
class BeamFault(Exception):
    def __init__(self, pin_num):
        self.pin_num = pin_num

# fault function function for the break beam sensor
def raiseIfBeamBroken():
    # if the BEAM_RECEIVER pin is low, then the beam is broken
    if IR_sen.beam_broken():
        raise BeamFault(pin_num=IR_sen.beam_pin)


# Main execution loop for the script
if __name__ == '__main__':

    try:
        # counter for the print statements
        print_counter = 0

        # Initialize the desired speed to be 0
        speed_des = 0

        while True:
            # test for driver faults
            raiseIfFault()

            # test the break beam sensor so that it isn't broken
            raiseIfBeamBroken()

            # attempt to get a user input if available on the queue
            speed_des, user_changed_velocity = user_input.readUserInput()

            # set the motor speed determined from user input and current motor speeds (ramping included)
            if (user_changed_velocity):
                control_sig, curr_speed, user_changed_velocity = motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)
            else:
                control_sig, curr_speed = motor_control.maintainMotorVelocity(speed_des=speed_des)

            # print useful information about motor speeds
            if (print_counter % 10 == 0):
                print(control_sig, "|", speed_des, "|", curr_speed)

            print_counter = print_counter + 1

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        
        # slow the motor down so that it does not stop abruptly
        speed_des = 0
        motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)

    except DriverFault as e:
        print("Driver %s fault!" % e.driver_num)

    except BeamFault as b:
        print(f"IR sensor on pin {b.pin_num} is broken!")
        print("Motor shutting down!")

        # slow the motor down to a halt
        speed_des = 0
        motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)

    finally:
        GPIO.cleanup()
        print("GPIO pins cleaned up")
        motors.forceStop()
        print("Motors stopped")
        print("Program exited")
