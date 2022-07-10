# SpiderTreadmill

Version: 1.0.0<br>
Release Date: 2022-07-10<br>
[https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill](https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill)

## Summary

The purpose of this project is to develop a treadmill that will be used for insects. This GitHub repository contains various scripts that pertain to the development of the PID controller for a DC brushless motor provided by Pololu via this [link](https://www.pololu.com/product/4842), which will ultimately run the treadmill. The motor is controlled via a PID loop using a magnetic-based hall effect senson on the end of the motor. In addition to closed loop control over the motor, this project includes a LCD module to display the speeds live-time, an encoder/knob used to control the speed of the motor without the terminal, and IR beam sensors to check whether any insects have fallen off the treadmill.

## Getting Started

### Installation

In order to run the various scripts within repository, it is necessary to perform some initial installation of various required dependencies.

First clone the main repository: 

```
git clone https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill
```

Within this repository, we will need to download the code regarding the motor driver libraries, which are stored in a different repository.

```
cd SpiderTreadmill
git submodule update --init --recursive
```

Now install the motor driver library with the following commands:

```
cd Hardware_Testing_Scripts/single-tb9051ftg-motor-driver-rpi
sudo pip install .
```

The install command should install all dependencies as well, but if there are issues, external dependencies can also be installed via the following command within the `single-tb9051ftg-motor-driver-rpi` directory:

```
sudo pip install -r requirements.txt
```

With the motor driver library now installed, it is now necessary to install the PID libraries to run the controller. Find the `motor_PID_package` directory in the root directory and enter that directory. Within the directory, run the same installation command as above `sudo pip install .`. Once again, the dependencies should install automatically, but if there are errors, there has been a requirements.txt file included within this directory as well.

### Important directories/files

The `SpiderTreadmill` repository includes several useful scripts. Within the `Hardware_Testing_Scripts` directory, there are various scripts used to test different hardware to verify they are working properly. For example, `single-tb9051ftg-motor-driver-rpi` includes an example script to test the motor driver and the motor conditions. Because there are some legacy components that are not used within the current iteration of the treadmill, `encoder_knob_test.py, IR_break_beam_test.py, LCD_module_test.py` and `motor_test.py` are the modules you should take a closer look at.

The actual code used to run the main loop to run the treadmill is located within the `motor_PID_package` directory, named as `main.py`. To run this code, just run the following lines when you are in the directory:

```
python main.py
```

This directory also contains various other scripts that contain classes which operate the individual equipment for the treadmill, such as classes for the motor encoder in `Encoder_Class.py` or classes for the LCD module in `LCD_Class.py`.

## Features of the main loop

As mentioned above, the treadmill can be run via the `main.py` module. The following are some of the features for the treadmill.

* When first running the code, it is necessary to ensure all the IR sensors are connected correctly, or else the code will trip a fault and immediately shut the treadmill down as a safety precaution. The IR break beam sensors are used to detect whether or not the insects running on the treadmills have fallen off or something of the sorts. 
* The user has two main options to control the speed of the treadmill: via the terminal or via the encoder knob. The terminal allows the user to input a speed from -1.5 m/s to 1.5 m/s inclusive. The encoder knob can be turned to manually change the speed of the motor and changes the desired speed in increments of 0.1 m/s or 0.01 m/s (which can be toggled via a button switch built into the encoder).
* The speed of the treadmill will be displayed in terms of m/s to the LCD module, which displays the desired and actual speeds of the motor. Whenever the encoder button has been toggled, the LCD will also display what increment has been chosen.
* There has been a "ramping" function built into the code to reduce stress on the motor driver, which means changing the velocity of the motor will not be instantaneous (a bit similar to a human treadmill).

## Library reference

Most of the functionality of the treadmill, LCD, IR sensors, etc. are contained within the `*Class.py` scripts in  `motor_PID_package` directory. The code has been pretty well documented, so please refer to those directories regarding any of the functionalities of the main script.

## Version history

* 1.0.0 (2022-07-10): Original release.