from core.game.world.tile import Tile
class Layer(Tile):
    def __init__(self, system, camera):
        super().__init__(system, camera)
        self.collision_tiles = set()

    def register(self, name, grid_x, grid_y, collidable=False):
        super().register(name, grid_x, grid_y)
        if collidable:
            self.collision_tiles.add(name)

    def is_collidable(self, tile_name):
        return tile_name in self.collision_tiles