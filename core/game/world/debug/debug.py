from core.state.GameLayer.Debug.Chunk.state import CHUNK_BORDER_STATE
from core.state.GameLayer.Debug.Tile.state import TILE_OVERLAY_STATE
from core.state.GameLayer.Debug.Chunk.statemanager import ChunkBorderStateManager
from core.state.GameLayer.Debug.Tile.statemanager import TileOverlayStateManager


class WorldDebug():
    def __init__(self, system, camera, world):
        self.system = system
        self.camera = camera
        self.ground_layer = world.ground_layer
        self.structure_layer = world.structure_layer
        self.generate_tiles = world.generate_tiles
        self.chunk_size = world.chunk_size
        self.chunk_border_state = ChunkBorderStateManager()
        self.tile_overlay_state = TileOverlayStateManager()

    def toggle_chunk_borders(self):
        if self.chunk_border_state.is_state(CHUNK_BORDER_STATE.OFF):
            self.chunk_border_state.set_state(CHUNK_BORDER_STATE.ON)
        else:
            self.chunk_border_state.set_state(CHUNK_BORDER_STATE.OFF)
        
    def enable_structure_tile_overlay(self):
        self.tile_overlay_state.set_state(TILE_OVERLAY_STATE.STRUCTURE)
    
    def disable_tile_overlays(self):
        self.tile_overlay_state.set_state(TILE_OVERLAY_STATE.NONE)

    def handle_input(self,event):
        if event.type == self.system.input.keydown():
            if event.key == self.system.input.keys.F3_key():
                self.toggle_chunk_borders()
            if event.key == self.system.input.keys.F4_key():
                self.enable_structure_tile_overlay()
            if event.key == self.system.input.keys.F5_key():
                self.disable_tile_overlays()
            
    def _highlight_structure_tiles(self):
        start_x, start_y, end_x, end_y = self.ground_layer.get_visible()
        end_x += 1
        end_y += 1

        ts = self.structure_layer.render_tile_size
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                _, structure_tile = self.generate_tiles(x, y)
                if structure_tile:
                    window_x = int(x * ts - self.camera.offset_x)
                    window_y = int(y * ts - self.camera.offset_y)

                    tile_overlay = self.system.window.make_surface(ts, ts, True)
                    tile_overlay.fill((255, 0, 0, 128))

                    self.system.window.blit(tile_overlay, (window_x, window_y))

    def _draw_chunk_border(self, chunk_x, chunk_y, tile_render_size, width, color=(255,0,0)):
        chunk_size_pixels = self.chunk_size * tile_render_size
        x0 = int(chunk_x * chunk_size_pixels - self.camera.offset_x)
        y0 = int(chunk_y * chunk_size_pixels - self.camera.offset_y)
        x1 = x0 + chunk_size_pixels
        y1 = y0 + chunk_size_pixels

        self.system.window.draw_line((x0, y0), (x1, y0), color, width)
        self.system.window.draw_line((x0, y1), (x1, y1), color, width)  
        self.system.window.draw_line((x0, y0), (x0, y1), color, width)
        self.system.window.draw_line((x1, y0), (x1, y1), color, width)

    def _get_visible_chunks(self,player):
        start_x, start_y, end_x, end_y = self.ground_layer.get_visible()
        end_x += 1
        end_y += 1

        visible_chunks = {}
        player_chunk_x = int(player.normalized_x) // self.chunk_size
        player_chunk_y = int(player.normalized_y) // self.chunk_size

        self.system.game_debug["chunk"] = (player_chunk_x,player_chunk_y)

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                chunk_x = x // self.chunk_size
                chunk_y = y // self.chunk_size
                if (chunk_x, chunk_y) not in visible_chunks:
                    is_player_chunk = (chunk_x == player_chunk_x and chunk_y == player_chunk_y)
                    visible_chunks[(chunk_x, chunk_y)] = is_player_chunk
                    

        return visible_chunks

    def _draw_chunk_borders(self,player):
        ts = self.structure_layer.render_tile_size
        visible_chunks = self._get_visible_chunks(player)

        for (chunk_x, chunk_y), is_player_chunk in visible_chunks.items():
            color = (0, 0, 0) if is_player_chunk else (255, 0, 0)
            width = 3 if is_player_chunk else 1
            self._draw_chunk_border(chunk_x, chunk_y, ts, width, color=color)

    def draw(self,player):
        if self.tile_overlay_state.is_state(TILE_OVERLAY_STATE.STRUCTURE):
            self._highlight_structure_tiles()
        if self.chunk_border_state.is_state(CHUNK_BORDER_STATE.ON):
            self._draw_chunk_borders(player)
