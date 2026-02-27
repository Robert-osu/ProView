import pygame

from my_lib.GameObjectRenderer import GameObject

# --- Класс для сетки (будет рисовать команды) ---
class GridObject(GameObject):
    def __init__(self, viewer_context, z_order=1):
        super().__init__(z_order)
        print(f"[DEBUG] GridObject.__init__: viewer_context={viewer_context}, z_order={z_order}")
        self.ctx = viewer_context # Ссылка на главный класс с данными
        self.screen = self.ctx.screen

    def _draw(self):
        if self.ctx.re_grid:
            # Очищаем экран
            self.screen.fill((50, 50, 50))

            self.draw_grid()
            self.ctx.re_grid = False
            self.ctx.re_ui = True
            self.ctx.re_top = True

    def _update(self):
        # Обновление, связанное с сеткой (например, скролл)
        pass

    def _execute(self):
        # Логика сетки (проверка hover, клики)
        pass

    def draw_grid(self):
        """Рисует сетку с изображениями"""
        self.ctx.update_visible_range()
        
        # Определяем шрифт для номеров строк
        ln_size = self.ctx.line_font_size
        line_font = pygame.font.Font(None, ln_size)
        
        # Рисуем номера строк (только для видимых строк)
        first_visible_row = self.ctx.first_visible_row
        last_visible_row = self.ctx.last_visible_row
        padding = self.ctx.padding
        thumb_size = self.ctx.thumb_size
        offsetW = self.ctx.offsetW
        offsetH = self.ctx.offsetH
        scroll_y = self.ctx.scroll_y
        window_height = self.ctx.window_height
        line_number_padding = self.ctx.line_number_padding
        k = self.ctx.k_size
        cols = self.ctx.cols


        for row in range(first_visible_row, last_visible_row):
            y = padding + row * (thumb_size + padding) + offsetH - scroll_y
            
            if y + thumb_size > 0 and y < window_height:
                line_number_x = padding + line_number_padding
                line_number_y = y + thumb_size // 2
                
                if row < 9:
                    pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * k), line_number_y - (12 * k), (30 * k), (26 * k)), border_top_right_radius=int(5 * k))
                elif row < 99:
                    pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * k), line_number_y - (12 * k), (40 * k), (26 * k)), border_top_right_radius=int(5 * k))
                else:
                    pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * k), line_number_y - (12 * k), (45 * k), (26 * k)), border_top_right_radius=int(5 * k))
                
                line_text = line_font.render(f"{row + 1}", True, (200, 200, 200))
                self.ctx.screen.blit(line_text, (line_number_x, line_number_y - (8 * k)))
        
        # Рисуем только видимые миниатюры
        for row in range(first_visible_row, last_visible_row):
            for col in range(cols):
                i = row * cols + col
                if i >= len(self.ctx.cmd_list):
                    break
                
                x = padding + col * (thumb_size + padding) + offsetW
                y = padding + row * (thumb_size + padding) + offsetH - scroll_y
                
                if y + thumb_size < 0 or y > window_height:
                    continue
                
                self.draw_thumbnail(i, x, y)

        self.ctx.scrollbar.draw(self.ctx.screen)

    def draw_thumbnail(self, index, x, y):
        """Рисует одну миниатюру с рамкой и номером"""
        cmd = self.ctx.cmd_list[index]
        self.screen.blit(self.ctx.cmd_images[cmd], (x, y))
        
        # Рисуем номер
        font = pygame.font.Font(None, self.ctx.font_size)
        text = font.render(str(index), True, (255, 255, 255))
        self.screen.blit(text, (x+self.ctx.font_padding, y+self.ctx.font_padding))