class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width = width
        self.height = height
        self.zoom_size = 24

    def update(self, target):
        self.offset_x = target.world_x - self.width // 2
        self.offset_y = target.world_y - self.height // 2

    def apply(self, rect):
        return rect.move(-self.offset_x, -self.offset_y)