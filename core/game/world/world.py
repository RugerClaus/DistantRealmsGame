from opensimplex import OpenSimplex
from core.game.world.debug.debug import WorldDebug
from core.game.entities.type import EntityType
from core.game.camera.camera import Camera
from core.game.world.layer import Layer
from core.game.entities.player.player import Player
from core.game.world.structure import Structure

class World():
    def __init__(self, system, camera=None, load_data=None):
        self.system = system
        self.camera = camera if camera else Camera(system.window.get_width(), system.window.get_height())

        if load_data is not None:
            self.player = Player(load_data["player_world_x"],load_data["player_world_y"], system, EntityType.PLAYER, self.camera,self.check_player_collision)
            self.seed = load_data["seed"]
        else:
            self.player = Player(0,0,system, EntityType.PLAYER, self.camera,self.check_player_collision)
            self.seed = system.random.randint(100000, 200000)

        self.ground_layer = Layer(system, self.camera)
        self.structure_layer = Layer(system, self.camera)
        self.h_noise = OpenSimplex(self.seed)
        self.moist_noise = OpenSimplex(self.seed + 1)
        self.plant_noise = OpenSimplex(self.seed + 2)
        
        self.chunk_size = 16
        self.current_tile = None

        self.ground_layer.register("grass", 0, 1)
        self.ground_layer.register("water", 0, 0)
        self.ground_layer.register("sand", 4, 2)

        self.structure_layer.register("bush", 5, 0, collidable=True)
        self.structure_layer.register("rock", 5, 1, collidable=True)
        self.structure_layer.register("stone", 3, 3, collidable=True)
        self.structure_layer.register("brick",5,3, collidable=True)


        self.world_debug = WorldDebug(system,self.camera,self)
        
        self.tile_cache = {}
        self.chunk_cache = {}

        self.structures = {}

        tiles1 = [
            [(1,0,"stone"), (2,0,"stone"), (3,0,"stone"), (4,0,"stone"), (5,0,"stone"), (6,0,"stone"), (7,0,"stone")],
            [(1,1,"stone"), (2,1,"stone"), (3,1,"stone"), (4,1,"stone"), (5,1,"stone"), (6,1,"stone"), (7,1,"stone")],
            [(1,2,"stone"), (2,2,"stone"), (3,2,"stone"), (4,2,"stone"), (5,2,"stone"), (6,2,"stone"), (7,2,"stone")],
            [(1,3,"stone"), (2,3,"stone"), (3,3,"stone"), (4,3,"stone"), (5,3,"stone"), (6,3,"stone"), (7,3,"stone")],
            [(1,4,"stone"), (2,4,"stone"), (3,4,"stone"), (4,4,"stone"), (5,4,"stone"), (6,4,"stone"), (7,4,"stone")],
            [(1,5,"stone"), (2,5,"stone"), (3,5,"stone"), (4,5,"stone"), (5,5,"stone"), (6,5,"stone"), (7,5,"stone")],
            [(1,6,"stone"), (2,6,"stone"), (3,6,"stone"), (4,6,"stone"), (5,6,"stone"), (6,6,"stone"), (7,6,"stone")],
            [(1,7,"stone"), (2,7,"stone"), (3,7,"stone"), (4,7,"brick_entrance"), (5,7,"stone"), (6,7,"stone"), (7,7,"stone")],
        ]
        tiles2 = [
            [(1,0,"stone"), (2,0,"stone"), (3,0,"stone"), (4,0,"stone"), (5,0,"stone"), (6,0,"stone"), (7,0,"stone")],
            [(1,1,"stone"), (2,1,"stone"), (3,1,"stone"), (4,1,"stone"), (5,1,"stone"), (6,1,"stone"), (7,1,"stone")],
            [(1,2,"stone"), (2,2,"stone"), (3,2,"stone"), (4,2,"stone"), (5,2,"stone"), (6,2,"stone"), (7,2,"stone")],
            [(1,3,"stone"), (2,3,"stone"), (3,3,"stone"), (4,3,"stone"), (5,3,"stone"), (6,3,"stone"), (7,3,"brick_entrance")],
            [(1,4,"stone"), (2,4,"stone"), (3,4,"stone"), (4,4,"stone"), (5,4,"stone"), (6,4,"stone"), (7,4,"stone")],
            [(1,5,"stone"), (2,5,"stone"), (3,5,"stone"), (4,5,"stone"), (5,5,"stone"), (6,5,"stone"), (7,5,"stone")],
            [(1,6,"stone"), (2,6,"stone"), (3,6,"stone"), (4,6,"stone"), (5,6,"stone"), (6,6,"stone"), (7,6,"stone")],
            [(1,7,"stone"), (2,7,"stone"), (3,7,"stone"), (4,7,"stone"), (5,7,"stone"), (6,7,"stone"), (7,7,"stone")],
        ]
        
        entrances1 = [(3, 7)]
        entrances2 = [(6, 3)]

        house = Structure("forward_facing_stone_hovel", tiles=tiles1, entrances=entrances1, collidable=True)
        althouse = Structure("right_facing_alt_stone_hovel", tiles=tiles2, entrances=entrances2, collidable=True)

        self.register_structure(house)
        self.register_structure(althouse)

    def register_structure(self, structure):
        self.structures[structure.name] = structure
        for row in structure.tiles:  # iterate over each row
            for dx, dy, tile_type in row:  # now dx, dy, tile_type is correct
                is_entrance = (dx, dy) in structure.entrances
                if tile_type == "stone":
                    self.structure_layer.register(tile_type, 3, 3, collidable=structure.collidable and not is_entrance)
                elif tile_type == "bush":
                    self.structure_layer.register(tile_type, 5, 0, collidable=structure.collidable and not is_entrance)
                elif tile_type == "rock":
                    self.structure_layer.register(tile_type, 5, 1, collidable=structure.collidable and not is_entrance)
                elif tile_type.startswith("brick"):
                    self.structure_layer.register(tile_type, 5, 3, collidable=structure.collidable and not is_entrance)

    def serialize(self):
        return {
            "player_world_x": self.player.world_x,
            "player_world_y": self.player.world_y,
            "seed": self.seed
        }

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
                tile_data = self.generate_tiles(x, y)

                # --- 1. Check collidable tiles ---
                if tile_data.get("collidable", False):
                    tile_rect = self.system.window.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    if test_rect.colliderect(tile_rect):
                        self.player.handle_collisions(tile_data)
                        return True

                # --- 2. Check entrances ---
                if tile_data.get("is_entrance", False):
                    tile_rect = self.system.window.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    if test_rect.colliderect(tile_rect):
                        self.player.handle_entrance(tile_data)
                        return False

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
    
    def place_structure_at(self, structure, anchor_x, anchor_y):
        if not hasattr(self, "preplaced_structures"):
            self.preplaced_structures = []

        self.preplaced_structures.append({
            "structure_obj": structure,
            "anchor_x": anchor_x,
            "anchor_y": anchor_y
        })

        occupied_chunks = set()

        for row in structure.tiles:
            for dx, dy, tile_type in row:
                gx = anchor_x + dx
                gy = anchor_y + dy
                chunk_x = gx // self.chunk_size
                chunk_y = gy // self.chunk_size
                local_x = gx % self.chunk_size
                local_y = gy % self.chunk_size

                if (chunk_x, chunk_y) not in self.chunk_cache:
                    self.chunk_cache[(chunk_x, chunk_y)] = {
                        "tiles": {},
                        "tile_structures": {},
                        "structures": [],
                        "objects": []
                    }
                chunk = self.chunk_cache[(chunk_x, chunk_y)]

                # Store tile type and structure name
                chunk["tiles"][(local_x, local_y)] = tile_type
                chunk["tile_structures"][(local_x, local_y)] = structure.name
                occupied_chunks.add((chunk_x, chunk_y))

        # Keep structure record in each affected chunk
        for chunk_key in occupied_chunks:
            chunk = self.chunk_cache[chunk_key]
            chunk["structures"].append({
                "structure": structure.name,
                "anchor_x": anchor_x % self.chunk_size,
                "anchor_y": anchor_y % self.chunk_size
            })

        # Track all occupied chunks globally
        if not hasattr(self, "occupied_structure_chunks"):
            self.occupied_structure_chunks = set()
        self.occupied_structure_chunks.update(occupied_chunks)

    def _generate_chunk(self, chunk_x, chunk_y):
        chunk_seed = self.seed + chunk_x * (self.seed + 3) + chunk_y * (self.seed + 3)
        rand = self.system.random.Random(chunk_seed)

        # Initialize chunk if missing
        if (chunk_x, chunk_y) not in self.chunk_cache:
            self.chunk_cache[(chunk_x, chunk_y)] = {
                "tiles": {},
                "tile_structures": {},
                "structures": [],
                "objects": []
            }
        chunk = self.chunk_cache[(chunk_x, chunk_y)]

        max_objects = 5
        num_objects = rand.randint(0, max_objects)
        available_structures = list(self.structures.values())
        single_tile_objects = ["bush", "rock"]

        placed = 0
        attempts = 0
        min_distance_chunks = 5  # Minimum distance between structures in chunks

        while placed < num_objects and attempts < 20:
            local_x = rand.randint(0, self.chunk_size - 1)
            local_y = rand.randint(0, self.chunk_size - 1)
            choice_type = rand.choice(["structure", "object"])

            if choice_type == "structure" and available_structures:
                structure = rand.choice(available_structures)

                # --- 1. Check nearby chunks for minimum distance ---
                can_place = True
                for dx in range(-min_distance_chunks, min_distance_chunks + 1):
                    for dy in range(-min_distance_chunks, min_distance_chunks + 1):
                        check_chunk = (chunk_x + dx, chunk_y + dy)
                        if hasattr(self, "occupied_structure_chunks") and check_chunk in self.occupied_structure_chunks:
                            can_place = False
                            break
                    if not can_place:
                        break
                if not can_place:
                    attempts += 1
                    continue

                # --- 2. Check terrain suitability ---
                valid = True
                for row in structure.tiles:
                    for dx, dy, _ in row:
                        gx = chunk_x * self.chunk_size + local_x + dx
                        gy = chunk_y * self.chunk_size + local_y + dy
                        h, _, _ = self.world_eval(gx, gy)
                        if h < -0.15:  # avoid water/sand
                            valid = False
                            break
                    if not valid:
                        break
                if not valid:
                    attempts += 1
                    continue

                # --- 3. Place structure tiles in all affected chunks ---
                for row in structure.tiles:
                    for dx, dy, tile_type in row:
                        gx = chunk_x * self.chunk_size + local_x + dx
                        gy = chunk_y * self.chunk_size + local_y + dy
                        struct_chunk_x = gx // self.chunk_size
                        struct_chunk_y = gy // self.chunk_size
                        local_x_chunk = gx % self.chunk_size
                        local_y_chunk = gy % self.chunk_size

                        if (struct_chunk_x, struct_chunk_y) not in self.chunk_cache:
                            self.chunk_cache[(struct_chunk_x, struct_chunk_y)] = {
                                "tiles": {},
                                "tile_structures": {},
                                "structures": [],
                                "objects": []
                            }
                        target_chunk = self.chunk_cache[(struct_chunk_x, struct_chunk_y)]
                        target_chunk["tiles"][(local_x_chunk, local_y_chunk)] = tile_type
                        target_chunk["tile_structures"][(local_x_chunk, local_y_chunk)] = structure.name

                        # --- 4. Mark chunk as occupied for spacing ---
                        if not hasattr(self, "occupied_structure_chunks"):
                            self.occupied_structure_chunks = set()
                        self.occupied_structure_chunks.add((struct_chunk_x, struct_chunk_y))

                # Keep structure record
                chunk["structures"].append({
                    "structure": structure.name,
                    "anchor_x": local_x,
                    "anchor_y": local_y
                })

            elif choice_type == "object":
                if (local_x, local_y) in chunk["tiles"]:
                    attempts += 1
                    continue

                gx = chunk_x * self.chunk_size + local_x
                gy = chunk_y * self.chunk_size + local_y
                h, _, _ = self.world_eval(gx, gy)
                if h < -0.15:
                    attempts += 1
                    continue

                obj_type = rand.choice(single_tile_objects)
                chunk["objects"].append({
                    "object": obj_type,
                    "x": local_x,
                    "y": local_y
                })
                chunk["tiles"][(local_x, local_y)] = obj_type
                chunk["tile_structures"][(local_x, local_y)] = None

            placed += 1
            attempts += 1


    def generate_tiles(self, x, y):
        tile_key = (x, y)
        if tile_key in self.tile_cache:
            return self.tile_cache[tile_key]

        h, m, _ = self.world_eval(x, y)
        if h < -0.25:
            ground_tile = "water"
            collidable = True
        elif h < -0.15:
            ground_tile = "sand"
            collidable = False
        else:
            ground_tile = "grass"
            collidable = False

        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        chunk_key = (chunk_x, chunk_y)

        if chunk_key not in self.chunk_cache:
            self._generate_chunk(chunk_x, chunk_y)

        local_x = x % self.chunk_size
        local_y = y % self.chunk_size
        chunk = self.chunk_cache[chunk_key]

        structure_tile = chunk["tiles"].get((local_x, local_y), None)
        building_name = chunk["tile_structures"].get((local_x, local_y), None)

        tile_data = {
            "ground": ground_tile,
            "structure": structure_tile,
            "building": building_name,          # <-- new field
            "type": structure_tile or ground_tile,
            "collidable": collidable,
            "is_entrance": False
        }

        if structure_tile:
            if self.structure_layer.is_collidable(structure_tile):
                tile_data["collidable"] = True
            if structure_tile.endswith("_entrance"):
                tile_data["is_entrance"] = True

        self.tile_cache[tile_key] = tile_data
        return tile_data

    def update(self):
        self.camera.update(self.player)

        tile_data = self.generate_tiles(self.player.normalized_x, self.player.normalized_y)
        self.current_tile = tile_data["structure"] if tile_data["structure"] else tile_data["ground"]

    def draw(self):
        start_x, start_y, end_x, end_y = self.ground_layer.get_visible()
        end_x += 1
        end_y += 1

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile_data = self.generate_tiles(tile_x, tile_y)
                ground_tile = tile_data["ground"]
                structure_tile = tile_data["structure"]

                window_x = int(tile_x * self.ground_layer.render_tile_size - self.camera.offset_x)
                window_y = int(tile_y * self.ground_layer.render_tile_size - self.camera.offset_y)

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