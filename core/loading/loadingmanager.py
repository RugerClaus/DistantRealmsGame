from core.state.ApplicationLayer.state import APPSTATE
from core.state.ApplicationLayer.Loading.state import LOAD_SCREEN_STATE
from core.state.ApplicationLayer.Loading.statemanager import LoadingStateManager
from core.state.ApplicationLayer.Audio.SFX.state import SYSTEM_SFX_STATE
from core.state.GameLayer.Entities.Player.Movement.Vertical.state import PLAYER_MOVE_VERT_STATE
from core.state.GameLayer.Entities.Player.Movement.Horizontal.state import PLAYER_MOVE_HORZ_STATE
from core.game.world.world import World
from core.game.camera.camera import Camera
from helper import asset

class LoadingManager:
    def __init__(self,system):
        self.system = system
        self.state = LoadingStateManager()
        self.splash_one_original = self.system.window.load_image(asset("splashpt1")).convert_alpha()
        self.splash_one = self.splash_one_original
        self.splash_one_rect = self.splash_one.get_rect(center=(self.system.window.get_width()//2,self.system.window.get_height()//2))
        self.splash_two_original = self.system.window.load_image(asset("splashpt2")).convert_alpha()
        self.splash_two = self.splash_two_original
        self.splash_two_rect = self.splash_two.get_rect(center=(self.system.window.get_width()//2,self.system.window.get_height()//2))
        self.splash_one_sfx_played = False
        self.splash_two_sfx_played = False
        self.splash_two_start_time = None
        self.start_time = self.system.window.get_current_time()
        self.state.set_state(LOAD_SCREEN_STATE.STUDIO_SPLASH_SCREEN_ONE)

        # Paralax splash screen
        camera = Camera(self.system.window.get_width(),self.system.window.get_height())
        camera.zoom_size = 128
        self.world = World(self.system,camera)
        self.world.player.ignore_input = True
        self.world.player.speed = 500
        
        for tile in self.world.tile.cache.values():
            tile.set_alpha(80)

    def rescale_assets(self):
        window_w, window_h = self.system.window.get_size()
        self.splash_one_rect = self.splash_one.get_rect(center=(window_w // 2, window_h // 2 - 50))
        self.splash_two_rect = self.splash_two.get_rect(center=(window_w // 2, window_h // 2 - 50))

    def update(self):
        if self.state.is_state(LOAD_SCREEN_STATE.NONE):
            self.system.app_state.set_state(APPSTATE.MAIN_MENU)
            
        if not self.system.app_state.is_state(APPSTATE.LOADING):
            self.system.sound.system_sfx_state.set_state(SYSTEM_SFX_STATE.OFF)
        
        if self.system.app_state.is_state(APPSTATE.MAIN_MENU):
            pass

    def play_splash_2_fade_in(self):
        current_time = self.system.window.get_current_time()
        
        if self.splash_two_start_time is None:
            self.splash_two_start_time = current_time
            if not self.splash_two_sfx_played:
                self.system.sound.play_sfx("splash2")
                self.splash_two_sfx_played = True
         
        el = current_time - self.splash_two_start_time
        du = 9300
        alpha = (el / du) * 255
        if alpha > 255:
            alpha = 255
        
        self.splash_two.set_alpha(alpha)

        self.system.window.blit(self.splash_two,self.splash_two_rect)

        if el >= du:
            self.state.set_state(LOAD_SCREEN_STATE.NONE)

        if self.world is not None:
            self.world.player.move_horz_state.set_state(PLAYER_MOVE_HORZ_STATE.MOVE_LEFT)
            self.world.player.move_vert_state.set_state(PLAYER_MOVE_VERT_STATE.MOVE_UP)
            self.world.update()

    def draw(self):
        current_time = self.system.window.get_current_time()
        if self.state.is_state(LOAD_SCREEN_STATE.STUDIO_SPLASH_SCREEN_ONE):
            self.system.window.blit(self.splash_one, self.splash_one_rect)

            if not self.splash_one_sfx_played:
                self.system.sound.play_sfx("splash1")
                self.splash_one_sfx_played = True
        if current_time - self.start_time > 2500:
            self.state.set_state(LOAD_SCREEN_STATE.STUDIO_SPLASH_SCREEN_TWO)
            
            self.world.update()
            self.world.draw()
        if self.state.is_state(LOAD_SCREEN_STATE.STUDIO_SPLASH_SCREEN_TWO):
            
            self.play_splash_2_fade_in()   
