    Tile(tileSize * mapWidth + displayHeight / 4 - tileSize / 2, tileSize * mapHeight / 2, pygame.image.load(os.path.join(sourceFileDir, "verticalBorder.png")), 600, 3720, True)
    Tile(tileSize * mapHeight / 2, -displayHeight / 4, pygame.image.load(os.path.join(sourceFileDir, "horizontalBorder.png")), 4800, 420, True)
    Tile(tileSize * mapHeight / 2, tileSize * mapHeight + displayHeight / 4 - tileSize / 2, pygame.image.load(os.path.join(sourceFileDir, "horizontalBorder.png")), 4800, 420, True)
