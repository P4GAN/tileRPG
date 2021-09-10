import random

class Room:
    def __init__(self, x, y, width, height):
        self.x = x #center x and center y
        self.y = y
        self.width = width
        self.height = height
        self.roomCoordinates = []
        self.wallCoordinates = []
        self.obstacleCoordinates = []
        self.roomType = ""

        '''for posX in range(x - int(width / 2) - 1, x + 2 + int(width / 2)):
            for posY in range(y - int(height / 2) - 1, y + 2 + int(height / 2)):
                self.wallCoordinates.append((posX, posY))'''

        for posX in range(x - int(width / 2), x + 1 + int(width / 2)):
            for posY in range(y - int(height / 2), y + 1 + int(height / 2)):
                self.roomCoordinates.append((posX, posY))

        numObstacles = int((self.width * self.height)/15)

        for i in range(numObstacles):
            self.obstacleCoordinates.append((random.randint(x - int(width / 2), x + int(width / 2)), random.randint(y - int(height / 2), y + int(height / 2))))

        


def rectCollisionCheck(object1, object2):
    object1.left = object1.x - int(object1.width/2)
    object1.right = object1.x + int(object1.width/2)
    object1.top = object1.y + int(object1.height/2)
    object1.bottom = object1.y - int(object1.height/2)

    object2.left = object2.x - int(object2.width/2)
    object2.right = object2.x + int(object2.width/2)
    object2.top = object2.y + int(object2.height/2)
    object2.bottom = object2.y - int(object2.height/2)

    return (object1.left <= object2.right and object1.right >= object2.left and object1.top >= object2.bottom and object1.bottom <= object2.top) 

def createCorridors(room1, room2):
    intersectionPoint = (room1.x, room2.y)
    positions = [intersectionPoint]

    wallPositions = []

    for y in range(min(room1.y, room2.y), max(room1.y, room2.y)):
        positions.append((room1.x, y))

    for x in range(min(room1.x, room2.x), max(room1.x, room2.x)):
        positions.append((x, room2.y))


    '''sortedXPositions = sorted([room1.x - int(room1.width/2), room1.x + int(room1.width/2), room2.x - int(room2.width/2), room2.x + int(room2.width/2)])
    sortedYPositions = sorted([room1.y - int(room1.height/2), room1.y + int(room1.height/2), room2.y - int(room2.height/2), room2.y + int(room2.height/2)])

    for y in range(sortedYPositions[1] + 1, sortedYPositions[2]):
        wallPositions.append((room1.x - 1, y))
        wallPositions.append((room1.x + 1, y))

    for x in range(sortedXPositions[1] + 1, sortedXPositions[2]):
        wallPositions.append((x, room2.y - 1))
        wallPositions.append((x, room2.y + 1))'''

    return positions, wallPositions


def generateMap(width, height, maxRooms, minSize, maxSize):
    rooms = []
    map = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append("W")
        map.append(row)

    for i in range(maxRooms):
        roomWidth = random.randint(minSize, maxSize)
        roomHeight = random.randint(minSize, maxSize)
        x = random.randint(int(roomWidth / 2) + 1, width - 2 - int(roomWidth / 2))
        y = random.randint(int(roomHeight / 2) + 1, height - 2 - int(roomHeight / 2))
        room = Room(x, y, roomWidth, roomHeight)

        roomCollision = False
        for otherRoom in rooms:
            roomCollision = rectCollisionCheck(otherRoom, room)
            if roomCollision:
                break
        
        if not roomCollision:
            rooms.append(room)

    for i in range(1, len(rooms)):
        positions, wallPositions = createCorridors(rooms[i], rooms[i - 1])
        for position in wallPositions:
            map[position[1]][position[0]] = "W"

    for room in rooms:
        for position in room.wallCoordinates:
            map[position[1]][position[0]] = "W"

        for position in room.roomCoordinates:
            map[position[1]][position[0]] = " "

        for position in room.obstacleCoordinates:
            map[position[1]][position[0]] = "C"

    for i in range(1, len(rooms)):
        positions, wallPositions = createCorridors(rooms[i], rooms[i - 1])
        for position in positions:
            map[position[1]][position[0]] = " "

    minRoomIndex = 0
    maxRoomIndex = len(rooms) - 1
    for i in range(len(rooms)):
        if rooms[i].x < rooms[minRoomIndex].x and rooms[i].y < rooms[minRoomIndex].y:
            minRoomIndex = i

        elif rooms[i].x > rooms[maxRoomIndex].x and rooms[i].y > rooms[maxRoomIndex].y:
            maxRoomIndex = i

    rooms[minRoomIndex].roomType = "start"
    rooms[maxRoomIndex].roomType = "finish"

    map[rooms[minRoomIndex].y][rooms[minRoomIndex].x] = "S"
    map[rooms[maxRoomIndex].y][rooms[maxRoomIndex].x] = "F"
    map[rooms[maxRoomIndex].y - 2][rooms[maxRoomIndex].x] = "B"

    for room in rooms:
        if room.roomType != "start" and room.roomType != "finish":
            numEnemies = int((room.width * room.height)/15)

            for i in range(numEnemies):
                enemyPosition = (random.randint(room.x - int(room.width / 2), room.x + int(room.width / 2)), random.randint(room.y - int(room.height / 2), room.y + int(room.height / 2)))
                map[enemyPosition[1]][enemyPosition[0]] = "E"




    return map

for y, row in enumerate(generateMap(60, 48, 10, 6, 12)):
    print("".join(row))