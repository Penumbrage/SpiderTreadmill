'''
 * @file    main.py
 * @author  William Wang
 * @brief   This script is the main script running the 
            PID controller for the DC motor
'''

# import required modules
from single_tb9051ftg_rpi import Motor, Motors, MAX_SPEED
from Encoder_Class import Encoder
from IR_Break_Beam_Class import IRBreakBeam
from PID_Controller_Class import MotorPID
from User_Input_Class import UserInput
from Knob_Class import Knob
from LCD_Class import LCD
from Data_Collection_Class import DataLogger
import Buttons_Class
import Exceptions
import RPi.GPIO as GPIO
import time
import board
import digitalio

# Create a StartStopButton object which will be used to start/stop the main function via a service
start_button = Buttons_Class.StartStopButton(button_pin=9)

def main():
    '''
    DESCRIPTION: main function that executes the treadmill script

    ARGS: NONE

    RETURN: NONE
    '''

    # pass in the start_button as a global variable
    global start_button

    # print start statement for the program to the terminal
    print("Program starting")

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
    lcd = LCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                        lcd_d7, lcd_columns, lcd_rows)

    # Create the Motor and Motors objects
    motor1 = Motor(pwm1_pin=12, pwm2_pin=13, en_pin=4, enb_pin=5, diag_pin=6)
    motors = Motors(motor1)

    # Create an encoder object
    encoder = Encoder(ENCA=23, ENCB=24)

    # Create an IR break beam sensor object
    IR_sen = IRBreakBeam(beam_pin=21)

    # Create user input object
    user_input = UserInput(input_mode='m/s')

    # Create data collection object
    data_logger = DataLogger()

    # Create object for the knob (requires the user_input object)
    knob = Knob(user_input=user_input, lcd=lcd, clk=18, dt=25, sw=20)

    # Create object for the preset speed button (requires the user_input object)
    preset_speed_button = Buttons_Class.PresetSpeedButton(button_pin=11, user_input=user_input, lcd=lcd)

    # Create object for the experiment button
    exp_button = Buttons_Class.ExperimentButton(button_pin=19, camera_pin=26, data_collector=data_logger,
                                                        user_input=user_input, lcd=lcd)

    # Create a PID control object
    motor_control = MotorPID(motor=motor1, encoder=encoder, data_logger=data_logger, exp_button=exp_button)

    # execute the main loop for the treadmill
    try:
        # print start message and current step size of the knob
        msg = "Program\nstarting!"
        lcd.sendtoLCDThread(target="main", msg=msg, duration=2.5, clr_before=True, clr_after=True)
        msg = "Curr step size:\n0.1 m/s"
        lcd.sendtoLCDThread(target="main", msg=msg, duration=2.5, clr_before=True, clr_after=True)
        time.sleep(5)        # synchonize the print statement with the main script

        # time delay after which print statements should occur (sec)
        print_delay = 1

        # create a start timer for the print statements
        print_time_start = time.perf_counter()

        while True:
            # test for driver faults
            Exceptions.raiseIfFault(motors=motors)

            # test to see if the user stopped the program with the button
            Exceptions.raiseIfProgramStopped(start_stop_button=start_button)

            # test the break beam sensor so that it isn't broken
            Exceptions.raiseIfBeamBroken(IR_sen=IR_sen)

            # attempt to get a user input if available on the queue (starts at zero speed and tries to maintain velocity)
            user_input.readUserInput()
            with user_input.speed_des_lock:            # access the speed_des_RPM with lock so that the rotary encoder does not access it via interrupts
                speed_des = user_input.speed_des_RPM
                user_changed_velocity = user_input.user_changed_velocity        # check if the user inputted a command via terminal

            # set the motor speed determined from user input and current motor speeds (ramping included)
            if (user_changed_velocity):
                msg = "Ramping speed"
                print(msg)
                lcd.sendtoLCDThread(target="main", msg=msg, duration=5, clr_before=True, clr_after=True)
                control_sig, curr_speed, user_changed_velocity = motor_control.changeMotorVelocity(ramp_time=5, speed_des=speed_des)
                user_input.user_changed_velocity = user_changed_velocity    # reset flag

                # convert desired and current speeds back to m/s and print to the LCD
                des_spd_mps = motor_control.RPMToMPS(speed_des)
                curr_spd_mps = motor_control.RPMToMPS(curr_speed)
                line_1 = "Des: %.2f m/s" % des_spd_mps
                line_2 = "\nAct: %.2f m/s" % curr_spd_mps
            else:
                control_sig, curr_speed = motor_control.maintainMotorVelocity(speed_des=speed_des)

                # convert desired and current speeds back to m/s and print to the LCD
                des_spd_mps = motor_control.RPMToMPS(speed_des)
                curr_spd_mps = motor_control.RPMToMPS(curr_speed)
                line_1 = "Des: %.2f m/s\n" % des_spd_mps
                line_2 = "\nAct: %.2f m/s" % curr_spd_mps

            # print desired motor speed livetime to the LCD module
            lcd.sendtoLCDThread(target="main", msg=line_1, duration=0, clr_before=False, clr_after=False)

            # check the print time
            print_time_stop = time.perf_counter()

            # print useful information about motor speeds to terminal
            if ((print_time_stop - print_time_start) >= print_delay):
                # print(control_sig, "|", speed_des, "|", curr_speed)
                lcd.sendtoLCDThread(target="main", msg=line_2, duration=0, clr_before=False, clr_after=False)    # print the actual speeds on a delay
                print_time_start = time.perf_counter()

    except KeyboardInterrupt:
        # print stop messages
        print("\nKeyboard Interrupt")
        msg = "Program stopped!"
        lcd.sendtoLCDThread(target="main", msg=msg, duration=0, clr_before=True, clr_after=False)

        # reset the program_start variable
        with start_button.start_stop_lock:
            start_button.program_started = False

        # slow the motor down so that it does not stop abruptly
        speed_des = 0
        motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)

        # add delay to allow the message to print the LCD screen
        time.sleep(0.2)

    except Exceptions.ProgramStopped as p:
        # print stop messages
        msg = "Program stopped!"
        print("\n" + msg)
        lcd.sendtoLCDThread(target="main", msg=msg, duration=0, clr_before=True, clr_after=False)

        # reset the program_start variable
        with start_button.start_stop_lock:
            start_button.program_started = False

        # slow the motor down to a halt
        speed_des = 0
        motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)

        # add delay to allow exception to print to LCD
        time.sleep(0.2)

    except Exceptions.DriverFault as e:
        # print messages
        print("\nDriver %s fault!" % e.driver_num)
        msg = ("Driver %s fault!" % e.driver_num)
        lcd.sendtoLCDThread(target="main", msg=msg, duration=0, clr_before=True, clr_after=False)

        # reset the program_started variable
        with start_button.start_stop_lock:
            start_button.program_started = False

        # add delay to allow fault to print to LCD
        time.sleep(0.2)

    except Exceptions.BeamFault as b:
        # print messages
        print(f"\nIR sensor on pin {b.pin_num} is broken or has been triggered!")
        msg = ("IR %s triggered!" % b.pin_num)
        lcd.sendtoLCDThread(target="main", msg=msg, duration=0, clr_before=True, clr_after=False)
        print("Motor shutting down!")

        # reset the program_started variable
        with start_button.start_stop_lock:
            start_button.program_started = False

        # slow the motor down to a halt
        speed_des = 0
        motor_control.changeMotorVelocity(ramp_time=2, speed_des=speed_des)

        # add delay to allow message to print to LCD screen
        time.sleep(0.2)

    finally:
        GPIO.cleanup()
        print("GPIO pins cleaned up")
        motors.forceStop()
        print("Motors stopped")
        print("Program exited")


# Execute the main function
if __name__ == '__main__':
    # Execute an infinite loop that runs as a background service

    while True:
        # get the state for the start_stop button (to see if we should start the main program)
        with start_button.start_stop_lock:
            program_started = start_button.program_started
    
        if program_started == True:
            # only execute the main program if the start button has been pressed
            main()  

            # break out of the while loop (the service will restart the entire script)
            break     
