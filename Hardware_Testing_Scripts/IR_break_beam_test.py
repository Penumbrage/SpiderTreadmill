# This script serves to test the IR break beam sensor provided by Adafruit

# import relevant libraries
import RPi.GPIO as GPIO
import time

# set the board mode to BCM
GPIO.setmode(GPIO.BCM)

# define the pin for the IR receiver
BEAM_RECEIVER = 21

# set up the pin to as in input with resister pulled up HI
GPIO.setup(BEAM_RECEIVER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Loop to test the break beam sensor

try:
    while True:
        # read the state of the receiver
        beam_state = GPIO.input(BEAM_RECEIVER)

        # if the receiver is LOW, then the beam is broken
        if beam_state == False:
            print("The beam is broken!")
        else:
            print("The beam is fine!")

        # wait 1 second before reading another time
        time.sleep(2)

except KeyboardInterrupt:
    print("\nKeyboard Interrupt ... Exiting")

finally:
    print("GPIO pins cleaned up")
    GPIO.cleanup()
    print("Exited")