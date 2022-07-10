# This scripts entails a class that has various functions which allow the user to implement PID control with
# a DC moter and encoder

# import required libraries
import time
from math import pi

class MotorPID(object):
    '''
    This class provides various functions that allow the user to control
    a DC motor via PID. Note that this class requires access to motor and
    encoder objects
    '''

    # instantiation function
    def __init__(self, motor, encoder):
        self.motor = motor          # obtain a motor object
        self.encoder = encoder      # obtain an encoder object
        self.err_prev = 0           # variable that stores the error from the previous iteration of PID function (used for the integral and derivative terms)
        self.err_sum = 0            # variable that stores the integral sum of the error for the integral term of the PID
        self.u_prev = 0             # variable that stores the previous control signal sent to the motor (used to generate new control signal)
        self.time_prev = time.perf_counter()        # variable that stores the previous time for the PID loop (used to calculate deltaT)

    # Create function to execute the PID controller
    def motorPID(self, desired_vel, meas_vel):

        # obtain the change in time since the last time this function has been called
        time_curr = time.perf_counter()
        deltaT = time_curr - self.time_prev

        # tuning constants
        # NOTE: from testing, it appears that having k_p as 0.1 as the only value works quite well (if using u_prev)
        # NOTE: from testing, k_p = 0.5, k_i = 0.5 works for classic PID (no use of u_prev in control signal)
        k_p = 0.1
        k_i = 0
        k_d = 0

        # NOTE: there is a check for 0 m/s as an input speed because the PID will actually
        #       never send a control signal of "0" and will waste energy sending a voltage
        #       that is not enough to actually power the motor
        if not (desired_vel == 0):
            # calculate the current error between the desired and measured motor speeds
            err = desired_vel - meas_vel

            # calculate the sum of the error for the integral term for the PID
            self.err_sum = self.err_sum + (1/2)*(err + self.err_prev)*deltaT

            # calculate the change in error for the derivative term for the PID
            deltaErr = err - self.err_prev
        else:
            # here, we set the errors and previous control signal to zero so that we send a command of u = 0
            err = 0
            self.err_sum = 0
            deltaErr = 0
            self.u_prev = 0

        # calculate the control signal
        u = k_p*err + k_i*self.err_sum + k_d*(deltaErr/deltaT) + self.u_prev

        # update required global variables for the next iteration of the loop
        self.err_prev = err
        self.u_prev = u
        self.time_prev = time.perf_counter()

        return u

    # Function used to maintain the motor velocity if the user has not changed the velocity
    def maintainMotorVelocity(self, speed_des):

        # Read in the current motor velocity
        curr_speed = self.encoder.calcMotorVelocity()

        # generate a control signal using the PID function
        control_sig = self.motorPID(speed_des, curr_speed)

        # send the control signal to the motor
        self.motor.setSpeed(control_sig)

        return control_sig, curr_speed

    # Function used to change the motor velocity when the user specifies a different speed
    def changeMotorVelocity(self, ramp_time, speed_des):

        # NOTE: built into this function is the ability to "ramp" from the current velocity
        #       to the desired velocity to provide smoother transitions between velocities
        #       that also minimize strain of sharp fluctuations of speed on the motor and
        #       the motor driver. This function is only called whenever there is a change in
        #       the desired velocity. Otherwise, the main thread will be running the
        #       maintainMotorVelocity() function

        # create variable that stores the time elapsed
        time_elapsed = 0

        # obtain the current starting velocity from the motor
        start_speed = self.encoder.calcMotorVelocity()

        # create variable that stores the current motor velocity
        curr_speed = start_speed

        # create a variable to store the speed to send to the PID loop
        ramp_vel = 0

        # determine the slope for the linear profile of the ramp signal
        slope = (speed_des - start_speed)/ramp_time

        # obtain the start time for the ramp signal
        start_time = time.perf_counter()

        # execute the ramp signal over the time_diff
        while (time_elapsed <= ramp_time):
            # calculate the ramp velocity to send to the PID loop
            ramp_vel = slope*time_elapsed + start_speed      # standard y = mx + b linear equation

            # send velocity to PID
            control_sig = self.motorPID(ramp_vel, curr_speed)

            # send the motor speed
            self.motor.setSpeed(control_sig)

            # clock the time elaspsed
            stop_time = time.perf_counter()
            time_elapsed = stop_time - start_time

            # obtain new speed for the motor
            curr_speed = self.encoder.calcMotorVelocity()

        user_changed_velocity = False
        print("Ramp completed")

        return control_sig, curr_speed, user_changed_velocity          # return final control signal and motor velocity and flag

    # function to convert speeds from RPM to m/s
    def RPMToMPS(self, rpm):
        mps = rpm*(pi/60.0)*(2/39.3701)
        return mps

    # function to convert speeds from m/s to RPM
    def MPSToRPM(self, mps):
        rpm = mps*(60/pi)/(2/39.3701)
        return rpm
