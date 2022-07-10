'''
 * @file    setup.py
 * @author  William Wang
 * @brief   Setup script to import all the different classes and any
            other necessary modules/packages
'''

from setuptools import setup

setup(name='motor_PID_package',
      version='1.0.0',
      description=('Librairy containing all the different modules '
                    'required to operate a DC motor with PID'),
      author='William Wang',
      url='https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill',
      install_requires=['adafruit-blinka', 'adafruit-circuitpython-charlcd', 'single_tb9051ftg_rpi'],
      py_modules=['Encoder_Class', 'Exceptions', 'IR_Break_Beam_Class', 'PID_Controller_Class',
                   'User_Input_Class', 'Knob_Class', 'LCD_Class'],
      )
