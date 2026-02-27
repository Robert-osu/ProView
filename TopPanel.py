import pygame

from my_lib.GameObjectRenderer import GameObject

# --- Класс для верхней панели ---
class TopPanelObject(GameObject):
    def __init__(self, viewer_context, z_order=10):
        super().__init__(z_order)
        print(f"[DEBUG] TopPanelObject.__init__: viewer_context={viewer_context}, z_order={z_order}")
        self.ctx = viewer_context
        self.screen = viewer_context.screen

    def _draw(self):
        # Рисует панель поверх сетки
        if self.ctx.re_top:
            self.draw_top_panel()
            self.ctx.re_top = False

    def _update(self):
        # Обновление, связанное с сеткой (например, скролл)
        pass

    def _execute(self):
        # Логика сетки (проверка hover, клики)
        pass

    def draw_top_panel(self):
        """Рисует верхнюю панель с кнопками"""
        # Рисуем фон панели
        panel_rect = pygame.Rect(0, 0, self.ctx.window_width, self.ctx.panel_height)
        pygame.draw.rect(self.screen, (60, 60, 70), panel_rect)  # Темно-серый фон
        
        # Рисуем нижнюю границу панели
        pygame.draw.line(self.screen, (100, 100, 110), 
                        (0, self.ctx.panel_height), 
                        (self.ctx.window_width, self.ctx.panel_height), 2)
        
        # Рисуем дополнительную информацию на панели
        font = pygame.font.Font(None, int(20 * self.ctx.k_size))
        
        # Информация о количестве команд
        text = font.render(f"Привет от Majin'а", True, (200, 200, 200))
        text_x = self.ctx.window_width - text.get_width() - self.ctx.padding * 2
        text_y = (self.ctx.panel_height - text.get_height()) // 2
        self.screen.blit(text, (text_x, text_y))