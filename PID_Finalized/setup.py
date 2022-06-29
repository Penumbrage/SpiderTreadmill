# Setup script to import all the different classes

from distutils.core import setup
setup(name='motor_PID_package',
      version='1.0.0',
      description=('Librairy containing all the different modules '
                    'required to operate a DC motor with PID'),
      author='William Wang',
      url='https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill',
      py_modules=['Encoder_Class', 'Exceptions', 'IR_Break_Beam_Class', 'PID_Controller_Class', 'User_Input_class'],
      )
