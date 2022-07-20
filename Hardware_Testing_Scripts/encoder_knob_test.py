# This is test code used to verify the functionality of the KY-040 rotary encoder used to
# change the speed of the motor
# Source for this code comes from this tutorial: https://blog.sharedove.com/adisjugo/index.php/2020/05/10/using-ky-040-rotary-encoder-on-raspberry-pi-to-control-volume/

import RPi.GPIO as GPIO

step = 0.1 #linear steps for increasing/decreasing volume
pressed = False #button pressed state

#tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
GPIO.setmode(GPIO.BCM)

#set up the pins we have been using
clk = 2
dt = 3
sw = 4

#set up the GPIO events on those pins
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#get the initial states
counter = 0
clkLastState = GPIO.input(clk)
dtLastState = GPIO.input(dt)
swLastState = GPIO.input(sw)

#define functions which will be triggered on pin state changes
def clkClicked(channel):
    global counter, step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 0 and dtState == 1:
        counter = counter - step
        print ("Counter ", counter)

def dtClicked(channel):
    global counter, step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 1 and dtState == 0:
        counter = counter + step
        print ("Counter ", counter)

def swClicked(channel):
    global pressed, step
    pressed = not pressed
    if pressed:
        step = 0.01
    else:
        step = 0.1
    print ("Pressed ", pressed)

print ("Initial clk:", clkLastState)
print ("Initial dt:", dtLastState)
print ("Initial sw:", swLastState)
print ("Initial increment:", step)
print ("=========================================")

#set up the interrupts
GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=200)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=200)
GPIO.add_event_detect(sw, GPIO.FALLING, callback=swClicked, bouncetime=300)

try:
    input("Start monitoring input; press any key to exit")
except KeyboardInterrupt:
    print("Keyboard interrupt")
finally:
    GPIO.cleanup()
