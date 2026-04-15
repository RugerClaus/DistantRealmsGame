from core.game.entities.entity import Entity
from core.state.GameLayer.Entities.Player.Movement.Vertical.statemanager import PlayerVerticalMoveStateManager
from core.state.GameLayer.Entities.Player.Movement.Vertical.state import PLAYER_MOVE_VERT_STATE
from core.state.GameLayer.Entities.Player.Movement.Horizontal.statemanager import PlayerHorizontalMoveStateManager
from core.state.GameLayer.Entities.Player.Movement.Horizontal.state import PLAYER_MOVE_HORZ_STATE

class Player(Entity):
    def __init__(self, x, y, system, type, camera,collision):
        self.ignore_input = False
        self.camera = camera
        self.collision_check = collision
        self.size = camera.zoom_size // 2
        super().__init__(x, y, system, type)
        self.surface = self.system.window.make_surface(self.size, self.size, True)
        self.rect = self.surface.get_rect()
        self.move_vert_state = PlayerVerticalMoveStateManager()
        self.move_horz_state = PlayerHorizontalMoveStateManager()

        self.speed = 2000

        self.vel_x = 0
        self.vel_y = 0
        self.normalized_x = 0
        self.normalized_y = 0
        
        self.color = (255, 0, 0)

    def update(self):
        self.handle_input()
        self.update_velocity()

        delta = self.system.window.get_delta_time()
        new_x = self.world_x + self.vel_x * delta
        new_y = self.world_y + self.vel_y * delta

        if self.collision_check:
            if not self.collision_check(new_x, self.world_y, self.rect):
                self.world_x = new_x
            else:
                self.vel_x = 0

            if not self.collision_check(self.world_x, new_y, self.rect):
                self.world_y = new_y
            else:
                self.vel_y = 0
        else:
            self.world_x = new_x
            self.world_y = new_y

        self.normalized_x = self.world_x / self.camera.zoom_size
        self.normalized_y = self.world_y / self.camera.zoom_size

    def draw(self):
        if not self.ignore_input:
            self.surface.fill((0, 0, 0, 0))
            self.system.window.draw_rect(self.surface, self.color, (0, 0, self.size, self.size))

            screen_x = self.system.window.get_width() // 2
            screen_y = self.system.window.get_height() // 2

            self.system.window.blit(self.surface, (screen_x, screen_y))

    def handle_input(self):
        if not self.ignore_input:
            keys = self.system.input.get_pressed_keys()

            if keys[self.system.input.game_controls.move_up] and not keys[self.system.input.game_controls.move_down]:
                self.move_vert_state.set_state(PLAYER_MOVE_VERT_STATE.MOVE_UP)
            elif keys[self.system.input.game_controls.move_down] and not keys[self.system.input.game_controls.move_up]:
                self.move_vert_state.set_state(PLAYER_MOVE_VERT_STATE.MOVE_DOWN)
            else:
                self.move_vert_state.set_state(PLAYER_MOVE_VERT_STATE.NONE)

            if keys[self.system.input.game_controls.move_right] and not keys[self.system.input.game_controls.move_left]:
                self.move_horz_state.set_state(PLAYER_MOVE_HORZ_STATE.MOVE_RIGHT)
            elif keys[self.system.input.game_controls.move_left] and not keys[self.system.input.game_controls.move_right]:
                self.move_horz_state.set_state(PLAYER_MOVE_HORZ_STATE.MOVE_LEFT)
            else:
                self.move_horz_state.set_state(PLAYER_MOVE_HORZ_STATE.NONE)
        else:
            return

    def update_velocity(self):
        self.vel_x = 0
        self.vel_y = 0

        if self.move_horz_state.is_state(PLAYER_MOVE_HORZ_STATE.MOVE_RIGHT):
            self.vel_x = self.speed
        elif self.move_horz_state.is_state(PLAYER_MOVE_HORZ_STATE.MOVE_LEFT):
            self.vel_x = -self.speed

        if self.move_vert_state.is_state(PLAYER_MOVE_VERT_STATE.MOVE_DOWN):
            self.vel_y = self.speed
        elif self.move_vert_state.is_state(PLAYER_MOVE_VERT_STATE.MOVE_UP):
            self.vel_y = -self.speed

        if self.vel_x != 0 and self.vel_y != 0:
            import math
            factor = math.sqrt(2) / 2
            self.vel_x *= factor
            self.vel_y *= factor