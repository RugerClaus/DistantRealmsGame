from helper import log_event, log_error
from core.state.GameLayer.state import GAMESTATE
from core.state.GameLayer.statemanager import GameStateManager
from core.state.ApplicationLayer.dev import DEVELOPER_MODE
from core.state.ApplicationLayer.state import APPSTATE
from core.menus.pause import Pause

from core.game.world.world import World

class Game:
    def __init__(self, system):
        self.state = GameStateManager()
        self.system = system
        self.pause_menu = Pause(system, self)
        self.world = None

    def toggle_pause(self):
        if not self.state.is_state(GAMESTATE.PAUSED):
            self.pause_menu.reset_menu()
            self.state.set_state(GAMESTATE.PAUSED)
        else:
            self.state.set_state(GAMESTATE.PLAYING)

    def resize(self,event_h):
        self.game_object.resize(event_h)

    def new_game(self):
        self.world = World(self.system)
        self.system.app_state.set_state(APPSTATE.GAME)
        self.state.set_state(GAMESTATE.PLAYING)

    def handle_event(self, event):

        if event.type == self.system.input.keydown():
            if self.system.input.get_key_name(event.key) == "escape":
                
                if self.state.is_state(GAMESTATE.PAUSED):
                    self.pause_menu.back_to_root()
                    self.toggle_pause()
                else:
                    self.toggle_pause()
        
        if self.state.is_state(GAMESTATE.PLAYING):
            if event.type == self.system.input.keydown():
                if self.system.control_state.is_state(DEVELOPER_MODE.ON):
                    pass

        elif self.state.is_state(GAMESTATE.PAUSED):
            self.pause_menu.handle_event(event)
        
        if event.type == self.system.input.video_resize_event():
            self.pause_menu.create_buttons()
            self.resize(event.h)

    def draw(self):
        if self.state.is_state(GAMESTATE.PAUSED):
            self.pause_menu.update()
            self.pause_menu.draw()
        elif self.state.is_state(GAMESTATE.PLAYING):
            if self.world is not None:
                self.world.update()
                self.world.draw()

    def update(self):
        pass

    def quit_to_menu(self):
        self.system.go_to_menu()

    def quit(self):
        # MAYBE PUT SOME AUTO SAVE LOGIC HERE
        self.system.app_state.set_state(APPSTATE.QUIT)