from core.game.entities.entity import Entity
from core.game.entities.player.atlas import PlayerAtlas
from core.state.GameLayer.Entities.Player.Movement.Vertical.statemanager import PlayerVerticalMoveStateManager
from core.state.GameLayer.Entities.Player.Movement.Vertical.state import PLAYER_MOVE_VERT_STATE
from core.state.GameLayer.Entities.Player.Movement.Horizontal.statemanager import PlayerHorizontalMoveStateManager
from core.state.GameLayer.Entities.Player.Movement.Horizontal.state import PLAYER_MOVE_HORZ_STATE
from core.state.GameLayer.Entities.Player.Life.state import PLAYER_LIFE_STATE
from core.state.GameLayer.Entities.Player.Life.statemanager import PlayerLifeStateManager
class Player(Entity):
    def __init__(self, x, y, system, type, camera,collision):
        self.system = system
        self.ignore_input = False
        self.camera = camera
        self.collision_check = collision
        self.size = camera.zoom_size
        super().__init__(x, y, system, type)
        if self.ignore_input:
            self.surface = self.system.window.make_surface(self.size, self.size, True)
            self.rect = self.surface.get_rect()
        self.move_vert_state = PlayerVerticalMoveStateManager()
        self.move_horz_state = PlayerHorizontalMoveStateManager()
        self.life_state = PlayerLifeStateManager()

        self.health = 100

        self.speed = 1000

        self.vel_x = 0
        self.vel_y = 0
        self.normalized_x = 0
        self.normalized_y = 0

        self.atlas = PlayerAtlas(system)
        self.animations = {
            "idle": self.animation(self.atlas.get_frames("idle"), frame_delay=5),
            "idleleft": self.animation(self.atlas.get_frames("idleleft"), frame_delay=5),
            "walkleft": self.animation(self.atlas.get_frames("walkleft"), frame_delay=2),
            "walkright": self.animation(self.atlas.get_frames("walkright"), frame_delay=2),
        }
        self.current_animation = self.animations["idle"]
        self.rect = None
        
    def handle_collisions(self,structure_tile):
        if structure_tile == "bush":
            self.health -= 1

    def respawn(self):
        self.life_state.set_state(PLAYER_LIFE_STATE.ALIVE)
        self.health = 100
        self.world_x = 0
        self.world_y = 0

    def check_death(self):
        if self.health <= 0:
            self.life_state.set_state(PLAYER_LIFE_STATE.DEAD)
            self.respawn()

    def update(self):
        self.handle_input()
        self.update_velocity()
        self.check_death()

        delta = self.system.window.get_delta_time()
        new_x = self.world_x + self.vel_x * delta
        new_y = self.world_y + self.vel_y * delta

        if self.collision_check and self.rect is not None:
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

        self.current_animation.update()
        print(self.health)

    def draw(self):
        if not self.ignore_input:
            frame = self.current_animation.get_current_frame()
            self.rect = frame.get_rect()
            final = frame.subsurface(self.rect).copy()
            final = self.system.window.transform_smoothscale(frame, self.camera.zoom_size, self.camera.zoom_size).convert_alpha()

            screen_x = self.system.window.get_width() // 2
            screen_y = self.system.window.get_height() // 2
            self.rect.topleft = (screen_x, screen_y)
            

            self.system.window.blit(final,self.rect)

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
            self.current_animation = self.animations["walkright"]
        elif self.move_horz_state.is_state(PLAYER_MOVE_HORZ_STATE.MOVE_LEFT):
            self.vel_x = -self.speed
            self.current_animation = self.animations["walkleft"]
        if self.move_vert_state.is_state(PLAYER_MOVE_VERT_STATE.MOVE_DOWN):
            self.vel_y = self.speed
        elif self.move_vert_state.is_state(PLAYER_MOVE_VERT_STATE.MOVE_UP):
            self.vel_y = -self.speed

        elif self.move_horz_state.is_state(PLAYER_MOVE_HORZ_STATE.NONE) and self.move_vert_state.is_state(PLAYER_MOVE_VERT_STATE.NONE):
            if self.move_horz_state.previous_state == PLAYER_MOVE_HORZ_STATE.MOVE_LEFT:
                self.current_animation = self.animations["idleleft"]
            else:
                self.current_animation = self.animations["idle"]

        if self.vel_x != 0 and self.vel_y != 0:
            import math
            factor = math.sqrt(2) / 2
            self.vel_x *= factor
            self.vel_y *= factor