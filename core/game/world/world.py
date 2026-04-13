from core.game.entities.type import EntityType
from core.game.camera.camera import Camera
from core.game.world.tile import Tile
from core.game.entities.player.player import Player

class World():
    def __init__(self,system, load_data=None):
        self.system = system
        self.load_date = load_data
        self.camera = Camera(system.window.get_width(),system.window.get_height())
        self.tile = Tile(system,self.camera)
        self.player = Player(0,0,system,EntityType.PLAYER)

        self.tile.register("grass",0,0)
        self.tile.register("water",1,0)

    def tile_hash(self,x, y):
        n = x * 73856093 ^ y * 19349663
        n = (n << 13) ^ n
        return (n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff

    def generate_tiles(self, x, y):
        h = self.tile_hash(x, y) % 1000 / 1000.0

        if h < 0.3:
            return "grass"
        elif h < 0.8:
            return "water"
        else:
            return "grass"

    def update(self):
        self.camera.update(self.player)

    def draw(self):
        start_x,start_y,end_x,end_y = self.tile.get_visible()

        for tile_x in range(start_x,end_x):
            for tile_y in range(start_y,end_y):
                tile = self.generate_tiles(tile_x,tile_y)
                
                world_x = tile_x * self.tile.tile_size
                world_y = tile_y * self.tile.tile_size

                window_x = int(world_x - self.camera.offset_x)
                window_y = int(world_y - self.camera.offset_y)

                self.tile.draw(tile,window_x,window_y)