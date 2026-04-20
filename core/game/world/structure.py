class Structure:
    def __init__(self, name, tiles, collidable=True, entrances=None):

        self.name = name
        self.tiles = tiles
        self.collidable = collidable
        self.entrances = entrances or []