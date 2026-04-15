from opensimplex import OpenSimplex
from core.game.world.debug.debug import WorldDebug
from core.game.entities.type import EntityType
from core.game.camera.camera import Camera
from core.game.world.layer import Layer
from core.game.entities.player.player import Player

class World():
    def __init__(self, system, camera=None, load_data=None):
        self.system = system
        self.load_date = load_data
        self.camera = camera if camera else Camera(system.window.get_width(), system.window.get_height())

        
        self.ground_layer = Layer(system, self.camera)
        self.structure_layer = Layer(system, self.camera)

        self.player = Player(10 * self.camera.zoom_size,40 *self.camera.zoom_size , system, EntityType.PLAYER, self.camera,self.check_player_collision)

        self.chunk_size = 16

        self.seed = system.random.randint(100000, 200000)
        self.h_noise = OpenSimplex(self.seed)
        self.moist_noise = OpenSimplex(self.seed + 1)
        self.plant_noise = OpenSimplex(self.seed + 2)

        self.current_tile = None

        self.ground_layer.register("grass", 0, 1)
        self.ground_layer.register("water", 0, 0)
        self.ground_layer.register("sand", 4, 2)

        self.structure_layer.register("bush", 5, 0, collidable=True)
        self.structure_layer.register("rock", 5, 1, collidable=True)

        self.world_debug = WorldDebug(system,self.camera,self)

        self.tile_cache = {}
        self.chunk_cache = {}

    def check_player_collision(self, new_world_x, new_world_y, player_rect):
        tile_size = self.camera.zoom_size

        left = int(new_world_x // tile_size)
        right = int((new_world_x + player_rect.width) // tile_size)
        top = int(new_world_y // tile_size)
        bottom = int((new_world_y + player_rect.height) // tile_size)

        test_rect = player_rect.copy()
        test_rect.topleft = (new_world_x, new_world_y)

        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                _, structure_tile = self.generate_tiles(x, y)
                if structure_tile and self.structure_layer.is_collidable(structure_tile):
                    tile_rect = self.system.window.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    if test_rect.colliderect(tile_rect):
                        return True
        return False

    def resize(self):
        self.camera.width = self.system.window.get_width()
        self.camera.height = self.system.window.get_height()
        self.ground_layer.camera = self.camera
        self.structure_layer.camera = self.camera

    def world_eval(self, x, y):
        scale = 0.05
        height = self.h_noise.noise2(x * scale, y * scale)
        moisture = self.moist_noise.noise2(x * scale, y * scale)
        plants = self.plant_noise.noise2(x * scale, y * scale)
        return height, moisture, plants

    def generate_tiles(self, x, y):
        tile_key = (x, y)
        if tile_key in self.tile_cache:
            return self.tile_cache[tile_key]

        height, moisture, plants = self.world_eval(x, y)
        if height < -0.25:
            ground_tile = "water"
        elif height < -0.15:
            ground_tile = "sand"
        elif moisture > 0.3:
            ground_tile = "grass"
        else:
            ground_tile = "grass"

        structure_tile = None

        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        chunk_key = (chunk_x, chunk_y)

        if chunk_key not in self.chunk_cache:
            self.chunk_cache[chunk_key] = {"objects": []}
            chunk_seed = self.seed + chunk_x * (self.seed + 3) + chunk_y * (self.seed + 3)
            rand = self.system.random.Random(chunk_seed)

            max_objects = 7
            num_objects = rand.randint(0, max_objects)

            placed = 0
            attempts = 0
            while placed < num_objects and attempts < 20:
                local_x = rand.randint(0, self.chunk_size - 1)
                local_y = rand.randint(0, self.chunk_size - 1)
                global_x = chunk_x * self.chunk_size + local_x
                global_y = chunk_y * self.chunk_size + local_y

                # Only place on grass
                h, m, p = self.world_eval(global_x, global_y)
                tile_type = "grass" if h >= -0.15 or m > 0.3 else "sand"
                if tile_type != "grass":
                    attempts += 1
                    continue

                too_close = any(
                    abs(local_x - ox) <= 1 and abs(local_y - oy) <= 1
                    for ox, oy, _ in self.chunk_cache[chunk_key]["objects"]
                )
                if too_close:
                    attempts += 1
                    continue

                obj_type = rand.choice(["bush", "rock"])
                self.chunk_cache[chunk_key]["objects"].append((local_x, local_y, obj_type))
                placed += 1

        if ground_tile == "grass" and chunk_key in self.chunk_cache:
            local_x = x % self.chunk_size
            local_y = y % self.chunk_size
            for ox, oy, obj_type in self.chunk_cache[chunk_key]["objects"]:
                if ox == local_x and oy == local_y:
                    structure_tile = obj_type
                    break

        self.tile_cache[tile_key] = (ground_tile, structure_tile)
        return ground_tile, structure_tile

    def update(self):
        self.camera.update(self.player)

        ground_tile, structure_tile = self.generate_tiles(self.player.normalized_x, self.player.normalized_y)
        self.current_tile = structure_tile if structure_tile else ground_tile

    def draw(self):
        start_x, start_y, end_x, end_y = self.ground_layer.get_visible()
        end_x += 1
        end_y += 1

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                ground_tile, structure_tile = self.generate_tiles(tile_x, tile_y)

                world_x, world_y = tile_x, tile_y
                window_x = int(world_x * self.ground_layer.render_tile_size - self.camera.offset_x)
                window_y = int(world_y * self.ground_layer.render_tile_size - self.camera.offset_y)

                self.ground_layer.draw(ground_tile, window_x, window_y)

                if structure_tile:
                    self.structure_layer.draw(structure_tile, window_x, window_y)
                
        visible_chunks = set()
        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                chunk = (tile_x // self.chunk_size, tile_y // self.chunk_size)
                visible_chunks.add(chunk)
        
        self.player.update()
        self.world_debug.draw(self.player)
        self.player.draw()