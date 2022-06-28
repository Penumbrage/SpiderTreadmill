# This script is used to send the motor a continuous voltage

# import required modules
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

# main function to test
def main():
    global motors
    
    try:
        while True:
            motors.setSpeeds(240)
            raiseIfFault()
        
    except DriverFault as e:
        print("Driver %s fault!" % e.driver_num)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")

    finally:
        motors.forceStop()

if __name__ == '__main__':
    main()
