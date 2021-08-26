import pygame
from pygame.locals import *
import math
import time
import random
import os
import json

sourceFileDir = os.path.dirname(os.path.abspath(__file__))

flags =  DOUBLEBUF

pygame.init()
clock = pygame.time.Clock()

displayWidth = 1200
displayHeight = 750
centerX = displayWidth/2
centerY = displayHeight/2
tileSize = 50

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), flags)
backgroundImage = pygame.image.load(os.path.join(sourceFileDir,"background.png")).convert()

movingUp = False
movingDown = False
movingLeft = False
movingRight = False

enemies = []
tiles = []
projectiles = []

font = pygame.font.SysFont('Comic Sans MS', 50)


def displayText(text):
    surface = font.render(text, True, (0, 0, 0))
    gameDisplay.blit(surface, (random.randint(1, 100), random.randint(1, 100)))


class Player():
    def __init__(self, x, y):
        self.velocityX = 0
        self.velocityY = 0
        self.inventory = []
        self.image = pygame.image.load(os.path.join(sourceFileDir,"character.png"))
        self.speed = 5
        self.rect = pygame.Rect(x, y, 60, 63)
        print(self.rect)
        self.angle = 0
        self.movingUp = False
        self.movingDown = False
        self.movingRight = False
        self.movingLeft = False
        self.health = 100
    
    def update(self):
        if self.velocityY > 0:
            self.velocityY -= 1
        if self.velocityY < 0:
            self.velocityY += 1
        if self.velocityX > 0:
            self.velocityX -= 1
        if self.velocityX < 0:
            self.velocityX += 1
        if self.movingUp and self.velocityY >= -self.speed:
            self.velocityY -= 2
        if self.movingDown and self.velocityY <= self.speed:
            self.velocityY += 2
        if self.movingRight and player.velocityX <= self.speed:
            self.velocityX += 2
        if self.movingLeft and self.velocityX >= -self.speed:
            self.velocityX -= 2
        
        self.rect.move_ip(self.velocityX, self.velocityY)

        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocityX > 0:
                    self.rect.right = tile.rect.left
                if self.velocityX < 0:
                    self.rect.left = tile.rect.right

        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocityY > 0:
                    self.rect.bottom = tile.rect.top
                if self.velocityY < 0:
                    self.rect.top = tile.rect.bottom

        center = self.rect.center
        newImage = pygame.transform.rotate(self.image, self.angle)
        newRect = newImage.get_rect(center=(self.rect.centerx, self.rect.centery))
        gameDisplay.blit(newImage, newRect)
    
    def meleeAttack(self, angle, attackRange, damage):
        for enemy in enemies:
            if (enemy.rect.centerx - player.rect.centerx)**2 + (enemy.rect.centery - player.rect.centery)**2 < attackRange**2:
                enemy.health -= damage
                knockbackX = math.cos(math.radians(angle))
                knockbackY = -math.sin(math.radians(angle))
                enemy.velocityX = 20 * knockbackX
                enemy.velocityY = 20 * knockbackY

player = Player(500, 50)


class Projectile():
    def __init__(self, x, y, speed, angle):
        posX, posY = pygame.mouse.get_pos()
        self.angle = -math.radians(angle-360)
        self.image = pygame.transform.rotate(pygame.image.load(os.path.join(sourceFileDir,"projectile.png")), self.angle)
        self.rect = self.image.get_rect(center = (x, y))
        self.speed = speed
        self.distx = posX - x
        self.disty = posY - y
        self.angle = math.atan2(self.disty, self.distx)
        self.velocityx = self.speed * math.cos(self.angle)
        self.velocityy = self.speed * math.sin(self.angle)
        self.x = x + (self.velocityx * 2)
        self.y = y + (self.velocityy * 2)
        projectiles.append(self)
    def update(self):
        self.x += self.velocityx
        self.y += self.velocityy
        for tile in tiles:
            if tile.rect.left < self.rect.centerx < tile.rect.right and tile.rect.top < self.rect.centery < tile.rect.bottom:
                projectiles.remove(self)
        #gameDisplay.blit(self.image, (centerX - player.rect.width/2 + (self.rect.centerx - player.rect.x), centerY - player.rect.height/2 + (self.rect.centery - player.rect.y)))
        #pygame.draw.circle(gameDisplay, (90, 0, 0), (int(centerX - player.rect.width/2 + (self.rect.centerx - player.rect.x)), int(centerY - player.rect.height/2 + (self.rect.centery - player.rect.y))), 5)
        pygame.draw.circle(gameDisplay, (90,0,0), (int(self.x), int(self.y)), 5)


class Tile():
    def __init__(self, x, y):
        self.image = pygame.image.load(os.path.join(sourceFileDir,"tile.png"))
        self.rect = pygame.Rect(x, y, tileSize, tileSize)
        self.x = x
        self.y = y
        tiles.append(self)
    def update(self):
        gameDisplay.blit(self.image, (self.x, self.y))

    '''displayX = centerX + (self. rect.x - player.rect.x)
    displayY = centerY + (self.rect.y - player.rect.x)
    if displayWidth > displayX > 0 and displayHeight > displayY > 0:
        gameDisplay.blit(self.image, (displayX, displayY))'''

class Enemy():
    def __init__(self, x, y):
        self.velocityX = 0
        self.velocityY = 0
        self.image = pygame.image.load(os.path.join(sourceFileDir,"enemy.png"))
        self.speed = 2
        self.rect = pygame.Rect(x, y, 36, 45)
        self.angle = 0
        self.moveMode = "idle"
        self.idleTimer = 0
        self.health = 50
        self.directionX = 0
        self.directionY = 0
        enemies.append(self)
    def update(self):
        if self.velocityY > 0:
            self.velocityY -= 1
        if self.velocityY < 0:
            self.velocityY += 1
        if self.velocityX > 0:
            self.velocityX -= 1
        if self.velocityX < 0:
            self.velocityX += 1
        if pygame.time.get_ticks() >= self.idleTimer:
            self.idleTimer += 3000
            if self.directionX == 0 and self.directionY == 0:
                self.directionX = random.randint(-1, 1)
                self.directionY = random.randint(-1, 1)
            else:
                self.directionX = 0
                self.directionY = 0
        if self.velocityY < self.speed and self.directionY == 1:
            self.velocityY += 1
        if self.velocityY > -self.speed and self.directionX == -1:
            self.velocityY -= 1
        if self.velocityX < self.speed and self.directionX == 1:
            self.velocityX += 1
        if self.velocityX > -self.speed and self.directionX == -1:
            self.velocityX -= 1

        self.rect.x += self.velocityX
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocityX > 0:
                    self.rect.right = tile.rect.left
                if self.velocityX < 0:
                    self.rect.left = tile.rect.right
        self.rect.y += self.velocityY
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocityY > 0:
                    self.rect.bottom = tile.rect.top
                if self.velocityY < 0:
                    self.rect.top = tile.rect.bottom
        self.angle = -math.atan2(self.velocityY, self.velocityX) * 57.3
        newImage = pygame.transform.rotate(self.image, self.angle)
        gameDisplay.blit(newImage, (self.rect.x, self.rect.y))

tile = Tile(500, 500)
tile2 = Tile(200, 500)
tile3 = Tile(250, 550)
enemy = Enemy(300, 400)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.movingUp = True
                displayText("dask")

            if event.key == pygame.K_s:
                player.movingDown = True
            if event.key == pygame.K_d:
                player.movingRight = True
            if event.key == pygame.K_a:
                player.movingLeft = True
            if event.key == pygame.K_LSHIFT:
                player.speed *= 2
            if event.key == pygame.K_p:
                Projectile(player.rect.centerx, player.rect.centery, 10, player.angle)
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.meleeAttack(player.angle, 100, 2)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                player.movingUp = False
            if event.key == pygame.K_s:
                player.movingDown = False
            if event.key == pygame.K_d:
                player.movingRight = False
            if event.key == pygame.K_a:
                player.movingLeft = False
            if event.key == pygame.K_LSHIFT:
                player.speed /= 2
    mouseX, mouseY = pygame.mouse.get_pos()
    player.angle = 360 - math.degrees(math.atan2(mouseY - player.rect.centery, mouseX - player.rect.centerx))

    gameDisplay.blit(backgroundImage, (0, 0))
    player.update()
    for tile in tiles:
        tile.update()
    for enemy in enemies:
        enemy.update()
    for projectile in projectiles:
        projectile.update()
    pygame.display.update()
    #print(clock.get_fps())



    clock.tick(60)

pygame.quit()
quit()
