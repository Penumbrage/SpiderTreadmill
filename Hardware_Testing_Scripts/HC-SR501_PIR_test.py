# This code tests the functionality of the HC-SR501 PIR motion sensor

# import relavant libraries
import RPi.GPIO as GPIO
import time

# Assign the sensor to a GPIO pin on the Raspberry Pi
GPIO.setmode(GPIO.BCM) #Set GPIO to use BCM numbering
PIR_pin = 21 #Assign pin 8 to PIR
# led = 10 #Assign pin 10 to LED

# setup the pins as output or input
GPIO.setup(PIR_pin, GPIO.IN) #Setup GPIO pin PIR as input
# GPIO.setup(led, GPIO.OUT) #Setup GPIO pin for LED as output

# Initialize the sensor for 1 minute (indicated in spec sheet)
print ("Sensor initializing . . .")
time.sleep(60) #Give sensor time to startup
print ("Sensor active")
print ("Press Ctrl+c to end program")

# The main execution loop for the sensor
try:
    while True:
        if GPIO.input(PIR_pin) == True: #If PIR pin goes high, motion is detected
            print ("Motion Detected!")
            # GPIO.output(led, True) #Turn on LED
            # time.sleep(4) #Keep LED on for 4 seconds
            # GPIO.output(led, False) #Turn off LED
            # time.sleep(0.1)

except KeyboardInterrupt: #Ctrl+c
    pass #Do nothing, continue to finally

finally:
    #  GPIO.output(led, False) #Turn off LED in case left on
    GPIO.cleanup() #reset all GPIO
    print ("Program ended")