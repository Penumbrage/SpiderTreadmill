# This is test code used to verify the functionality of the KY-040 rotary encoder used to 
# change the speed of the motor

import RPi.GPIO as GPIO
 
step = 1 #linear steps for increasing/decreasing volume
pressed = False #button pressed state
 
#tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
GPIO.setmode(GPIO.BCM) 
 
#set up the pins we have been using
clk = 18
dt = 25
sw = 8
 
#set up the GPIO events on those pins
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
#get the initial states
counter = 0
clkLastState = GPIO.input(clk)
dtLastState = GPIO.input(dt)
swLastState = GPIO.input(sw)
 
#define functions which will be triggered on pin state changes
def clkClicked(channel):
    global counter
    global step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 0 and dtState == 1:
            counter = counter + step
            print ("Counter ", counter)
 
def dtClicked(channel):
    global counter
    global step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
        
    if clkState == 1 and dtState == 0:
            counter = counter - step
            print ("Counter ", counter)
 
def swClicked(channel):
    global pressed
    pressed = not pressed
    print ("Paused ", pressed)             
                 
print ("Initial clk:", clkLastState)
print ("Initial dt:", dtLastState)
print ("Initial sw:", swLastState)
print ("=========================================")
 
#set up the interrupts
GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=300)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=300)
GPIO.add_event_detect(sw, GPIO.FALLING, callback=swClicked, bouncetime=300)
 
input("Start monitoring input")
 
GPIO.cleanup()