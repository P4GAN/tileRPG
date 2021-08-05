import pygame
from pygame.locals import *
import math
import time
import random
import os
import json

#importing modules


sourceFileDir = os.path.dirname(os.path.abspath(__file__)) + "/images/"
#get file directory

flags =  DOUBLEBUF

pygame.init()
clock = pygame.time.Clock()

displayWidth = 1000
displayHeight = 750


fishermanImage = pygame.image.load(os.path.join(sourceFileDir, "fisherman.png"))
backgroundImage = pygame.image.load(os.path.join(sourceFileDir, "background.png")).convert()
skyImage = pygame.image.load(os.path.join(sourceFileDir, "sky.png")).convert()
waterImage = pygame.image.load(os.path.join(sourceFileDir, "water.png"))

#displaying text

font = pygame.font.SysFont('Calibri', 15)

def displayText(text, x, y):
    surface = font.render(text, True, (0, 0, 0))
    gameDisplay.blit(surface, (x, y))


def gameLoop():

    with open(os.path.join(sourceFileDir, fileName), 'r') as jsonFile:
        data = json.load(jsonFile)
    


    #game loop, separate to main game loop
    while True:
        keys = pygame.key.get_pressed() 

        if keys[pygame.K_UP] or keys[pygame.K_w] :
            pass
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            pass

        mouseX, mouseY = pygame.mouse.get_pos()

        for event in pygame.event.get():
            #handling event and input

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass 

        #display screen 60 times per second
        pygame.display.update()

        clock.tick(60)



gameLoop()
