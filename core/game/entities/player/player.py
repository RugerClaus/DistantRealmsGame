from core.game.entities.entity import Entity

class Player(Entity):
    def __init__(self, x, y, system, type):
        super().__init__(x, y, system, type)

    def update(self):
        pass

    def draw(self):
        pass