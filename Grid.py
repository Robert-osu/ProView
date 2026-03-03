import pygame
from my_lib.GameObjectRenderer import GameObject
from TextInput import TextInput
from Command import Command

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
    
    def _draw(self):
        if self.ctx.re_grid:
            self.screen.fill((50, 50, 50))
            # self.screen.fill((255, 250, 250))
            self.draw_grid()
            self.ctx.re_top = True
            self.ctx.re_ui = True
            self.ctx.re_grid = False
    
    def _update(self):
        pass
    
    def _execute(self):
        pass

    # def input_text(self):
    #     if self.text == None:
    #         self.text = TextInput(self.ctx, self.ctx.x + 3, self.ctx.y + 3, 64, 64, 6)
    #         self.ctx.manager.add(self.text, self.text.z_order)
    #         self.hovered = self.ctx.hovered.current
    #         self.ctx.text = self.text
    #     if self.hovered != self.ctx.hovered.current:
    #         self.ctx.manager.delete(self.text.id)
    #         self.text = None
    #         self.ctx.text = None
    #         self.ctx.is_input = False
    #         self.ctx.re_grid = True
    
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
        cmd_list = list(Command)
        
        for idx, cmd in enumerate(self.ctx.cmd_list):
            print(self.ctx.cmd_list[idx])
            # Создаем поверхность для ячейки
            cell = self.ctx.cmd_images[cmd]

            cmd = self.ctx.pro._commands[idx]
            if cmd in Command.NO_ARGS:
                pass
            elif cmd in Command.ONE_ARGS:
                if cmd == cmd_list[112]:
                    x, y = 35, 42
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[113]:
                    x, y = 35, 42
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[24]:
                    x, y = 42, 33
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[25]:
                    x, y = 32, 33
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[26]:
                    x, y = 32, 33
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[40]:
                    x, y = 20, 33
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[97]:
                    x, y = 34, 44
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[98]:
                    x, y = 28, 44
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[104]:
                    x, y = 32, 48
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[105]:
                    x, y = 32, 48
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[106]:
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[107]:
                    x, y = 32, 48
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[166]:
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[114]:
                    x, y = 35, 40
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[115]:
                    x, y = 35, 40
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[116]:
                    x, y = 38, 40
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[117]:
                    x, y = 38, 40
                    cell.blit(*self.render_text(idx, x=x, y=y))
                elif cmd == cmd_list[137]:
                    x, y = 32, 33
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[139]:
                    x, y = 28, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[140]:
                    x, y = 28, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[181]:
                    x, y = 30, 35
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                elif cmd == cmd_list[182]:
                    x, y = 30, 35
                    cell.blit(*self.render_text(idx, x=x, y=y, color=-1))
                else:
                    x, y = 30, 33
                    cell.blit(*self.render_text(idx, x=x, y=y))
            elif cmd in Command.TWO_ARGS:
                if cmd == cmd_list[119]:
                    x, y = 22, 23
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[99]:
                    x, y = 30, 15
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=1))
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[100]:
                    x, y = 30, 15
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=1))
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[101]:
                    x, y = 30, 15
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=1))
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[102]:
                    x, y = 30, 15
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=1))
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[103]:
                    x, y = 30, 15
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=1))
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[120]:
                    x, y = 22, 23
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[121]:
                    x, y = 22, 23
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[122]:
                    x, y = 22, 23
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[123]:
                    x, y = 22, 23
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[124]:
                    x, y = 22, 23
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 52
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[108]:
                    x, y = 26, 16
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=2))
                    x, y = 30, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[109]:
                    x, y = 26, 16
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=2))
                    x, y = 30, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[110]:
                    x, y = 26, 16
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=2))
                    x, y = 30, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[111]:
                    x, y = 26, 16
                    cell.blit(*self.render_text(idx, x=x, y=y, i=1, color=2))
                    x, y = 30, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[128]:
                    x, y = 22, 22
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                    x, y = 30, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                elif cmd == cmd_list[129]:
                    x, y = 22, 22
                    cell.blit(*self.render_text(idx, x=x, y=y, color=2))
                    x, y = 38, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                elif cmd == cmd_list[130]:
                    x, y = 22, 22
                    cell.blit(*self.render_text(idx, x=x, y=y, color=2))
                    x, y = 38, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
                else:
                    x, y = 30, 15
                    cell.blit(*self.render_text(idx, x=x, y=y, color=1))
                    x, y = 32, 50
                    cell.blit(*self.render_text(idx, x=x, y=y, color=0))
            
            
            # Добавляем рамку
            pygame.draw.rect(cell, (80, 80, 80), cell.get_rect(), 1)
            
            self.cell_surfaces[idx] = cell

    def render_text(self, id, i=0, x=5, y=0, fsize=20, color=0):
        thumb_size = self.ctx.thumb_size
        padding = self.ctx.padding
        font = pygame.font.SysFont('Times New Roman', fsize)
        # font = pygame.font.Font(None, fsize)
        color_var1 = (127, 255, 212) # cyan
        color_var2 = (100, 255, 100) # green
        color_var3 = (152, 251, 152) # light green
        color_val1 = (255, 248, 220) # Cornsilk (brown)
        color_val2 = (240, 230, 140) # gold
        color_lab1 = (255, 255, 255)

        # text_surface = font.render(self.ctx.pro.getValue(id, i), True, text_color)
        if color==0: # цвет переменных
            color = color_var1
        elif color==-1: # цвет меток
            color = color_lab1
        elif color==2: # цвет переменных 2
            color = color_var2
        elif color==1: # цвет числовых значений
            color = color_val2

        valueT = self.ctx.pro.getValue(id, i)
        if valueT == '0':
            valueT = ''



        text_surface = font.render(valueT, True, color)
        # text_surface = font.render("WWW", True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Позиционируем текст внизу ячейки
        # text_x = x
        # text_y = y
        
        # # Добавляем фон для текста для лучшей читаемости
        # text_bg = pygame.Surface((text_surface.get_width() + 10, 
        #                             text_surface.get_height() + 4))
        # text_bg.fill((30, 30, 30))
        # text_bg.set_alpha(180)
        # cell.blit(text_bg, (text_x - 5, text_y - 2))
        
        # Добавляем текст
        return (text_surface, text_rect)
 
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