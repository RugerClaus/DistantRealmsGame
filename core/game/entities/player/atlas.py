from helper import asset
class PlayerAtlas:
    def __init__(self,system):
        self.animations = {
            "idle": (system.window.load_image(asset("playeridle")).convert_alpha(),4),
            "idleleft": (system.window.load_image(asset("playeridleleft")).convert_alpha(),4),
            "walkleft": (system.window.load_image(asset("playerleft")).convert_alpha(),6),
            "walkright": (system.window.load_image(asset("playerright")).convert_alpha(),6)
        }
        self.frame_size = 32

    def get_frames(self, key):
        if key in self.animations:
            sheet = self.animations[key][0]
            frame_count = self.animations[key][1]
            frames = self.extract_frames(sheet, frame_count)
            return frames
        return None
    
    def extract_frames(self, sheet, frame_count):
            frames = []
            sheet_width, sheet_height = sheet.get_size()
            frames_per_row = sheet_width // self.frame_size
            
            for i in range(frame_count):
                x = (i % frames_per_row) * self.frame_size
                y = (i // frames_per_row) * self.frame_size
                frame = sheet.subsurface((x, y, self.frame_size, self.frame_size))
                frames.append(frame)
            
            return frames