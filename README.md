# SpiderTreadmill

Version: 1.0.1<br>
Release Date: 2022-07-18<br>
[https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill](https://github.com/Animal-Inspired-Motion-And-Robotics-Lab/SpiderTreadmill)

## Summary

The purpose of this project is to develop a treadmill that will be used for insects. This GitHub repository contains various scripts that pertain to the development of the PID controller for a DC brushless motor provided by Pololu via this [link](https://www.pololu.com/product/4842), which will ultimately run the treadmill. The motor is controlled via a PID loop using a magnetic-based hall effect senson on the end of the motor. In addition to closed loop control over the motor, this project includes a LCD module to display the speeds live-time, an encoder/knob used to control the speed of the motor without the terminal, and IR beam sensors to check whether any insects have fallen off the treadmill.

From update 1.0.1, new functionalities have been added to the original functions stated above. In 1.0.1, three additional buttons have been included in order to allow the user a more headless setup (i.e. the user can use the treadmill without logging into the Raspberry Pi). The first button allows the user to start and stop the main script. The second button allows the user to save the current speed the treadmill is at as a "preset speed," which can be used in conjuction with the third button. The third button allows the user to perform experiments with the treadmill. Upon clicking the button, the treadmill ramps up to the saved preset speed and maintains that speed until the user presses the button again, which stops the experiment. Data about the treadmill speeds and experiment times are automatically saved to a .csv file. In addition, when the user presses the third button, the Raspberry Pi triggers a GPIO pin, which can be used to trigger an external camera.

## Getting Started

### Connecting to the Raspberry Pi

This project is currently using a Raspberry Pi Zero 2 W in headless mode. Because the Raspberry Pi is running in a headless configuration, it is necessary to SSH into the Raspberry Pi due to the fact there is no HDMI monitor available to login to the Raspberry Pi. There are various programs that allow you to access the Raspberry Pi via SSH, which will be discussed below. 

In addition to the software used to SSH into the Raspberry Pi, it is also necessary to determine the IP address given to the Raspberry Pi when it connects to a network. A tutorial on how to scan your current network is available via this [link](https://www.pcwdld.com/how-to-scan-network-for-ip-addresses#wbounce-modal). 

Personally, I have found that using [Angry IP Scanner](https://angryip.org/) to work well for this task because scanning across you network IP with this software reveals the hostnames for the different devices, which can help you determine the IP address of the Raspberry Pi out of all the IP addresses connected to your router.

#### Network for the Raspberry Pi

For the AIM-RL lab, note that the Raspberry Pi is currently configured to automatically connect to the AIM-RL network. Therefore, in order to connect to the Raspberry Pi, it is necessary for you to connect to AIM-RL internet before attempting to SSH the Raspberry Pi. After scanning the AIM-RL network for the IP address the Raspberry Pi, follow the instructions below to determine how to SSH into the Pi with the IP address.

#### Password for the Raspberry Pi

For the Raspberry Pi connected to the treadmill, the following are the login credentials:

```
username: pi
password: spidertreadmill
```

The username is included when trying to SSH into the Pi, usually in the following form `pi@ip_address_of_the_pi`. The password will be prompted when attempting the SSH.

#### Linux OS

If you are running a Linux platform, SSH is directly available via the command prompt using the following command:

```
ssh pi@ip_address
```

where `ip_address` represents the IP address given to the Raspberry Pi from the router it is connected to.

#### Windows

Using SSH on Windows platforms is not as straightforward as using it on Linux, but there are third-party softwares that allow you to SSH into the Raspberry Pi. The following list are some options:

1. [PuTTY](https://www.putty.org/)
2. [Ubuntu on Windows](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-10#1-overview)
3. [SSH using a VS Code extension](https://code.visualstudio.com/docs/remote/ssh-tutorial)

As long as you have the IP address of the Raspberry Pi, using any of the above softwares should allow you connect to the Raspberry Pi via SSH.

#### Mac OS

Personally, I have not used Mac OS to SSH into the Raspberry Pi, but there are plenty of tutorials on how to use SSH with Mac OS online, such as this [link](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh/using-ssh-on-a-mac-or-linux).

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

### Current location of the SpiderTreadmill directory

If you are using the Raspberry Pi connected to the treadmill, there is a pre-built version of the `SpiderTreadmill` directory with all the neccessary libraries and dependencies already install. After logging into the Raspberry Pi, you should be automatically be directed to the `/home/pi` directory, which is the directory for the `pi` user. Within this directory, the `SpiderTreadmill` directory is located in the `Documents` directory, so the following commands will lead you directly into the `SpiderTreadmill` directory.

```
cd Documents/SpiderTreadmill
```

### Important directories/files

The `SpiderTreadmill` repository includes several useful scripts. Within the `Hardware_Testing_Scripts` directory, there are various scripts used to test different hardware to verify they are working properly. For example, `single-tb9051ftg-motor-driver-rpi` includes an example script to test the motor driver and the motor conditions. Because there are some legacy components that are not used within the current iteration of the treadmill, `encoder_knob_test.py, IR_break_beam_test.py, LCD_module_test.py, button_test.py` and `motor_test.py` are the modules you should take a closer look at.

The `PID_Testing_Scripts` directory contains some scripts of the initial revision regarding the PID controller for the DC motor. Note that these scripts are extremely out-of-date compared to the scripots in the `motor_PID_package`, but it may be useful to take a look at these scripts if you want to see how the PID controller works in a chronological sense.

The actual code used to run the main loop to run the treadmill is located within the `motor_PID_package` directory, named as `main.py`. To run this code, just run the following lines when you are in the directory:

```
python main.py
```

This directory also contains various other scripts that contain classes which operate the individual equipment for the treadmill, such as classes for the motor encoder in `Encoder_Class.py` or classes for the LCD module in `LCD_Class.py`. Most of the functionality for the treadmill components are located within these scripts, so please take a look at them in order to gain an understanding regarding how every component works together. The following list is a brief description of the purpose of all these scripts:

* `Buttons_Class.py`: contains classes that describe the functionality of the push buttons
* `Data_Collection_Class.py`: contains a class that deals with the different functions regarding collecting data into a .csv file
* `Encoder_Class.py`: contains a class that contains functions which operate the encoder included on the DC motor
* `Exceptions.py`: contains classes that call up various exceptions for the main execution loop (i.e. when the motor driver faults, or something trips the IR sensor)
* `IR_Break_Beam_Class.py`: contains the class that deals with the functionality of the IR sensors
* `Knob_Class.py`: contains the class which works with the encoder knob that is used to adjust the speed of the treadmill
* `LCD_Class.py`: contains the class that deals with the functions of the LCD module
* `PID_Controller_Class.py`: contains the class that runs the PID controller for the DC motor
* `User_Input_Class.py`: contains the class that deals with various user input functions (i.e. threads that operate the terminal inputs, variables that store the desired speed, etc.)
* `main.py`: the main script for the treadmill

#### Miscellaneous files

The following are some extra files in the `motor_PID_package` that don't have direct influence of the functionality of the treadmill, but deal with the meta data of the package itself.

* `requirements.txt`: contains the dependencies for the `motor_PID_package`
* `setup.py`: the setup script for the `motor_PID_package` (this allows for the pip install functionality)
* `treadmill.service`: a file used to run `main.py` as a background service on the Raspberry Pi, which allows for the user to use the treadmill without even logging in

## Features of the main loop

As mentioned above, the treadmill can be run via the `main.py` module. The following are some of the features for the treadmill.

* When first running the code, it is necessary to ensure all the IR sensors are connected correctly, or else the code will trip a fault and immediately shut the treadmill down as a safety precaution. The IR break beam sensors are used to detect whether or not the insects running on the treadmills have fallen off or something of the sorts. 
* The user has two main options to control the speed of the treadmill: via the terminal or via the encoder knob. The terminal allows the user to input a speed from -1.5 m/s to 1.5 m/s inclusive. The encoder knob can be turned to manually change the speed of the motor and changes the desired speed in increments of 0.1 m/s or 0.01 m/s (which can be toggled via a button switch built into the encoder).
* The speed of the treadmill will be displayed in terms of m/s to the LCD module, which displays the desired and actual speeds of the motor. Whenever the encoder button has been toggled, the LCD will also display what increment has been chosen.
* There has been a "ramping" function built into the code to reduce stress on the motor driver, which means changing the velocity of the motor will not be instantaneous (a bit similar to a human treadmill).
* Since update 1.0.1, running `main.py` will not automatically run the script; rather, the script is now running in an "idle" mode when executing the command `python main.py`, where the main loop (with all the features listed above) will only run after pressing the first button, which starts/stops the main script.
* Since update 1.0.1, there are two other major buttons that allow the user to take experiments with the treadmill (one to save a specific speed and one to start/stop an experiment). Details regarding how to use these buttons and their features will be included in a section below.

## Using the buttons (Headless operation)

Since update 1.0.1, three new buttons have been incorporated with the treadmill. There are two major purposes for including these buttons: 1) allow the user to use the treadmill without needing to SSH into the Raspberry Pi, 2) allow the user to perform experiments with the treadmill. 

### Start/Stop button

The start/stop button allows the user to use the treadmill without needing to SSH into the Raspberry Pi. By default, when the Raspberry Pi is powered (as well as booted up), it will be running in an "idle" mode (for those interested, the idle mode is due to the `main.py` script running as a background service on the Raspberry Pi). This button, when pressed, will start the main loop in `main.py` and will allow the user to change the motor speed values via the encoder knob. Pressing this button again will shut the main script down. 

### Set speed button and trial button

The second and third buttons are aimed to be used together and will allow the user to perform experiments with the treadmill. Suppose the user tunes the treadmill to a desired speed using the encoder knob, and they desire to perform experiments at this speed. The user can use the set speed button to save this speed. By pressing the set speed button, the Raspberry Pi saves the current desired speed on display as a "preset speed," and then slows the motor down to a stop, which prepares the treadmill for any experiments.

In order to actually perform an experiment, the trial button can be used. Upon clicking the trial button, the treadmill will speed up to the saved "preset speed" and maintain this speed until the button is clicked again, which will then stop the trial and slow the motor down to a halt. When the set speed button is clicked to start the trial, the Raspberry Pi will automatically start saving data in the form of `[time_elapsed, desired_speed, actual_speed]` to a .csv file with a file name specified with the date and time of trial. This file is saved to directory called `data_logs` in the `motor_PID_package` directory. In addition, pressing this button will also trigger a GPIO pin, which can be used to start an external camera. 

### Possible steps to a trial

The following could be a series of steps the user takes to perform an experiment with the headless setup.

1. Power up the Raspberry Pi and wait for it to boot up (wait until the Raspberry Pi's LED stops flickering)
2. Press the start/stop button to start the main script
3. Tune the treadmill to the desired speed using the encoder knob
4. Press the set speed button to save current desired speed as the preset speed for future trials (this button will also slow the treadmill to a halt)
5. Press the trial button to start a trial (this will speed the treadmill up to the preset speed and maintain that speed)
6. Press the trial button again when you want to stop the trial (this will slow the motor down to a halt)
7. Perform steps 3 - 6 for different speeds for each trial, or perform steps 5 - 6 for several trials with the same preset speed.
8. Press the start/stop button to exit the main script after all desired trials have been completed

NOTES:
* The Raspberry Pi will automatically exit the main script if the IR sensors are tripped or if the motor driver faults
* All data will be saved in the `data_logs` directory in files titled with the date and time of the trial
* The camera will be triggered to start on step 5

## Library reference

Most of the functionality of the treadmill, LCD, IR sensors, etc. are contained within the `*Class.py` scripts in `motor_PID_package` directory. The code has been pretty well documented, so please refer to those directories regarding any of the functionalities of the main script.

## Version history

* 1.0.0 (2022-07-10): Original release.
* 1.0.1 (2022-07-18): Button updates incorporated.
