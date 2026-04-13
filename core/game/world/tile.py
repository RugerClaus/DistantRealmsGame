import helper
class Tile():
    def __init__(self,system,camera):
        self.system = system
        self.camera = camera
        self.tile_size = 32
        self.image = system.window.load_image(helper.asset("atlas"))
        print(self.image.get_size())
        
        self.tiles = {}

    def get_rect(self,tile_name):
        x,y = self.tiles[tile_name]
        return (x*self.tile_size,y*self.tile_size,self.tile_size,self.tile_size)

    def register(self, name, grid_x, grid_y):
        self.tiles[name] = (grid_x, grid_y)
        
    def get_visible(self):
        screen_w = self.system.window.get_width()
        screen_h = self.system.window.get_height()

        
        start_x = self.system.math.floor(self.camera.offset_x / self.tile_size)
        start_y = self.system.math.floor(self.camera.offset_y / self.tile_size)

        end_x = self.system.math.floor((self.camera.offset_x + screen_w) / self.tile_size) + 1
        end_y = self.system.math.floor((self.camera.offset_y + screen_h) / self.tile_size) + 1

        return start_x, start_y, end_x, end_y
    
    def draw(self, name, x, y):
        src_rect = self.get_rect(name)

        print(self.camera.offset_y)

        self.system.window.screen.blit(self.image, (x, y), src_rect)