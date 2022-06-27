# This class entails several functions that obtain the user input regarding changing the motor speed of the DC motor

# import required modules
import queue
import threading
from math import pi

class UserInput(object):
    '''
    This class entails several functions that run a separate thread which handle user inputs 
    regarding changing the speed of the DC motor
    '''

    # instantiation function
    def __init__(self):
        self.q = queue.Queue()      # queue used to pass information from the user input to the motors

        # create a thread that runs the user input function (obtain user defined speeds)
        # NOTE: This is a daemon thread which allows the thread to be killed when the main program is killed,
        #       or else main thread will not be killed
        self.user_input_thread = threading.Thread(target=self.getUserInput, args=(self,), daemon=True)
        
        # start the thread upon instantiation
        self.user_input_thread.start()

    # Create function running in child thread that waits for user inputs for speeds
    def getUserInput(self):
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

            except ValueError:
                print("You did not enter a number in the correct format (check for any unwanted characters, spaces, etc).")
                print("Please enter your speed again.")

    # Create a function that reads the user input from the queue in the main thread and updates the speed_des variable
    def readUserInput(self):

        # determine the desired speed from the user (in m/s) and covert it to RPM
        try:
            speed_des = self.q.get(block=False)                  # False used to prevent code on waiting for info
            print(f'Current desired speed updated to: {speed_des} m/s')
            user_changed_velocity = True
            speed_des = speed_des*(60/pi)/(2/39.3701)       # conversion to RPM

            return speed_des, user_changed_velocity

        except queue.Empty:
            pass
