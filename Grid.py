import pygame
from my_lib.GameObjectRenderer import GameObject
from TextInput import TextInput
from Command import Command

class GridObject(GameObject):
    """
    Представляет сетку операторов программатора и визуальные элементы управления
    методы: 
    - коллизия элементов
    - отрисовка сетки, номеров строк, навигации страниц
    - кэширование картинок всех и отдельно
    """
    def __init__(self, viewer_context, z_order=1):
        super().__init__(z_order)



        self.ctx = viewer_context
        self.screen = self.ctx.screen
        self.conf = self.ctx.config_cmd
        self.pagehover = False
        
        # Параметры сетки
        self.cell_size = self.ctx.thumb_size + self.ctx.padding
        self.cols = self.ctx.cols

        self.page = 0


        # кэш поверхностей 
        self.cell_rects = {} # Словарь для хранения прямоугольников операторов {id: rect}
        self._dirty_positions = True  # Флаг для обновления позиций
        self.nav_buttons_rects = {}  # Словарь для хранения прямоугольников кнопок {page_num: rect}
        self._nav_positions_dirty = True  # Флаг для обновления позиций
        self.cell_surfaces = {}  # Словарь для хранения изображений {index: surface}

        # требуемые параметры
        self.list_commands = self.ctx.pro._commands
        self.padding = self.ctx.padding
        self.offsetW = self.ctx.offsetW
        self.offsetH = self.ctx.offsetH
        self.window_height = self.ctx.window_height
        self.thumb_size = self.ctx.thumb_size
        
        # Кэш для поверхностей ячеек
        
        # Предварительно создаем все ячейки
        self._create_all_cells()
    
    def _draw(self):
        if self.ctx.re_grid:
            self.screen.fill((50, 50, 50))
            self.draw_grid()
            self.draw_page_navigation(self.pagehover)
            pygame.display.flip()
            self.ctx.re_grid = False
            self.ctx.re_top = False
        elif self.ctx.re_top:
            x, y = 0, 0
            width, height = self.ctx.window_height, self.ctx.panel_height
            rect = pygame.Rect(x, y, width, height)
            self.screen.fill((40, 40, 40), rect)
            self.draw_page_navigation(self.pagehover)
            pygame.display.flip()
            self.ctx.re_top = False
    
    def _update(self):
        pass
    
    def _execute(self):
        pass

    def _ensure_positions_updated(self):
        """Обновляет позиции если нужно"""
        if not self._dirty_positions:
            return
        
        self.cell_rects.clear()
        
        first_row = self.page * 12
        last_row = first_row + 12
        cell_size = self.cell_size
        padding = self.padding
        offsetW = self.offsetW
        offsetH = self.offsetH
        
        for row in range(first_row, last_row):
            normalized_row = row % 12
            
            for col in range(self.cols):
                idx = row * self.cols + col
                if idx >= len(self.list_commands):
                    break
                
                if idx in self.cell_surfaces:
                    x = padding + col * cell_size + offsetW
                    y = padding + normalized_row * cell_size + offsetH
                    self.cell_rects[idx] = pygame.Rect(
                        x, y, cell_size, cell_size
                    )
        
        self._dirty_positions = False

    def _ensure_all_positions_updated(self):
        """Обновляет позиции для всех страниц"""
        if not self._dirty_positions:
            return
        
        self.cell_rects.clear()
        
        cell_size = self.cell_size
        padding = self.padding
        offsetW = self.offsetW
        offsetH = self.offsetH
        rows_per_page = 12
        total_pages = 16
        
        # Проходим по всем страницам
        for page in range(total_pages):
            first_row = page * rows_per_page
            last_row = first_row + rows_per_page
            
            for row in range(first_row, last_row):
                normalized_row = row % rows_per_page  # или row - first_row
                
                for col in range(self.cols):
                    idx = row * self.cols + col
                    if idx >= len(self.list_commands):
                        break
                    
                    if idx in self.cell_surfaces:
                        x = padding + col * cell_size + offsetW
                        y = padding + normalized_row * cell_size + offsetH
                        
                        self.cell_rects[idx] = pygame.Rect(
                            x, y, cell_size, cell_size
                        )
        
        self._dirty_positions = False

    def draw_grid(self):
        """Рисует сетку с изображениями"""
        self._ensure_all_positions_updated()
        
        window_height = self.window_height
        first_row = self.page * 12
        last_row = first_row + 12
        print(self.page)

        self._draw_line_numbers(first_row, last_row, self.offsetH, window_height)
        
        for row in range(first_row, last_row):
            normalized_row = row % 12
            for col in range(self.cols):
                idx = row * self.cols + col
                if idx >= len(self.ctx.pro._commands):
                    break
                rect = self.cell_rects[idx]
                if rect.y + self.thumb_size < 0 or rect.y > window_height:
                    continue
                self.screen.blit(self.cell_surfaces[idx], rect.topleft)

    def _update_nav_positions(self):
        """Обновляет позиции кнопок навигации"""
        self.nav_buttons_rects.clear()
        
        total_pages = 16
        nav_y = 10
        button_width = 50
        button_height = 30
        button_spacing = 5
        
        # Пересчитываем начальную позицию с учетом текущей ширины экрана
        start_x = (self.screen.get_width() - (total_pages * (button_width + button_spacing))) // 2
        
        for page in range(1, total_pages + 1):
            x = start_x + (page - 1) * (button_width + button_spacing)
            self.nav_buttons_rects[page] = pygame.Rect(
                x, nav_y, button_width, button_height
            )
        
        self._nav_positions_dirty = False

    def draw_page_navigation(self, pagehover=None):
        """Рисует навигацию по страницам вверху экрана"""
        # Обновляем позиции если нужно (например, при изменении размера окна)
        if self._nav_positions_dirty:
            self._update_nav_positions()
        
        # Параметры навигации
        rows_per_page = 12
        total_pages = 16
        current_page = self.page + 1
        
        ishover = pagehover is not None
        
        # Параметры отображения
        nav_height = 40
        nav_y = 10
        
        # Рисуем фон для навигации
        nav_bg = pygame.Surface((self.screen.get_width(), nav_height))
        nav_bg.fill((40, 40, 40))
        nav_bg.set_alpha(200)
        self.screen.blit(nav_bg, (0, 0))
        
        # Шрифт для номеров страниц
        font = pygame.font.SysFont('arial', 16, bold=True)
        
        # Рисуем кнопки страниц
        for page, button_rect in self.nav_buttons_rects.items():
            # Определяем цвета для кнопки
            if page == current_page:
                button_color = (100, 150, 255)  # Синий для текущей страницы
                text_color = (255, 255, 255)
                border_color = (150, 200, 255)
            else:
                if ishover and page == pagehover:
                    button_color = (90, 90, 90)  # Светло-серый при наведении
                else:
                    button_color = (60, 60, 60)  # Серый для остальных
                text_color = (200, 200, 200)
                border_color = (100, 100, 100)
            
            # Используем функцию для отрисовки кнопки
            self._draw_nav_button(button_rect, page, button_color, 
                                text_color, border_color, font, ishover)

    # def draw_page_navigation(self, pagehover=None):
    #     """Рисует навигацию по страницам вверху экрана"""
    #     # Параметры навигации
    #     rows_per_page = 12
    #     total_pages = 16
    #     current_page = self.page + 1

    #     if pagehover != None:
    #         ishover = True
    #     else:
    #         ishover = False
        
    #     # Параметры отображения
    #     nav_height = 40
    #     nav_y = 10
    #     button_width = 50
    #     button_height = 30
    #     button_spacing = 5
    #     start_x = (self.screen.get_width() - (total_pages * (button_width + button_spacing))) // 2
        
    #     # Рисуем фон для навигации
    #     nav_bg = pygame.Surface((self.screen.get_width(), nav_height))
    #     nav_bg.fill((40, 40, 40))
    #     nav_bg.set_alpha(200)
    #     self.screen.blit(nav_bg, (0, 0))
        
    #     # Шрифт для номеров страниц
    #     font = pygame.font.SysFont('arial', 16, bold=True)
        
    #     # Рисуем кнопки страниц
    #     for page in range(1, total_pages + 1):
    #         x = start_x + (page - 1) * (button_width + button_spacing)
    #         button_rect = pygame.Rect(x, nav_y, button_width, button_height)

    #         # Сохраняем область кнопки
    #         # self.nav_buttons_rects[page] = button_rect
            
    #         # Определяем цвета для кнопки
    #         if page == current_page:
    #             button_color = (100, 150, 255)  # Синий для текущей страницы
    #             text_color = (255, 255, 255)
    #             border_color = (150, 200, 255)
    #         else:
    #             if ishover and page == pagehover:
    #                 button_color = (90, 90, 90)  # Светло-серый при наведении
    #             else:
    #                 button_color = (60, 60, 60)  # Серый для остальных
    #             text_color = (200, 200, 200)
    #             border_color = (100, 100, 100)
            
    #         # Используем функцию для отрисовки кнопки
    #         self._draw_nav_button(button_rect, page, button_color, 
    #                             text_color, border_color, font, ishover)
        
    #     # Рисуем дополнительную информацию
    #     info_font = pygame.font.SysFont('arial', 14, bold=True)
        
    #     info_text = f"Привет от Majin"
    #     text = info_font.render(info_text, True, (255, 228, 196))
    #     self.screen.blit(text, (10, self.ctx.panel_height // 2))

    # ПОЛУЧАЕМ КНОПКУ ПОД КУРСОРОМ МАТЕМАТИЧЕСКИ (БЕЗ ЦИКЛА)
    def get_nav_button_at_position(self, mouse_x, mouse_y):
        """Определяет номер страницы под курсором математически, без перебора"""
        # Проверяем, находится ли мышь в области навигации по Y
        if mouse_y < 10 or mouse_y > 40:  # nav_y = 10, nav_y + button_height = 40
            return None
        
        # Параметры навигации (должны быть доступны)
        total_pages = 16
        button_width = 50
        button_spacing = 5
        start_x = (self.screen.get_width() - (total_pages * (button_width + button_spacing))) // 2
        
        # Вычисляем смещение относительно начала первой кнопки
        rel_x = mouse_x - start_x
        
        # Проверяем, вне области кнопок
        if rel_x < 0 or rel_x > total_pages * (button_width + button_spacing):
            return None
        
        # Вычисляем номер страницы (1-16)
        page = rel_x // (button_width + button_spacing) + 1
        
        # Проверяем границы
        if 1 <= page <= total_pages:
            return page
        
        return None

    def _draw_nav_button(self, rect, page_num, button_color, 
                     text_color, border_color, font, ishover=False):
        # Добавляем эффект увеличения при наведении
        draw_rect = rect

        # Рисуем основную кнопку
        pygame.draw.rect(self.screen, button_color, draw_rect, border_radius=5)
        
        # Рисуем границу (более толстую при наведении)
        border_width = 3 if ishover and self.pagehover == page_num else 2
        pygame.draw.rect(self.screen, border_color, draw_rect, border_width, border_radius=5)
        
        # Рендерим и размещаем текст
        text = font.render(str(page_num), True, text_color)
        text_rect = text.get_rect(center=draw_rect.center)
        self.screen.blit(text, text_rect)

    def handle_page_click(self):
        """Обрабатывает клик по навигации страниц"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rows_per_page = 12
        total_pages = 16
        current_page = self.page + 1
        
        # Параметры отображения (должны совпадать с draw_page_navigation)
        nav_height = 40
        nav_y = 10
        button_width = 50
        button_height = 30
        button_spacing = 5
        start_x = (self.screen.get_width() - (total_pages * (button_width + button_spacing))) // 2
        
            # Проверяем вертикальную область
        if not (nav_y <= mouse_y <= nav_y + button_height):
            return None
        
        # Вычисляем начальную позицию
        total_width = total_pages * (button_width + button_spacing) - button_spacing
        start_x = (self.screen.get_width() - total_width) // 2
        
        # Проверяем горизонтальную область
        if not (start_x <= mouse_x <= start_x + total_width):
            return None
        
        # Вычисляем страницу
        relative_x = mouse_x - start_x
        page_index = relative_x // (button_width + button_spacing)
        
        # Проверяем, что клик по кнопке, а не по промежутку
        button_start = start_x + page_index * (button_width + button_spacing)
        if mouse_x > button_start + button_width:
            return None
        
        page = page_index + 1
        if page > total_pages:
            return None
        
        target_row = (page - 1) * rows_per_page
        if target_row >= len(self.ctx.cmd_list):
            return None
        
        self.page = page_index
        self.ctx.re_grid = True
        return None
    
    def update_cell_image(self, idx, cmd):
        """Обновляет кеш изображения для указанной ячейки"""
        if 0 <= idx < len(self.ctx.pro._commands):
            # self.ctx.cmd_list[idx] = cmd

            original = self.ctx.cmd_images[cmd]
            cell = original.copy()  # Создаем копию, чтобы не изменять оригинал

            if cmd in Command.NO_ARGS:
                pass
            elif cmd in Command.ONE_ARGS:
                x, y, type = self.conf.get_one_args_config(cmd)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=0, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=0, color=0))
                elif type == 2: # value
                    pass

            elif cmd in Command.TWO_ARGS:
                is_above = True
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=2))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

                is_above = False
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=0))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

            # Добавляем рамку
            pygame.draw.rect(cell, (80, 80, 80), cell.get_rect(), 1)
            
            # Обновляем кеш
            self.cell_surfaces[idx] = cell
            
            # Помечаем сетку для перерисовки
            self.ctx.re_grid = True

    def _create_cell(self, idx, cmd, condition):
        """Создает поверхности для всех ячеек заранее"""
        thumb_size = self.ctx.thumb_size
        padding = self.ctx.padding
        font = pygame.font.SysFont('arial', self.ctx.font_size)
        cmd_list = list(Command)
        
        # Создаем поверхность для ячейки
        original = self.ctx.cmd_images[cmd]
        cell = original.copy()  # Создаем копию, чтобы не изменять оригинал

        if cmd in Command.NO_ARGS:
            pass
        elif cmd in Command.ONE_ARGS:
            if condition == 2:
                x, y, type = self.conf.get_one_args_config(cmd)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=0, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=0, color=0))
                elif type == 2: # value
                    pass

        elif cmd in Command.TWO_ARGS:
            if condition == 0:
                is_above = True
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=2))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

            elif condition == 1:
                is_above = False
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=0))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))
            elif condition == 2:
                is_above = True
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=2))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

                is_above = False
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=0))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

    
        # Добавляем рамку
        pygame.draw.rect(cell, (80, 80, 80), cell.get_rect(), 1)
        
        self.cell_surfaces[idx] = cell

    def _create_all_cells(self):
        """Создает поверхности для всех ячеек заранее"""
        thumb_size = self.ctx.thumb_size
        padding = self.ctx.padding
        font = pygame.font.SysFont('arial', self.ctx.font_size)
        cmd_list = list(Command)
        
        for idx, cmd in enumerate(self.ctx.pro._commands):
            # Создаем поверхность для ячейки
            original = self.ctx.cmd_images[cmd]
            cell = original.copy()  # Создаем копию, чтобы не изменять оригинал

            if cmd in Command.NO_ARGS:
                pass
            elif cmd in Command.ONE_ARGS:
                x, y, type = self.conf.get_one_args_config(cmd)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=0, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=0, color=0))
                elif type == 2: # value
                    pass

            elif cmd in Command.TWO_ARGS:
                is_above = True
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=2))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

                is_above = False
                num = 0 if is_above else 1
                x, y, type = self.conf.get_two_args_config(cmd, is_above)
                if type == 0: # label
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=-1))
                elif type == 1: # variable
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=0))
                elif type == 2: # value
                    cell.blit(*self.render_text(idx, x=x, y=y, i=num, color=1))

        
            # Добавляем рамку
            pygame.draw.rect(cell, (80, 80, 80), cell.get_rect(), 1)
            
            self.cell_surfaces[idx] = cell

    def render_text(self, id, i=0, x=5, y=0, fsize=16, color=0):
        thumb_size = self.ctx.thumb_size
        padding = self.ctx.padding
        # font = pygame.font.SysFont('Times New Roman', fsize)
        font = pygame.font.SysFont('arial', fsize, bold=True)
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
 
    # def draw_grid(self):
    #     """Рисует сетку с изображениями"""
    #     # Определяем видимые строки
    #     first_row = self.page * 12
    #     last_row = first_row + 12
        
    #     # Параметры позиционирования
    #     cell_size = self.cell_size
    #     padding = self.ctx.padding
    #     offsetW = self.ctx.offsetW
    #     offsetH = self.ctx.offsetH
    #     window_height = self.ctx.window_height
        
    #     # Рисуем номера строк
    #     self._draw_line_numbers(first_row, last_row, offsetH, window_height)
        
    #     # Рисуем видимые ячейки
    #     for row in range(first_row, last_row):
    #         # Нормализуем row для расчета позиции на экране
    #         # Для 1-й страницы: row=0..11, normalized_row=0..11
    #         # Для 2-й страницы: row=12..23, normalized_row=0..11
    #         normalized_row = row % 12  # или row - first_row
            
    #         for col in range(self.cols):
    #             idx = row * self.cols + col
    #             if idx >= len(self.ctx.pro._commands):
    #                 break
                
    #             # Вычисляем позицию, используя нормализованный номер строки
    #             x = padding + col * cell_size + offsetW
    #             y = padding + normalized_row * cell_size + offsetH
                
    #             # Проверяем видимость
    #             if y + self.ctx.thumb_size < 0 or y > window_height:
    #                 continue
                
    #             # Рисуем ячейку из кэша
    #             if idx in self.cell_surfaces:
    #                 self.screen.blit(self.cell_surfaces[idx], (x, y))
        
    
    def _draw_line_numbers(self, first_row, last_row, offsetH, window_height):
        """Рисует номера строк"""
        line_font = pygame.font.SysFont('arial', 16, bold=True)
        padding = self.ctx.padding
        thumb_size = self.ctx.thumb_size
        cell_size = self.cell_size
        k = self.ctx.k_size
        line_number_padding = self.ctx.line_number_padding
        
        for row in range(first_row, last_row):
            normalized_row = row % 12
            y = padding + normalized_row * cell_size + offsetH
            
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
        rel_y = mouse_y - grid_y - self.ctx.offsetH
        
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