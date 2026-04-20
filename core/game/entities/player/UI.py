from enum import Enum, auto
from core.ui.font import FontEngine


class PlayerUIManager:
    def __init__(self, system, player):
        self.window = system.window
        self.player = player
        self.bar_width = self.window.get_width()
        self.bar_height = 20 
        self.surface = self.window.make_surface(self.bar_width, self.bar_height, True)
        self.rect_position = (0, self.window.get_height()-self.bar_height)
        self.font = FontEngine(30).font
        self.score_font = FontEngine(50).font
        self.last_reset_time = self.window.get_current_time()
        
    def resize(self):
        self.bar_width = self.window.get_width()
        self.rect_position = (0, self.window.get_height() - self.bar_height)
        self.surface = self.window.make_surface(self.bar_width, self.bar_height, True)

    def reset_timer(self):
        self.last_reset_time = self.window.get_current_time()

    def draw_player_info(self):

        health_text = f"Health %: {self.player.health}"
        health_surface = self.score_font.render(health_text, True, (0,0,0))
        health_surface_rect = health_surface.get_rect(right = self.window.get_width() - 5, top = self.window.get_height() - self.bar_height - 45)
        blur_surface = self.window.make_surface(275,40,True)
        blur_rect = blur_surface.get_rect(right = self.window.get_width() - 5, top = self.window.get_height() - self.bar_height - 45)
        blur_surface.fill((0,0,0,128))
        self.window.blit(blur_surface,blur_rect)
        self.window.blit(health_surface, health_surface_rect)

    def draw(self):

        self.surface.fill((0, 0, 0))

        
        size_avg = self.player.health
        progress = min(size_avg / self.player.max_health, 1.0)
        fill_width = int(self.bar_width * progress)
        fill_width = max(fill_width, 1)

        outline_rect = self.window.Rect(0, 0, self.bar_width, self.bar_height)

        fill_color = (
            max(0, min(255, int(255 * (1 - progress)))),
            0,
            max(0, min(255, int(255 * progress)))
        )
        fill_rect = self.window.Rect(
            outline_rect.left + 2,       
            outline_rect.top + 2,        
            fill_width - 4,
            self.bar_height - 4
        )

        self.window.draw_rect(self.surface, fill_color, fill_rect)
        self.window.draw_rect(self.surface, (255, 255, 255), outline_rect, 2)
            
        

        self.window.blit(self.surface, self.rect_position)
        self.draw_player_info()
