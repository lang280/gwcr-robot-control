"""
Purpose: Main Module for Robot Control System
Author: Jianjun Lang
Date: November 14, 2024
Version: v3.6
Additional Description:
Updates:
Version 3.6

Transitioned from using subprocess to multiprocessing.
Eliminated the use of package variables; parameters are now passed using function arguments.
"""
import multiprocessing
import random
import os
import signal
import sys

# import run functions
from .http_server.http_server import run_http_server
from .drivers.picamera_driver import run_picamera_driver
from .websockets_server import run_websockets_server
from .drivers.gpio_driver import run_gpio_driver

def main():
    '''parameters'''
    mainPath  = os.path.dirname(os.path.abspath(__file__))
    httpPath = mainPath + "/http_server"

    # server ports
    httpPort = 80
    websocketPort = random.randint(49152, 65535)

    # driver ports
    cameraPort = random.randint(49152, 65535)
    leftMotor_port = random.randint(49152, 65535)
    rightMotor_port = random.randint(49152, 65535)
    suctionMotor_port = random.randint(49152, 65535)
    indicatorLED_port = random.randint(49152, 65535)
    driverPort_tuple = (leftMotor_port, rightMotor_port, suctionMotor_port, indicatorLED_port)

    # GPIO pins
    GPIOpin_pwm_left = 23
    GPIOpin_pwm_right = 18
    GPIOpin_pwm_suction = 12 
    GPIOpin_LED_indicator = 5

    GPIOpin_direction_right = 17
    GPIOpin_direction_left = 22
    pin_tuple = (GPIOpin_pwm_left, GPIOpin_pwm_right, GPIOpin_pwm_suction, GPIOpin_LED_indicator, GPIOpin_direction_right, GPIOpin_direction_left)

    # PWM Frequency (Hz)
    PWMfreq_motion = 10000
    PWMfreq_suction = 18000
    pwmFreq_tuple = (PWMfreq_motion, PWMfreq_suction)
    

    # log print
    http_logPrint = 1
    websocket_logPrint = 1
    gpioDriver_logPrint = 1

    '''start and manage the child processes'''

    # processes
    processes = []

    # SIGINT handler
    def signalHandler(sig, frame):
        # terminate child processes
        for process in processes:
            process.terminate()
        
        # wait processes to end
        for process in processes:
            process.join()
        
        print("\nAll Processes Ended")
        
        sys.exit(0)
    
    
    # Process Parameters
    processParameters = [
        (run_http_server, (httpPort, httpPath, http_logPrint, websocketPort, "localhost", cameraPort, b"<END_OF_FILE>",)),
        (run_picamera_driver, (cameraPort,)),
        (run_websockets_server, (websocketPort, leftMotor_port, rightMotor_port, suctionMotor_port, websocket_logPrint)),
        (run_gpio_driver, (driverPort_tuple, pin_tuple, pwmFreq_tuple, gpioDriver_logPrint)),
    ]

    

    # ignore SIGINT which inherit by child processes
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # start processes
    for processParameter in processParameters:
        process = multiprocessing.Process(target=processParameter[0], args=processParameter[1])
        processes.append(process)
        process.start()

    # assign handler to SIGINT
    signal.signal(signal.SIGINT, signalHandler)

    print("All Processes Started")

    for process in processes:
        process.join()

main()
