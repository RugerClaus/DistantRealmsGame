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
        self.player = Player(0,0,system,EntityType.PLAYER,self.camera)
        self.seed = system.random.randint(100000,200000)

        self.tile.register("grass",0,0)
        self.tile.register("water",1,0)

    def tile_hash(self,x, y):
        n = x * 73856093 ^ y * 19349663
        n = (n << 13) ^ n
        return (n * (n * n * 15731 + 789221) + self.seed) & 0x7fffffff

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

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile_name = self.generate_tiles(tile_x, tile_y)
                
                # world coordinates in tile units
                world_x = tile_x
                world_y = tile_y

                # convert to screen coordinates
                window_x = int(world_x * self.tile.render_tile_size - self.camera.offset_x)
                window_y = int(world_y * self.tile.render_tile_size - self.camera.offset_y)

                self.tile.draw(tile_name, window_x, window_y)
        self.player.update()
        self.player.draw()