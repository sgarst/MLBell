#!/usr/bin/env python
# playsound.py - Function to play WAV audio file. 

import pygame

def playsound():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/mlb/MLBell/WAV/ThatsAllFolks.wav")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

if __name__ == "__main__":
    playsound();
