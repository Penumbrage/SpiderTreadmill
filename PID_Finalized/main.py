# This script is the main script running the PID controller for the DC motor

# import required modules
from single_tb9051ftg_rpi import Motor, Motors, MAX_SPEED
from Encoder_Class import Encoder
from IR_Break_Beam_Class import IRBreakBeam
from PID_Controller_Class import MotorPID
from User_Input_Class import UserInput
import Exceptions
import RPi.GPIO as GPIO
import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# ---------------- Create various objects required for the script --------------------- #
# Create the LCD object for the LCD screen (requires some setup with the input pins)
# Size of the LCD
lcd_columns = 16
lcd_rows = 2

# pin definitions for the LCD
lcd_rs = digitalio.DigitalInOut(board.D2)
lcd_en = digitalio.DigitalInOut(board.D3)
lcd_d4 = digitalio.DigitalInOut(board.D17)
lcd_d5 = digitalio.DigitalInOut(board.D27)
lcd_d6 = digitalio.DigitalInOut(board.D22)
lcd_d7 = digitalio.DigitalInOut(board.D10)

# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

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
user_input = UserInput(input_mode='m/s')

# Main execution loop for the script
if __name__ == '__main__':

    try:
        # print start message
        lcd.clear()
        lcd.message = "Program started!"
        time.sleep(5)
        lcd.clear()

        # time delay after which print should occur (sec)
        print_delay = 1

        # create a start timer for the print statements
        print_time_start = time.perf_counter()

        while True:
            # test for driver faults
            Exceptions.raiseIfFault(motors=motors)

            # test the break beam sensor so that it isn't broken
            Exceptions.raiseIfBeamBroken(IR_sen=IR_sen)

            # attempt to get a user input if available on the queue (starts at zero speed and tries to maintain velocity)
            user_input.readUserInput()
            speed_des = user_input.speed_des
            user_changed_velocity = user_input.user_changed_velocity

            # set the motor speed determined from user input and current motor speeds (ramping included)
            if (user_changed_velocity):
                lcd.clear()
                lcd.message = "Ramping speed"      # indicate speed ramp is occurring
                control_sig, curr_speed, user_changed_velocity = motor_control.changeMotorVelocity(ramp_time=5, speed_des=speed_des)
                lcd.clear()
                user_input.user_changed_velocity = user_changed_velocity    # reset flag

                # convert desired and current speeds back to m/s and print to the LCD
                des_spd_mps = motor_control.RPMToMPS(speed_des)
                curr_spd_mps = motor_control.RPMToMPS(curr_speed)
                line_1 = "Des: %.2f m/s\n" % des_spd_mps
                line_2 = "Act: %.2f m/s" % curr_spd_mps
            else:
                control_sig, curr_speed = motor_control.maintainMotorVelocity(speed_des=speed_des)

                # convert desired and current speeds back to m/s and print to the LCD
                des_spd_mps = motor_control.RPMToMPS(speed_des)
                curr_spd_mps = motor_control.RPMToMPS(curr_speed)
                line_1 = "Des: %.2f m/s\n" % des_spd_mps
                line_2 = "Act: %.2f m/s" % curr_spd_mps

            # check the print time
            print_time_stop = time.perf_counter()

            # print useful information about motor speeds
            if ((print_time_stop - print_time_start) >= print_delay):
                print(control_sig, "|", speed_des, "|", curr_speed)
                lcd.message = line_1 + line_2
                print_time_start = time.perf_counter()

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        lcd.clear()
        lcd.message = "Program stopped!"

        # slow the motor down so that it does not stop abruptly
        speed_des = 0
        motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)

    except Exceptions.DriverFault as e:
        print("Driver %s fault!" % e.driver_num)
        lcd.clear()
        lcd.message = ("Driver %s fault!" % e.driver_num)

    except Exceptions.BeamFault as b:
        print(f"IR sensor on pin {b.pin_num} is broken or has been triggered!")
        lcd.clear()
        lcd.message = ("IR %s triggered!" % b.pin_num)
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
