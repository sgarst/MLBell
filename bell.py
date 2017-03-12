#!/usr/bin/env python
# bell.py - Function to move bell, play audio and blink lights (threaded)

import time
from threading import Thread
import pygame
import pigpio

def blinkLight():
    led = pigpio.pi() # Connect to local Pi.
    start = time.time()
    while (time.time() - start) < 5: # Spin for 5 seconds.
	led.write(25, 0) # set Pi's gpio 25 low
	time.sleep(0.5)
	led.write(25, 1) # set Pi's gpio 25 HIGH
	time.sleep(0.5)

    led.write(25, 0) # Make sure it is OFF!
    led.stop

def playAudio():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/mlb/MLBell/WAV/bell_1_5s.wav")
    pygame.mixer.music.set_volume(0.9)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def moveBell():
    SERVO = 17     # Servo connected to gpio 17.
    DIR   = 1
    PW    = 1500
    SPEED = 50

    pi = pigpio.pi() # Connect to local Pi.
    pi.set_mode(SERVO, pigpio.OUTPUT) # Set gpio as an output.
    start = time.time()
    while (time.time() - start) < 5: # Spin for 5 seconds.
        pi.set_servo_pulsewidth(SERVO, PW)
        PW += (DIR * SPEED)
        if (PW < 1500) or (PW > 1900): # Bounce back at safe limits.
             DIR = - DIR
        time.sleep(0.05)

    pi.set_servo_pulsewidth(SERVO, 0) # Switch servo pulses off.
    pi.stop()

def bell():
    a = Thread(target=playAudio)
    a.start()
    b = Thread(target=moveBell)
    b.start()
    c = Thread(target=blinkLight)
    c.start()


    if (not a.isAlive()):
            a.join()
    if (not b.isAlive()):
            b.join()
    if (not c.isAlive()):
            c.join()

