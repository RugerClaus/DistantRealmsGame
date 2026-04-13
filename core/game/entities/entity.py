# if i ever want to mess with global entities

from core.game.entities.type import EntityType

class Entity:
    def __init__(self, world_x, world_y, system, type: EntityType):
        self.world_x = world_x
        self.world_y = world_y
        self.type = type
        self.system = system

    def update(self):
        pass

    def draw(self):
        pass