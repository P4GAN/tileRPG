import pygame
from pygame.locals import *
import math
import time
import random
import os
import json

from mapGeneration import *

sourceFileDir = os.path.dirname(os.path.abspath(__file__)) + "/sprites/"

flags =  DOUBLEBUF

pygame.init()
clock = pygame.time.Clock()

keys = pygame.key.get_pressed()

displayWidth = 1200
displayHeight = 840
centerX = displayWidth/2
centerY = displayHeight/2
tileSize = 30

mapWidth = 60 #number of tiles
mapHeight = 48 

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), flags)

backgroundSurface = pygame.Surface((mapWidth * tileSize, mapHeight * tileSize))

backgroundImage = pygame.image.load(os.path.join(sourceFileDir, "floor.png")).convert()
backgroundWidth = backgroundImage.get_width()
backgroundHeight = backgroundImage.get_height()

for x in range(0, mapWidth * tileSize, backgroundWidth):
    for y in range(0, mapHeight * tileSize, backgroundHeight):
        backgroundSurface.blit(backgroundImage, (x, y))

backgroundSurface = backgroundSurface.convert()
backgroundSurfaceWidth = backgroundSurface.get_width()
backgroundSurfaceHeight = backgroundSurface.get_height()

enemies = []
tiles = []
projectiles = []

font = pygame.font.SysFont('Comic Sans MS', 50)

friction = 0.5
acceleration = 1


def displayText(text, x, y):
    surface = font.render(text, True, (0, 0, 0))
    gameDisplay.blit(surface, (x, y))

def pointCollisionCheck(pointObject, rectObject):
    return rectObject.x - rectObject.width/2 < pointObject.x < rectObject.x + rectObject.width/2 and rectObject.y - rectObject.height/2 < pointObject.y < rectObject.y + rectObject.height/2

def rectCollisionCheck(object1, object2):
    object1.left = object1.x - object1.width/2
    object1.right = object1.x + object1.width/2
    object1.top = object1.y + object1.height/2
    object1.bottom = object1.y - object1.height/2

    object2.left = object2.x - object2.width/2
    object2.right = object2.x + object2.width/2
    object2.top = object2.y + object2.height/2
    object2.bottom = object2.y - object2.height/2

    return (object1.left < object2.right and object1.right > object2.left and object1.top > object2.bottom and object1.bottom < object2.top) 

class Player():
    def __init__(self, x, y):
        self.velocityX = 0
        self.velocityY = 0
        self.inventory = []
        self.image = pygame.image.load(os.path.join(sourceFileDir, "character.png"))
        self.speed = 10
        self.x = x #center x and y
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.angle = 0
        self.health = 100
    
    def updatePhysics(self):
        if self.velocityY > 0:
            self.velocityY -= friction
            self.velocityY = max(0, self.velocityY)
        elif self.velocityY < 0:
            self.velocityY += friction
            self.velocityY = min(0, self.velocityY)
        if self.velocityX > 0:
            self.velocityX -= friction
            self.velocityX = max(0, self.velocityX)
        elif self.velocityX < 0:
            self.velocityX += friction
            self.velocityX = min(0, self.velocityX)

        if self.velocityY > -self.speed and (keys[pygame.K_UP] or keys[pygame.K_w]):
            self.velocityY -= acceleration
        if self.velocityY < self.speed and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
            self.velocityY += acceleration
        if self.velocityX < self.speed and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.velocityX += acceleration
        if self.velocityX > -self.speed and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
            self.velocityX -= acceleration

        '''for tile in tiles:
            if self.rect.colliderect(tile.rect):
                self.velocityX = 0
                self.velocityY = -20''' # boost pad, if set both to 0, becomes sand

        self.x += self.velocityX #move x, then check for collisions horizontally, then move y and check for collisions vertically

        for tile in tiles:
            if tile.enabled:
                if rectCollisionCheck(self, tile):
                    if self.velocityX > 0:
                        self.x = tile.x - self.width/2 - tile.width/2
                    if self.velocityX < 0:
                        self.x = tile.x + self.width/2 + tile.width/2

        self.y += self.velocityY

        for tile in tiles:
            if tile.enabled:
                if rectCollisionCheck(self, tile):
                    if self.velocityY > 0:
                        self.y = tile.y - self.height/2 - tile.height/2
                    if self.velocityY < 0:
                        self.y = tile.y + self.height/2 + tile.height/2

    def update(self):
        self.updatePhysics()

        newImage = pygame.transform.rotate(self.image, self.angle)
        newRect = newImage.get_rect(center = (centerX, centerY))
        gameDisplay.blit(newImage, newRect)
    
    def meleeAttack(self, angle, attackRange, damage):
        for enemy in enemies:
            if (enemy.x - player.x) ** 2 + (enemy.y - player.y) ** 2 < attackRange ** 2:
                enemy.health -= damage
                knockbackX = math.cos(math.radians(angle))
                knockbackY = -math.sin(math.radians(angle))
                enemy.velocityX = 20 * knockbackX
                enemy.velocityY = 20 * knockbackY

    def takeDamage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0

class Projectile():
    def __init__(self, x, y, directionX, directionY, speed):

        magnitude = math.sqrt(directionX ** 2 + directionY ** 2)
        directionX = directionX / magnitude
        directionY = directionY / magnitude

        self.angle = -math.atan2(directionY, directionX)
        self.image = pygame.transform.rotate(pygame.image.load(os.path.join(sourceFileDir,"projectile.png")), math.degrees(self.angle))
        self.speed = speed
        self.velocityX = self.speed * directionX
        self.velocityY = self.speed * directionY
        self.x = x #center x and y
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        projectiles.append(self)

    def update(self):
        displayX = centerX + (self.x - player.x) - self.width/2
        displayY = centerY + (self.y - player.y) - self.height/2
        if not (displayWidth + 100 > displayX > -100 and displayHeight + 100 > displayY > -100):
            projectiles.remove(self)
            del self
            return
        self.x += self.velocityX
        self.y += self.velocityY
        for tile in tiles:
            if pointCollisionCheck(self, tile):
                projectiles.remove(self)
                del self
                return 
        for enemy in enemies:
            if pointCollisionCheck(self, enemy):
                projectiles.remove(self)
                enemy.takeDamage(10)
                del self
                return 
        #gameDisplay.blit(self.image, (centerX - player.rect.width/2 + (self.rect.centerx - player.rect.x), centerY - player.rect.height/2 + (self.rect.centery - player.rect.y)))
        #pygame.draw.circle(gameDisplay, (90, 0, 0), (int(centerX - player.rect.width/2 + (self.rect.centerx - player.rect.x)), int(centerY - player.rect.height/2 + (self.rect.centery - player.rect.y))), 5)
        gameDisplay.blit(self.image, (displayX, displayY))


class Tile():
    def __init__(self, x, y, image, width = tileSize, height = tileSize, border = False):
        self.image = pygame.image.load(os.path.join(sourceFileDir, image + ".png"))
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border = border
        self.enabled = False
        tiles.append(self)
    def update(self):
        self.enabled = False
        displayX = centerX + (self.x - player.x) - self.width/2
        displayY = centerY + (self.y - player.y) - self.height/2
        if self.border or (displayWidth + 100 > displayX > -100 and displayHeight + 100 > displayY > -100):
            self.enabled = True
            gameDisplay.blit(self.image, (displayX, displayY))


class Enemy():
    def __init__(self, x, y):
        self.image = pygame.image.load(os.path.join(sourceFileDir,"enemy.png"))
        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocityX = 0
        self.velocityY = 0
        self.speed = 3
        self.angle = 0
        self.moveMode = "idle"
        self.idleTimer = 0
        self.health = 50
        self.directionX = 0
        self.directionY = 0
        enemies.append(self)

    def updatePhysics(self):
        if self.velocityY > 0:
            self.velocityY -= friction
            self.velocityY = max(0, self.velocityY)
        elif self.velocityY < 0:
            self.velocityY += friction
            self.velocityY = min(0, self.velocityY)
        if self.velocityX > 0:
            self.velocityX -= friction
            self.velocityX = max(0, self.velocityX)
        elif self.velocityX < 0:
            self.velocityX += friction
            self.velocityX = min(0, self.velocityX)

        if -self.speed < self.velocityX < self.speed and -self.speed < self.velocityY < self.speed:
            self.velocityX += self.directionX * acceleration
            self.velocityY += self.directionY * acceleration

        self.x += self.velocityX #move x, then check for collisions horizontally, then move y and check for collisions vertically

        for tile in tiles:
            if tile.enabled:    
                if rectCollisionCheck(self, tile):
                    if self.velocityX > 0:
                        self.x = tile.x - self.width/2 - tile.width/2
                    if self.velocityX < 0:
                        self.x = tile.x + self.width/2 + tile.width/2

        self.y += self.velocityY

        for tile in tiles:
            if tile.enabled:    
                if rectCollisionCheck(self, tile):
                    if self.velocityY > 0:
                        self.y = tile.y - self.height/2 - tile.height/2
                    if self.velocityY < 0:
                        self.y = tile.y + self.height/2 + tile.height/2

        if rectCollisionCheck(self, player):
            player.takeDamage(10)

    def update(self):
        displayX = centerX + (self.x - player.x) - self.width/2
        displayY = centerY + (self.y - player.y) - self.height/2
        if displayWidth + 100 > displayX > -100 and displayHeight + 100 > displayY > -100:
            self.updatePhysics()

            '''if pygame.time.get_ticks() >= self.idleTimer:
                self.idleTimer += 3000
                if self.directionX == 0 and self.directionY == 0:
                    self.directionX = random.randint(-1, 1)
                    self.directionY = random.randint(-1, 1)
                else:
                    self.directionX = 0
                    self.directionY = 0'''

            magnitude = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
            self.directionX = (player.x - self.x) / magnitude
            self.directionY = (player.y - self.y) / magnitude

            self.angle = -math.degrees(math.atan2(self.velocityY, self.velocityX))
            newImage = pygame.transform.rotate(self.image, self.angle)
            gameDisplay.blit(newImage, (displayX, displayY))

    def takeDamage(self, damage):
        self.health -= damage
        if self.health <= 0:
            enemies.remove(self)
            del self 
            return

map = generateMap(60, 48, 10, 6, 16)

for y, row in enumerate(map):
    posY = y * 30
    for x, char in enumerate(row):
        posX = x * 30
        if char == "W":
            Tile(posX, posY, "wall")
        if char == "C":
            Tile(posX, posY, "crate")        
        if char == "S":
            player = Player(posX, posY)
        if char == "E":
            Enemy(posX, posY)

Tile(-300, tileSize * mapHeight / 2, "verticalBorder", 600, 2280, True)
Tile(tileSize * mapWidth + 285, tileSize * mapHeight / 2, "verticalBorder", 600, 2280, True)
Tile(tileSize * mapHeight / 2, -210, "horizontalBorder", 2400, 420, True)
Tile(tileSize * mapHeight / 2, tileSize * mapHeight + 195, "horizontalBorder", 2400, 420, True)


while True:
    keys = pygame.key.get_pressed()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                player.speed *= 2
            if event.key == pygame.K_p:
                Projectile(player.x, player.y, mouseX - centerX, mouseY - centerY, 10)
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.meleeAttack(player.angle, 100, 2)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                player.speed /= 2
    mouseX, mouseY = pygame.mouse.get_pos()
    player.angle = math.degrees(math.atan2(-(mouseY - centerY), mouseX - centerX))

    displayX = centerX - player.x
    displayY = centerY - player.y
    gameDisplay.blit(backgroundSurface, (displayX, displayY))

    player.update()
    for tile in tiles:
        tile.update()
    for enemy in enemies:
        enemy.update()
    for projectile in projectiles:
        projectile.update()

    displayText("health: " + str(max(player.health, 0)), 50, 50)


    pygame.display.update()


    #print(clock.get_fps())


    clock.tick(60)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    displayText("You have died, close the program", 400, 450)
    pygame.display.update()



    clock.tick(60)


pygame.quit()
quit()
