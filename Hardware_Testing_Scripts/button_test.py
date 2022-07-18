# This script is used to test the functionality of a simple switch for the Raspberry Pi

# import relevant libaries
import RPi.GPIO as GPIO

# Setup the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Identify the button pin
BUTTON_PIN = 9

# Set the button pin to be an input that is pulled down
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Define button callback function
def button_function(channel):
    # read in the button state
    button_state = GPIO.input(BUTTON_PIN)

    # determine the state and print out the respective statements
    if button_state == True:
        print("The button has been pressed!")
    elif button_state == False:
        print("The button has been released!")

# Add an interrupt function the pin for both rising and falling signals
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback = button_function, bouncetime = 100)

# Create an infinite loop to run the function
try:
    input("Press any key to exit the program: ")
except KeyboardInterrupt:
    print("\nKeyboard Interrupt")
finally:
    GPIO.cleanup()
