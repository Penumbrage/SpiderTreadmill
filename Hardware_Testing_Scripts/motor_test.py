# This script is used to send the motor a continuous voltage (hardware testing purposes)

# import required modules
from single_tb9051ftg_rpi import Motor, Motors, MAX_SPEED
from User_Input_class import UserInput
import Exceptions

# Create the Motor and Motors objects
motor1 = Motor(pwm1_pin=12, pwm2_pin=13, en_pin=4, enb_pin=5, diag_pin=6)
motors = Motors(motor1)

# Creat UserInput object to allow the user to change the PWM values
user_input = UserInput(input_mode='PWM')

# main function to test
def main():
    global motors, user_input
    
    try:
        while True:
            # check for driver faults
            Exceptions.raiseIfFault()

            # obtain user input if any
            user_input.readUserPWM()

            # obtain the current desired speed
            speed_des = user_input.speed_des

            # send the speed to the motor
            motors.setSpeeds(speed_des)
        
    except Exceptions.DriverFault as e:
        print("Driver %s fault!" % e.driver_num)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")

    finally:
        motors.forceStop()
        print("Program Exiting")

if __name__ == '__main__':
    main()
