import pygame
from my_lib.GameObjectRenderer import GameObject

class GridObject(GameObject):
    def __init__(self, viewer_context, z_order=1):
        super().__init__(z_order)
        self.ctx = viewer_context
        self.screen = self.ctx.screen
        
        # Параметры сетки
        self.cell_size = self.ctx.thumb_size + self.ctx.padding
        self.cols = self.ctx.cols
        
        # Кэш для поверхностей ячеек
        self.cell_surfaces = {}  # {index: surface}
        
        # Предварительно создаем все ячейки
        self._create_all_cells()
    
    def update_cell_image(self, idx, cmd):
        """Обновляет кеш изображения для указанной ячейки"""
        if 0 <= idx < len(self.ctx.cmd_list):
            # self.ctx.cmd_list[idx] = cmd
            
            # Обновляем кеш
            self.cell_surfaces[idx] = self.ctx.cmd_images[cmd]
            
            # Помечаем сетку для перерисовки
            self.ctx.re_grid = True

    def _create_all_cells(self):
        """Создает поверхности для всех ячеек заранее"""
        thumb_size = self.ctx.thumb_size
        padding = self.ctx.padding
        font = pygame.font.Font(None, self.ctx.font_size)
        
        for idx, cmd in enumerate(self.ctx.cmd_list):
            # Создаем поверхность для ячейки
            cell = self.ctx.cmd_images[cmd]
            
            # Добавляем рамку
            pygame.draw.rect(cell, (80, 80, 80), cell.get_rect(), 1)
            
            self.cell_surfaces[idx] = cell
    
    def _draw(self):
        if self.ctx.re_grid:
            self.screen.fill((50, 50, 50))
            self.draw_grid()
            self.ctx.re_grid = False
            self.ctx.re_ui = True
            self.ctx.re_top = True
    
    def _update(self):
        pass
    
    def _execute(self):
        pass
    
    def draw_grid(self):
        """Рисует сетку с изображениями"""
        self.ctx.update_visible_range()
        
        # Определяем видимые строки
        first_row = self.ctx.first_visible_row
        last_row = self.ctx.last_visible_row
        
        # Параметры позиционирования
        cell_size = self.cell_size
        padding = self.ctx.padding
        offsetW = self.ctx.offsetW
        offsetH = self.ctx.offsetH
        scroll_y = self.ctx.scroll_y
        window_height = self.ctx.window_height
        
        # Рисуем номера строк
        self._draw_line_numbers(first_row, last_row, offsetH, scroll_y, window_height)
        
        # Рисуем видимые ячейки
        for row in range(first_row, last_row):
            for col in range(self.cols):
                idx = row * self.cols + col
                if idx >= len(self.ctx.cmd_list):
                    break
                
                # Вычисляем позицию
                x = padding + col * cell_size + offsetW
                y = padding + row * cell_size + offsetH - scroll_y
                
                # Проверяем видимость
                if y + self.ctx.thumb_size < 0 or y > window_height:
                    continue
                
                # Рисуем ячейку из кэша
                if idx in self.cell_surfaces:
                    self.screen.blit(self.cell_surfaces[idx], (x, y))
        
        # Рисуем скроллбар
        self.ctx.scrollbar.draw(self.ctx.screen)
    
    def _draw_line_numbers(self, first_row, last_row, offsetH, scroll_y, window_height):
        """Рисует номера строк"""
        line_font = pygame.font.Font(None, self.ctx.line_font_size)
        padding = self.ctx.padding
        thumb_size = self.ctx.thumb_size
        cell_size = self.cell_size
        k = self.ctx.k_size
        line_number_padding = self.ctx.line_number_padding
        
        for row in range(first_row, last_row):
            y = padding + row * cell_size + offsetH - scroll_y
            
            if y + thumb_size > 0 and y < window_height:
                line_number_x = padding + line_number_padding
                line_number_y = y + thumb_size // 2
                
                # Фон для номера
                if row < 9:
                    width = 30 * k
                elif row < 99:
                    width = 40 * k
                else:
                    width = 45 * k
                
                pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * k), line_number_y - (12 * k), 
                                width, (26 * k)), 
                               border_top_right_radius=int(5 * k))
                
                # Текст номера
                line_text = line_font.render(f"{row + 1}", True, (200, 200, 200))
                self.screen.blit(line_text, (line_number_x, line_number_y - (8 * k)))
    
    def get_cell_at_pos(self, mouse_x, mouse_y, grid_x, grid_y):
        """Определяет индекс ячейки по координатам мыши"""
        # Относительные координаты внутри сетки
        rel_x = mouse_x - grid_x - self.ctx.offsetW
        rel_y = mouse_y - grid_y - self.ctx.offsetH + self.ctx.scroll_y
        
        if rel_x < 0 or rel_y < 0:
            return None
        
        col = rel_x // self.cell_size
        row = rel_y // self.cell_size
        
        if col >= self.cols:
            return None
        
        idx = row * self.cols + col
        if 0 <= idx < len(self.ctx.cmd_list):
            return idx
        return None