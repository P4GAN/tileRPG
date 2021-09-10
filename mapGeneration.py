import random

class Room:
    def __init__(self, x, y, width, height):
        self.x = x #center x and center y
        self.y = y
        self.width = width
        self.height = height
        self.roomCoordinates = []
        for posX in range(x - int(width / 2), x + 1 + int(width / 2)):
            for posY in range(y - int(height / 2), y + 1 + int(height / 2)):
                self.roomCoordinates.append((posX, posY))


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

    for y in range(min(room1.y, room2.y), max(room1.y, room2.y)):
        positions.append((room1.x, y))

    for x in range(min(room1.x, room2.x), max(room1.x, room2.x)):
        positions.append((x, room2.y))

    return positions


def generateMap(width, height, maxRooms, minSize, maxSize):
    rooms = []
    map = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append("w")
        map.append(row)

    for i in range(maxRooms):
        roomWidth = random.randint(minSize, maxSize)
        roomHeight = random.randint(minSize, maxSize)
        x = random.randint(int(roomWidth / 2), width - 1 - int(roomWidth / 2))
        y = random.randint(int(roomHeight / 2), height - 1 - int(roomHeight / 2))
        room = Room(x, y, roomWidth, roomHeight)

        roomCollision = False
        for otherRoom in rooms:
            roomCollision = rectCollisionCheck(otherRoom, room)
            if roomCollision:
                break
        
        if not roomCollision:
            for position in room.roomCoordinates:
                map[position[1]][position[0]] = " "
            
            if len(rooms) > 0:
                for position in createCorridors(room, rooms[-1]):
                    map[position[1]][position[0]] = " "

            rooms.append(room)

    return map, rooms

testMap, roomList = generateMap(100, 50, 15, 6, 12)
for row in testMap:
    print("".join(row))

for room in roomList:
    print(room.x, room.y, room.width, room.height)

