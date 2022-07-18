'''
 * @file    Data_Collection_Class.py
 * @author  William Wang
 * @brief   This script contains a class that allows
            the user store speed values into a .csv
            file which can be later exported for analysis
'''

# import the required libraries
import csv
import os
from datetime import datetime
import time

class DataLogger(object):
    '''
    DESCRIPTION: This class ontains various functions that allow the user to store
    time and speed data into a .csv file for future use (i.e. opening a new file, 
    saving data to the file, closing the file, etc.)

    ARGS: NONE
    '''

    def __init__(self):
        # initialization function for the class
        
        self.file_header = ['time_elapsed', 'desired_speed', 'actual_speed']            # header for the .csv data
        self.date_and_time = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")    # variable that stores the date and time for file names
        self.file_path = ''                                                     # variable that stores the file path to save the data to
        self.logs_path = ''                                                     # variable that stores the path for the data logs
        self.start_time = time.perf_counter()                                   # start time for the experiment

        # create a data_logs directory if it does not already exits
        self.__create_log_directory()

    def __create_log_directory(self):
        '''
        DESCRIPTION: This function is used when the object is initialized and creates a data_logs
        directory if it does not already exist

        ARGS: NONE

        RETURN: NONE
        '''

        # Obtain the path to the directory that holds this file
        curr_path = os.path.dirname(os.path.abspath(__file__))

        # Append the data_logs directory to the current path
        self.logs_path = curr_path + '/data_logs/'

        # Check if the data_logs directory already exists and create the directory if it doesn't
        path_exists = os.path.exists(self.logs_path)

        if not path_exists:
            # Create a new directory because it does not exist 
            os.makedirs(self.logs_path)
            print("\nBuilding data_logs directory")

    def create_new_file(self):
        '''
        DESCRIPTION: This function creates a new .csv file to save data to. The file 
        name is based off the date and time this function is called.

        ARGS: NONE

        RETURN: NONE
        '''

        # First get the date and time for the file name (in the form of a string)
        self.date_and_time = datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')

        # Create the file path to save to
        self.file_path = self.logs_path + self.date_and_time + '.csv'

        # Open the file and save the header to the file (the 'with' command eliminates the requirement to use file.close())
        with open(self.file_path, 'w+', encoding='UTF8', newline='') as f:
            # create .csv writer object
            csv_writer = csv.writer(f)

            # write the header to the file
            csv_writer.writerow(self.file_header)

    def save_data(self, data):
        '''
        DESCRIPTION: This function is used to save data to the currently open .csv file
        in the form of [time_elapsed, desired_speed, actual_speed]

        ARGS: data (in the form of [time_elapsed, desired_speed, actual_speed])

        RETURN: NONE
        '''

        # Open the file and save the new data into the file
        with open(self.file_path, 'a', encoding='UTF8', newline='') as f:
            # create .csv writer object
            csv_writer = csv.writer(f)

            # write the header to the file
            csv_writer.writerow(data)

    def set_start_time(self):
        '''
        DESCRIPTION: This function is used to set the start time for the trial when called

        ARGS: NONE

        RETURN: NONE
        '''

        self.start_time = time.perf_counter()

    def det_elasped_time(self):
        '''
        DESCRIPTION: This function is used to determine the elapsed time for the
        experiments as compared to the start time that is triggered via the
        experiment button.

        ARGS: NONE

        RETURN: elapsed_time (elapsed time since the start time of the experiment)
        '''

        current_time = time.perf_counter()

        elapsed_time = current_time - self.start_time

        return elapsed_time
