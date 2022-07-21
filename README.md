# SpiderTreadmill

Version: 1.0.1<br>
Release Date: 2022-07-18<br>
[https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill](https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill)

## Summary

The purpose of this project is to develop a treadmill that will be used for insects. This GitHub repository contains various scripts that pertain to the development of the PID controller for a DC brushless motor provided by Pololu via this [link](https://www.pololu.com/product/4842), which will ultimately run the treadmill. The motor is controlled via a PID loop using a magnetic-based hall effect senson on the end of the motor. In addition to closed loop control over the motor, this project includes a LCD module to display the speeds live-time, an encoder/knob used to control the speed of the motor without the terminal, and IR beam sensors to check whether any insects have fallen off the treadmill.

From update 1.0.1, new functionalities have been added to the original functions stated above. In 1.0.1, three additional buttons have been included in order to allow the user a more headless setup (i.e. the user can use the treadmill without logging into the Raspberry Pi). The first button allows the user to start and stop the main script. The second button allows the user to save the current speed the treadmill is at as a "preset speed," which can be used in conjuction with the third button. The third button allows the user to perform experiments with the treadmill. Upon clicking the button, the treadmill ramps up to the saved preset speed and maintains that speed until the user presses the button again, which stops the experiment. Data about the treadmill speeds and experiment times are automatically saved to a .csv file. In addition, when the user presses the third button, the Raspberry Pi triggers a GPIO pin, which can be used to trigger an external camera.

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

The `SpiderTreadmill` repository includes several useful scripts. Within the `Hardware_Testing_Scripts` directory, there are various scripts used to test different hardware to verify they are working properly. For example, `single-tb9051ftg-motor-driver-rpi` includes an example script to test the motor driver and the motor conditions. Because there are some legacy components that are not used within the current iteration of the treadmill, `encoder_knob_test.py, IR_break_beam_test.py, LCD_module_test.py, button_test.py` and `motor_test.py` are the modules you should take a closer look at.

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
* Since update 1.0.1, running `main.py` will not automatically run the script; rather, the script is now running in an "idle" mode when executing the command `python main.py`, where the main loop (with all the features listed above) will only run after pressing the first button, which starts/stops the main script.
* Since update 1.0.1, there are two other major buttons that allow the user to take experiments with the treadmill (one to save a specific speed and one to start/stop an experiment). Details regarding how to use these buttons and their features will be included in a section below.

## Using the buttons (Headless operation)

Since update 1.0.1, three new buttons have been incorporated with the treadmill. There are two major purposes for including these buttons: 1) allow the user to use the treadmill without needing to ssh into the Raspberry Pi, 2) allow the user to perform experiments with the treadmill. 

### Button 1

The first button allows the user to use the treadmill without needing to ssh into the Raspberry Pi. By default, when the Raspberry Pi is powered, it will be running in an "idle" mode. The first button, when pressed, will start the main loop in `main.py` and will allow the user to change the motor speed values via the encoder knob. Pressing this button again will shut the main script down. 

### Button 2 and 3

The second and third button are aimed to be used together and will allow the user to perform experiments with the treadmill. Suppose the user tunes the treadmill to a desired speed using the encoder knob, and they desire to perform experiments at this speed. The user can use the second button to save this speed. By pressing the second button, the Raspberry Pi saves the current desired speed on display as a "preset speed," and then slows the motor down to a stop.

In order to actually perform an experiment, button 3 can be used. Upon clicking button 3, the treadmill will speed up to the saved "preset speed" and maintain this speed until the button is clicked again. When button 3 is clicked to start the trial, the Raspberry Pi will automatically start saving data in the form of `[time_elapsed, desired_speed, actual_speed]` to a .csv file with a file name specified with the date and time of trial. This file is saved to directory called `data_logs` in the `motor_PID_package` directory. In addition, pressing this button will also trigger a GPIO pin, which can be used to start an external camera. 

### Possible steps to a trial

The following could be a series of steps the user takes to perform an experiment with the headless setup.

1. Power up the Raspberry Pi
2. Press the button 1 to start the main script
3. Tune the treadmill to the desired speed using the encoder knob
4. Press button 2 to save current desired speed as the preset speed for future trials (this button will also slow the treadmill to a halt)
5. Press button 3 to start a trial (this will speed the treadmill up to the preset speed and maintain that speed)
6. Press button 3 again when you want to stop the trial
7. Perform steps 3 - 6 for different speeds for each trial, or perform steps 5 - 6 for several trials with the same preset speed.
8. Press button 1 to exit the main script after all desired trials have been completed

NOTES:
* The Raspberry Pi will automatically exit the main script if the IR sensors are tripped or if the motor driver faults
* All data will be saved in the `data_logs` directory in files titled with the date and time of the trial
* The camera will be triggered to start on step 5

## Library reference

Most of the functionality of the treadmill, LCD, IR sensors, etc. are contained within the `*Class.py` scripts in  `motor_PID_package` directory. The code has been pretty well documented, so please refer to those directories regarding any of the functionalities of the main script.

## Version history

* 1.0.0 (2022-07-10): Original release.
* 1.0.1 (2022-07-18): Button updates incorporated.