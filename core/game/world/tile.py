import helper
class Tile():
    def __init__(self,system,camera):
        self.system = system
        self.camera = camera
        self.tile_size = 32
        self.image = system.window.load_image(helper.asset("atlas"))
        
        self.atlas_tile_size = 16
        self.render_tile_size = camera.zoom_size
        
        self.tiles = {}
        self.cache = {}

    def get_rect(self, tile_name):
        x, y = self.tiles[tile_name]
        return (
            x * self.atlas_tile_size,
            y * self.atlas_tile_size,
            self.atlas_tile_size,
            self.atlas_tile_size
        )

    def register(self, name, grid_x, grid_y):
        self.tiles[name] = (grid_x, grid_y)

        rect = self.get_rect(name)
        tile_surface = self.image.subsurface(rect).copy()
        tile_surface = self.system.window.transform_smoothscale(tile_surface, self.camera.zoom_size, self.camera.zoom_size).convert_alpha()

        self.cache[name] = tile_surface
        
    def get_visible(self):
        screen_w = self.system.window.get_width()
        screen_h = self.system.window.get_height()

        start_x = self.system.math.floor(self.camera.offset_x / self.render_tile_size)
        start_y = self.system.math.floor(self.camera.offset_y / self.render_tile_size)

        end_x = self.system.math.floor((self.camera.offset_x + screen_w) / self.render_tile_size) + 1
        end_y = self.system.math.floor((self.camera.offset_y + screen_h) / self.render_tile_size) + 1

        return start_x, start_y, end_x, end_y
    
    def draw(self, name, x, y):
        self.system.window.blit(self.cache[name], (x, y))