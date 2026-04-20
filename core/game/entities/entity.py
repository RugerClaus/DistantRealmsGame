from core.game.entities.animations import Animation
from core.game.entities.type import EntityType

class Entity:
    def __init__(self, world_x, world_y, type: EntityType, size=None):
        self.world_x = world_x
        self.world_y = world_y
        self.animation = Animation
        self.type = type
        self.animations = {}
        self.current_animation = None

    def update(self):
        if self.current_animation is not None:
            self.current_animation.update()