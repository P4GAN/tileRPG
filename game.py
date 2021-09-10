import pygame
from pygame.locals import *
import math
import time
import random
import os
import json

from mapGeneration import *

green = (0, 255, 0)
red = (255, 0, 0)

sourceFileDir = os.path.dirname(os.path.abspath(__file__)) + "/sprites/"

flags =  DOUBLEBUF

pygame.init()
clock = pygame.time.Clock()

keys = pygame.key.get_pressed()

displayWidth = 1200
displayHeight = 840
centerX = displayWidth/2
centerY = displayHeight/2
tileSize = 60

mapWidth = 60 #number of tiles
mapHeight = 48 

playerLevel = 1

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), flags)

backgroundSurface = pygame.Surface((mapWidth * tileSize, mapHeight * tileSize))

backgroundImage = pygame.image.load(os.path.join(sourceFileDir, "floor.png")).convert()
backgroundWidth = backgroundImage.get_width()
backgroundHeight = backgroundImage.get_height()

playerArrowImage = pygame.image.load(os.path.join(sourceFileDir, "playerArrow.png"))
enemyArrowImage = pygame.image.load(os.path.join(sourceFileDir, "enemyArrow.png"))
fireballImage = pygame.image.load(os.path.join(sourceFileDir, "fireball.png"))

zombieEnemyImage = pygame.image.load(os.path.join(sourceFileDir, "zombie.png"))
skeletonEnemyImage = pygame.image.load(os.path.join(sourceFileDir, "skeleton.png"))
wizardEnemyImage = pygame.image.load(os.path.join(sourceFileDir, "wizard.png"))

wallImage = pygame.image.load(os.path.join(sourceFileDir, "wall.png")).convert()
crateImage = pygame.image.load(os.path.join(sourceFileDir, "crate.png")).convert()

for x in range(0, mapWidth * tileSize, backgroundWidth):
    for y in range(0, mapHeight * tileSize, backgroundHeight):
        backgroundSurface.blit(backgroundImage, (x, y))

backgroundSurface = backgroundSurface.convert()
backgroundSurfaceWidth = backgroundSurface.get_width()
backgroundSurfaceHeight = backgroundSurface.get_height()

enemies = []
tiles = []
projectiles = []

font = pygame.font.SysFont('Comic Sans MS', 30)

friction = 0.5
acceleration = 1


def displayText(text, x, y):
    surface = font.render(text, True, (255, 255, 255))
    gameDisplay.blit(surface, (x, y))

def displayBar(x, y, color1, color2, score, maxScore, width, height):
    largeRect = pygame.Rect(x, y, width, height)
    smallRectWidth = width * (score / maxScore)
    smallRect = pygame.Rect(x, y, smallRectWidth, height)

    pygame.draw.rect(gameDisplay, color2, largeRect)
    pygame.draw.rect(gameDisplay, color1, smallRect)


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
        self.health = 50 * playerLevel
        self.maxHealth = 50 * playerLevel
        self.attackTimer = 0
        self.slashImage = pygame.image.load(os.path.join(sourceFileDir, "slash.png"))
    
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

        if portal:
            magnitude = math.sqrt((portal.y - self.y) ** 2 + (portal.x - self.x) ** 2)
            offsetX = (portal.x - self.x)/magnitude
            offsetY = (portal.y - self.y)/magnitude

            arrowPositionX = centerX + offsetX * 40
            arrowPositionY = centerY + offsetY * 40

            angle = math.degrees(math.atan2(-offsetY, offsetX))

            newImage = pygame.transform.rotate(pygame.image.load(os.path.join(sourceFileDir, "arrow.png")), angle)
            newRect = newImage.get_rect(center = (arrowPositionX, arrowPositionY))
            gameDisplay.blit(newImage, newRect)

        if pygame.time.get_ticks() <= self.attackTimer:
            mouseX, mouseY = pygame.mouse.get_pos()

            magnitude = math.sqrt((mouseY - centerY) ** 2 + (mouseX - centerX) ** 2)
            offsetX = (mouseX - centerX)/magnitude
            offsetY = (mouseY - centerY)/magnitude

            slashPositionX = centerX + offsetX * 30
            slashPositionY = centerY + offsetY * 30

            newImage = pygame.transform.rotate(pygame.image.load(os.path.join(sourceFileDir, "slash.png")), self.angle)
            newRect = newImage.get_rect(center = (slashPositionX, slashPositionY))
            gameDisplay.blit(newImage, newRect)

    def meleeAttack(self, angle, attackRange, damage):
        self.attackTimer = pygame.time.get_ticks() + 500
        for enemy in enemies:
            if (enemy.x - player.x) ** 2 + (enemy.y - player.y) ** 2 < attackRange ** 2:
                enemy.takeDamage(damage)
                knockbackX = math.cos(math.radians(angle))
                knockbackY = -math.sin(math.radians(angle))
                enemy.velocityX = 20 * knockbackX
                enemy.velocityY = 20 * knockbackY

    def takeDamage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0

class Projectile():
    def __init__(self, x, y, directionX, directionY, speed, image, owner):

        magnitude = math.sqrt(directionX ** 2 + directionY ** 2)
        directionX = directionX / magnitude
        directionY = directionY / magnitude

        self.angle = -math.atan2(directionY, directionX)
        self.image = pygame.transform.rotate(image, math.degrees(self.angle))
        self.speed = speed
        self.velocityX = self.speed * directionX
        self.velocityY = self.speed * directionY
        self.x = x #center x and y
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.owner = owner
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
        if self.owner == "player":
            for enemy in enemies:
                if pointCollisionCheck(self, enemy):
                    enemy.velocityX = self.velocityX
                    enemy.velocityY = self.velocityY
                    projectiles.remove(self)
                    enemy.takeDamage(10)
                    del self
                    return 
        elif self.owner == "enemy":
            if pointCollisionCheck(self, player):
                player.velocityX = self.velocityX
                player.velocityY = self.velocityY
                projectiles.remove(self)
                player.takeDamage(10)
                del self
                return 
        #gameDisplay.blit(self.image, (centerX - player.rect.width/2 + (self.rect.centerx - player.rect.x), centerY - player.rect.height/2 + (self.rect.centery - player.rect.y)))
        #pygame.draw.circle(gameDisplay, (90, 0, 0), (int(centerX - player.rect.width/2 + (self.rect.centerx - player.rect.x)), int(centerY - player.rect.height/2 + (self.rect.centery - player.rect.y))), 5)
        gameDisplay.blit(self.image, (displayX, displayY))


class Tile():
    def __init__(self, x, y, image, width = tileSize, height = tileSize, border = False):
        self.image = image
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

class Portal():
    def __init__(self, x, y):
        self.image = pygame.image.load(os.path.join(sourceFileDir, "portal.png"))
        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):

        displayX = centerX + (self.x - player.x) - self.width/2
        displayY = centerY + (self.y - player.y) - self.height/2

        gameDisplay.blit(self.image, (displayX, displayY))

class Enemy():
    def __init__(self, x, y, image, type):
        self.image = image
        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocityX = 0
        self.velocityY = 0
        self.speed = 3
        self.angle = 0
        self.type = type
        self.health = 30
        self.attackCooldown = 1500
        self.attackTimer = 0
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


    def update(self):
        displayX = centerX + (self.x - player.x) - self.width/2
        displayY = centerY + (self.y - player.y) - self.height/2
        if displayWidth + 100 > displayX > -100 and displayHeight + 100 > displayY > -100:
            self.updatePhysics()

            magnitude = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)

            if self.type == "zombie":
                self.directionX = (player.x - self.x) / magnitude
                self.directionY = (player.y - self.y) / magnitude

                if rectCollisionCheck(self, player):
                    if pygame.time.get_ticks() >= self.attackTimer:
                        knockbackX = math.cos(math.radians(self.angle))
                        knockbackY = -math.sin(math.radians(self.angle))
                        player.velocityX = 20 * knockbackX
                        player.velocityY = 20 * knockbackY
                        self.attackTimer = pygame.time.get_ticks() + self.attackCooldown
                        player.takeDamage(10)

            if self.type == "wizard" or self.type == "skeleton":
                if random.random() >= 0.9:
                    self.directionX = random.randint(-1, 1)
                    self.directionY = random.randint(-1, 1)
                if pygame.time.get_ticks() >= self.attackTimer:
                    self.attackTimer = pygame.time.get_ticks() + self.attackCooldown
                    directionX = (player.x - self.x) / magnitude
                    directionY = (player.y - self.y) / magnitude
                    if self.type == "wizard":
                        Projectile(self.x, self.y, directionX, directionY, 13, enemyArrowImage, "enemy")                    
                    if self.type == "skeleton":
                        Projectile(self.x, self.y, directionX, directionY, 13, fireballImage, "enemy")

            self.angle = -math.degrees(math.atan2(self.velocityY, self.velocityX))
            newImage = pygame.transform.rotate(self.image, self.angle)
            gameDisplay.blit(newImage, (displayX, displayY))

            displayBar(displayX, displayY + 20, green, red, self.health, 30, self.width, 5)

    def takeDamage(self, damage):
        self.health -= damage
        if self.health <= 0:
            enemies.remove(self)
            del self 
            return

def randomGeneration():

    gameMap = generateMap(60, 48, 10, 6, 16)

    for y, row in enumerate(gameMap):
        posY = y * tileSize
        for x, char in enumerate(row):
            posX = x * tileSize
            if char == "W":
                Tile(posX, posY, wallImage)
            if char == "C":
                Tile(posX, posY, crateImage)        
            if char == "S":
                player = Player(posX, posY)
            if char == "E":
                rand = random.random()
                if rand > 0.5:
                    enemyImage = zombieEnemyImage
                    enemyType = "zombie"
                elif rand < 0.25:
                    enemyImage = skeletonEnemyImage
                    enemyType = "skeleton"
                else:
                    enemyImage = wizardEnemyImage
                    enemyType = "wizard"
                Enemy(posX, posY, enemyImage, enemyType)

            if char == "F":
                portal = Portal(posX, posY)

    Tile(-displayWidth / 4, tileSize * mapHeight / 2, pygame.image.load(os.path.join(sourceFileDir, "verticalBorder.png")), 600, 3720, True)
    Tile(tileSize * mapWidth + displayHeight / 4 - tileSize / 2, tileSize * mapHeight / 2, pygame.image.load(os.path.join(sourceFileDir, "verticalBorder.png")), 600, 3720, True)
    Tile(tileSize * mapHeight / 2, -displayHeight / 4, pygame.image.load(os.path.join(sourceFileDir, "horizontalBorder.png")), 4800, 420, True)
    Tile(tileSize * mapHeight / 2, tileSize * mapHeight + displayHeight / 4 - tileSize / 2, pygame.image.load(os.path.join(sourceFileDir, "horizontalBorder.png")), 4800, 420, True)

    return player, portal

player, portal = randomGeneration()



while player.health > 0:
    keys = pygame.key.get_pressed()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                player.speed *= 2
            if event.key == pygame.K_SPACE:
                player.meleeAttack(player.angle, 100, 15)
        if event.type == pygame.MOUSEBUTTONDOWN:
            Projectile(player.x, player.y, mouseX - centerX, mouseY - centerY, 20, playerArrowImage, "player")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                player.speed /= 2
    mouseX, mouseY = pygame.mouse.get_pos()
    player.angle = math.degrees(math.atan2(-(mouseY - centerY), mouseX - centerX))

    displayX = centerX - player.x
    displayY = centerY - player.y
    gameDisplay.blit(backgroundSurface, (displayX, displayY))

    player.update()
    portal.update()

    if rectCollisionCheck(portal, player):
        playerLevel += 1
        tiles = []
        enemies = []
        projectiles = []
        player, portal = randomGeneration()

    for tile in tiles:
        tile.update()
    for enemy in enemies:
        enemy.update()
    for projectile in projectiles:
        projectile.update()

    displayText("Health", 25, 25)
    displayBar(25, 50, green, red, player.health, player.maxHealth, 200, 20)

    pygame.display.update()


    print(clock.get_fps())


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
