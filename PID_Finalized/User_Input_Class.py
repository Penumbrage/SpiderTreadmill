# This class entails several functions that obtain the user input regarding changing the motor speed of the DC motor

# import required modules
import queue
import threading
import time
from math import pi

class UserInput(object):
    '''
    This class entails several functions that run a separate thread which handle user inputs 
    regarding changing the speed of the DC motor
    '''

    # instantiation function
    def __init__(self, input_mode):
        self.speed_des_mps = 0          # initially set the desired speed to be 0 m/s
        self.speed_des_RPM = 0          # desired speed in RPM
        self.speed_des_PWM = 0          # desired speed in terms of PWM
        self.user_changed_velocity = False          # initially set the motor to maintain velocities
        self.q = queue.Queue()      # queue used to pass information from the user input to the motors
        self.input_mode = input_mode        # string that specifies what type of user thread to run

        # create a thread that runs the user input function (obtain user defined speeds)
        # NOTE: This is a daemon thread which allows the thread to be killed when the main program is killed,
        #       or else main thread will not be killed
        
        # if user wants to input m/s values
        if self.input_mode == 'm/s':
            self.user_input_thread = threading.Thread(target=self.__getUserInput, daemon=True)
            
            # start the thread upon instantiation
            self.user_input_thread.start()

        # if user wants to input PWM values
        elif self.input_mode == 'PWM':
            self.user_input_thread = threading.Thread(target=self.__getUserPWM, daemon=True)
            self.user_input_thread.start()

    # Create function running in child thread that waits for user inputs for speeds
    def __getUserInput(self):
        # loop that is always waiting for a user input for the speed (running on a separate thread)
        while True:
            try:
                # obtain the user input for the motor speed
                user_input = input('Enter a motor speed in meters/second (range from [-1.5, 1.5] m/s): ')

                # try to turn the input into a float (will throw an exception if it doesn't work)
                user_input = float(user_input)

                # check the number to see if it is in the correct range (0 m/s to 1.5 m/s)
                if not ((user_input >= -1.5) and (user_input <= 1.5)):
                    print("The speed you entered is not within the specified range. Please enter a new speed.")
                else:
                    self.q.put(user_input)       # put the user-defined speed on the queue in m/s

                # After successfully sending a user input, wait a bit before sending the next input
                time.sleep(0.1)

            except ValueError:
                print("You did not enter a number in the correct format (check for any unwanted characters, spaces, etc).")
                print("Please enter your speed again.")

    # Create function running in child thread that waits for user inputs for speeds (in terms of PWM values)
    def __getUserPWM(self):
        # loop that is always waiting for a user input for the speed (running on a separate thread)
        while True:
            try:
                # obtain the user input for the motor speed
                user_input = input('Enter a motor speed in PWM (range from [-480, 480]): ')

                # try to turn the input into a float (will throw an exception if it doesn't work)
                user_input = float(user_input)

                # check the number to see if it is in the correct range (-480 to 480)
                if not ((user_input >= -480.0) and (user_input <= 480.0)):
                    print("The speed you entered is not within the specified range. Please enter a new speed.")
                else:
                    self.q.put(user_input)       # put the user-defined speed on the queue

                # After successfully sending a user input, wait a bit before sending the next input
                time.sleep(0.1)

            except ValueError:
                print("You did not enter a number in the correct format (check for any unwanted characters, spaces, etc).")
                print("Please enter your speed again.")

    # Create a function that reads the user input from the queue in the main thread and updates the speed_des variable
    def readUserInput(self):

        # determine the desired speed from the user (in m/s) and covert it to RPM
        try:
            self.speed_des_mps = self.q.get(block=False)                  # False used to prevent code on waiting for info
            print(f'Current desired speed updated to: {self.speed_des_mps} m/s')
            self.user_changed_velocity = True
            self.speed_des_RPM = self.speed_des_mps*(60/pi)/(2/39.3701)       # conversion to RPM

        except queue.Empty:
            pass

    # Create a function that reads the user input from the queue in the main thread and updates the speed_des variable (for open loop PWM applications)
    def readUserPWM(self):

        # determine the desired speed from the user
        try:
            self.speed_des_PWM = self.q.get(block=False)                  # False used to prevent code on waiting for info
            print(f'Current desired speed updated to: {self.speed_des_PWM}')

        except queue.Empty:
            pass
