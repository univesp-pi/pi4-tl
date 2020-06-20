import RPi.GPIO as gpio
import time
 
gpio.setmode(gpio.BCM)
 
gpio.setup(23, gpio.IN, pull_up_down = gpio.PUD_DOWN)
 

gpio.cleanup()
exit()