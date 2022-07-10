'''
 * @file    LCD_Class.py
 * @author  William Wang
 * @brief   This script entails the class that covers the various functions 
            to be used with the 1602a LCD module
'''

# import required libraries
import queue
import time
import threading
import adafruit_character_lcd.character_lcd as characterlcd

class LCD(characterlcd.Character_LCD_Mono):
    '''
    DESCRIPTION: This class is used to control the print statements sent to the 1602a LCD
    module. Note that this class is inherited from the Adafruit characterlcd
    class, so all dependencies related to that class must be installed.
    One of the major purposes of inheriting this class is the ability to 
    allow for asychronous printing to the LCD module from various threads.
    
    ARGS: cd_rs, lcd_en, lcd_d4 lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows
    (various pins required for the LCD module)
    '''

    # initialization function for the LCD class
    def __init__(self, cd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                    lcd_d7, lcd_columns, lcd_rows):
        
        # initialize the LCD pins using the original parent class
        super().__init__(rs=cd_rs, en=lcd_en, db4=lcd_d4, db5=lcd_d5,
                            db6=lcd_d6, db7=lcd_d7, columns=lcd_columns, lines=lcd_rows)

        # create two queues (one for the main loop, one for the rotary encoder)
        self.main_q = queue.Queue(maxsize=0)        # infinite queue size
        self.knob_q = queue.Queue(maxsize=2)        # put a limit on the knob queue (prevent repetitive msgs)

        # create two lists to receive items from the above queues
        self.main_item = []
        self.knob_item = []

        # create and start the lcd thread
        self.lcd_thread = threading.Thread(target=self.__lcdThread, daemon=True)
        self.lcd_thread.start()

    def __lcdThread(self):
        '''
        DESCRIPTION: Function that runs the main thread for printing statements to the lcd module.
        Note that this thread will place priority on the messages sent from the Knob class because
        the users need to know what speeds they are changing the motors to.

        ARGS: NONE

        RETURN: NONE
        '''

        # always running this separate thread waiting for messages from the main loop and knob loop
        while True:
            # first try the knob queue because this queue has priority messages
            try:
                self.knob_item = self.knob_q.get_nowait()   # obtain message from knob queue
                self.printfromLCDThread(item = self.knob_item)
            except queue.Empty:
                # only after the knob queue is completely empty do we print from the main loop
                try:
                    self.main_item = self.main_q.get_nowait()
                    self.printfromLCDThread(item = self.main_item)
                except queue.Empty:
                    # NOTE: it is very important to have this delay here or else this thread runs too fast
                    time.sleep(0.001)

    def sendtoLCDThread(self, target, msg, duration, clr_before, clr_after):
        '''
        DESCRIPTION: Function that puts a message into the lcd queue
        NOTE: this function requires the user to input extra parameters such as
        the desired duration of the message and whether to clear the screen
        before/after the message

        ARGS: target ("main" for messages from the main loop, "knob" for messages from the knob loop),
        msg (desired msg to be sent to LCD), duration (duration of message in seconds), clr_before/clr_after
        (boolean - True to clear screen before and after placing msg on screen)

        RETURN: NONE
        '''

        # create a list to send over to the queue
        item = [msg, duration, clr_before, clr_after]

        # determine which queue to send the message to and send the item
        if (target == "main"):
            self.main_q.put_nowait(item)
        elif (target == "knob"):
            try:
                # try to put message on knob queue
                self.knob_q.put_nowait(item)
            except queue.Full:
                # if knob queue is full, ignore any further messages (likely repetitive)
                pass
 
    def printfromLCDThread(self, item):
        '''
        DESCRIPTION: Function that retrieves a message from the queue and prints the message
        NOTE: this function requires the duration of the print and whether to clear the print
        statement before and after the message

        ARGS: item (a list containing the following -- [msg, duration, clr_before, clr_after])
        RETURN: NONE
        '''

        # obtain various information from item
        msg = item[0]
        duration = item[1]
        clr_before = item[2]
        clr_after = item[3]

        # check to see if the screen needs to be cleared
        if clr_before == True:
            self.clear()
        else:
            pass

        # put the message onto the lcd monitor for the desired duration
        self.message = msg
        if not duration == 0:
            time.sleep(duration)
        else:
            pass

        # check to see if the screen needs to be cleared after the message
        if clr_after == True:
            self.clear()
        else:
            pass
