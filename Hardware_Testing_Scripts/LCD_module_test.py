# This script is used to test the LCD module's functionality. By default,
# the script should display the RPi's date, time, and IP address

# NOTE: This script requires specific packages to be installed from Adafruit
#       which can be found via this website: https://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/necessary-packages

# NOTE: For the VO pin, which provides the contrast on the LCD screen, a 5K Ohm resistor was used instead
#       of the potentiometer.

# SPDX-FileCopyrightText: 2018 Mikey Sklar for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D9)
lcd_en = digitalio.DigitalInOut(board.D11)
lcd_d4 = digitalio.DigitalInOut(board.D8)
lcd_d5 = digitalio.DigitalInOut(board.D7)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d7 = digitalio.DigitalInOut(board.D6)


# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

# looking for an active Ethernet or WiFi device
def find_interface():
    find_device = "ip addr show"
    interface_parse = run_cmd(find_device)
    for line in interface_parse.splitlines():
        if "state UP" in line:
            dev_name = line.split(':')[1]
    return dev_name

# find an active IP on the first LIVE network device
def parse_ip():
    find_ip = "ip addr show %s" % interface
    find_ip = "ip addr show %s" % interface
    ip_parse = run_cmd(find_ip)
    for line in ip_parse.splitlines():
        if "inet " in line:
            ip = line.split(' ')[5]
            ip = ip.split('/')[0]
    return ip

# run unix shell command, return as ASCII
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode('ascii')

# wipe LCD screen before we start
lcd.clear()

# before we start the main loop - detect active network device and ip address
sleep(2)
interface = find_interface()
ip_address = parse_ip()

try:
    while True:

        # date and time
        lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

        # current ip address
        lcd_line_2 = "IP " + ip_address

        # combine both lines into one update to the display
        lcd.message = lcd_line_1 + lcd_line_2

        sleep(1)

except KeyboardInterrupt:
    print("\nexiting...")
    lcd.clear()
