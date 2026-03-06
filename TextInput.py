import pygame
import sys
from my_lib.GameObjectRenderer import GameObject


class TextInput(GameObject):
    def __init__(self, ctx, screen, x, y, width, height, max_length=20):
        super().__init__(1000)
        self.ctx = ctx
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.color_inactive = (100, 100, 100)
        self.color_active = (200, 200, 200)
        self.color = self.color_inactive
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.SysFont('arial', 24)
        self.is_active = False
        self.id_cmd = None
        self.num_cmd = 0
        
        # Новые атрибуты для выделения текста
        self.text_selected = False
        self.selection_start = 0
        self.selection_end = 0
        self.cursor_position = 0  # Позиция курсора в тексте

        self.flag_end = False

    def _execute(self):
        pass

    def _update(self):
        if self.is_active and self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

    def _draw(self):
        if self.is_active:
            # Матричный зеленый
            text_color = (0, 255, 255)  # Ярко-зеленый
            glow_color = (0, 150, 0)  # Темно-зеленый для свечения
            
            text_surface = self.font.render(self.text, True, text_color)
            
            # Эффект свечения
            glow_surface = self.font.render(self.text, True, glow_color)

            # center
            x, y = self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2
            text_rect = glow_surface.get_rect(center=(x, y))

            # === ТЕМНАЯ ОБЛАСТЬ ПОД ТЕКСТОМ ===
            # Создаем поверхность для темной области
            text_rect = text_surface.get_rect(center=(x, y))
            padding = 2  # Отступ от текста
            bg_rect = pygame.Rect(
                text_rect.x - padding,
                text_rect.y - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            
            # Рисуем полупрозрачный черный прямоугольник
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)  # Прозрачность (0-255)
            bg_surface.fill((0, 0, 0))
            self.screen.blit(bg_surface, bg_rect)


            self.screen.blit(glow_surface, text_rect)
            text_rect.centerx = x - 1
            text_rect.centery = y - 1
            self.screen.blit(glow_surface, text_rect)
            text_rect.centerx = x + 1
            text_rect.centery = y + 1
            self.screen.blit(glow_surface, text_rect)
            
            # Отрисовка выделенного текста (если есть)
            if self.text_selected and self.active:
                self._draw_selection(x, y, text_surface)
            
            # Основной текст поверх
            text_rect.centerx = x
            text_rect.centery = y
            self.screen.blit(text_surface, text_rect)
            
            # Курсор
            if self.active and self.cursor_visible and not self.text_selected:
                # Вычисляем позицию курсора на основе текущей позиции в тексте
                if self.cursor_position < len(self.text):
                    text_before_cursor = self.text[:self.cursor_position]
                    text_before_surface = self.font.render(text_before_cursor, True, text_color)
                    cursor_offset = text_before_surface.get_width()
                else:
                    cursor_offset = text_surface.get_width()
                
                cursor_x = x - text_surface.get_width() // 2 + cursor_offset
                cursor_y = y - text_surface.get_height() // 2
                cursor_height = text_surface.get_height()
                pygame.draw.line(self.screen, text_color, 
                            (cursor_x, cursor_y), 
                            (cursor_x, cursor_y + cursor_height), 3)
            pygame.display.flip()

    def _draw_selection(self, x, y, text_surface):
        """Отрисовка выделенного текста"""
        if self.selection_start == self.selection_end:
            return
            
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        
        # Получаем поверхности для текста до выделения и выделенного текста
        text_before = self.text[:start]
        selected_text = self.text[start:end]
        
        # Создаем поверхности для расчета позиций
        font = self.font
        before_surface = font.render(text_before, True, (0, 255, 255))
        selected_surface = font.render(selected_text, True, (0, 255, 255))
        
        # Вычисляем позиции
        text_start_x = x - text_surface.get_width() // 2
        text_y = y - text_surface.get_height() // 2
        
        selection_x = text_start_x + before_surface.get_width()
        selection_width = selected_surface.get_width()
        
        # Рисуем прямоугольник выделения
        selection_rect = pygame.Rect(selection_x, text_y, selection_width, text_surface.get_height())
        pygame.draw.rect(self.screen, (0, 100, 0), selection_rect, 2)  # Зеленая рамка выделения
        # заливка полупрозрачным цветом:
        selection_surface = pygame.Surface((selection_width, text_surface.get_height()))
        selection_surface.set_alpha(128)
        selection_surface.fill((0, 255, 0))
        self.screen.blit(selection_surface, (selection_x, text_y))

    def handle_event(self, event, type=0):
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_ESCAPE:
                self.flag_end = True
            elif event.key == pygame.K_RETURN:
                self.ctx.pro._values[self.id_cmd][self.num_cmd] = self.text
                self.ctx.grid.update_cell_image(self.id_cmd, self.ctx.cmd_list[self.id_cmd])
                self.ctx.re_grid = True
                print(f"Введенный текст: {self.text}")
                self.text_selected = False
                self.flag_end = True
            
            elif event.key == pygame.K_BACKSPACE:
                if self.text_selected and self.selection_start != self.selection_end:
                    # Удаляем выделенный текст
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:start] + self.text[end:]
                    self.cursor_position = start
                    self.text_selected = False
                elif self.cursor_position > 0:
                    # Удаляем символ перед курсором
                    self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                    self.cursor_position -= 1
            
            elif event.key == pygame.K_DELETE:
                if self.text_selected and self.selection_start != self.selection_end:
                    # Удаляем выделенный текст
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:start] + self.text[end:]
                    self.cursor_position = start
                    self.text_selected = False
                elif self.cursor_position < len(self.text):
                    # Удаляем символ после курсора
                    self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
            
            elif event.key == pygame.K_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
                    # Снимаем выделение при движении курсора
                    self.text_selected = False
                else:
                    # Снимаем выделение при движении курсора
                    self.text_selected = False
            
            elif event.key == pygame.K_RIGHT:
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
                    # Снимаем выделение при движении курсора
                    self.text_selected = False
                else:
                    # Снимаем выделение при движении курсора
                    self.text_selected = False
            
            elif event.key == pygame.K_HOME:
                self.cursor_position = 0
                self.text_selected = False
            
            elif event.key == pygame.K_END:
                self.cursor_position = len(self.text)
                self.text_selected = False
            
            elif event.scancode == 4 and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Ctrl+A - выделить весь текст
                self.select_all()
            
            else:
                # Ввод символов
                if event.unicode and event.unicode.isprintable():
                    print(type)
                    access = False
                    if (type == 1 or type == 0) and (event.unicode.isalpha() and event.unicode.isascii()):
                        access = True
                    elif (type == 2) and event.unicode.isdigit():
                        access = True
                    if access and self.text_selected and self.selection_start != self.selection_end:
                        # Заменяем выделенный текст
                        start = min(self.selection_start, self.selection_end)
                        end = max(self.selection_start, self.selection_end)
                        self.text = self.text[:start] + event.unicode + self.text[end:]
                        self.cursor_position = start + 1
                        self.text_selected = False
                    elif access and len(self.text) < self.max_length:
                        # Вставляем символ в позицию курсора
                        self.text = self.text[:self.cursor_position] + event.unicode + self.text[self.cursor_position:]
                        self.cursor_position += 1
    
    def _set_cursor_from_mouse(self, mouse_pos):
        """Устанавливает позицию курсора на основе клика мыши"""
        if not self.text:
            self.cursor_position = 0
            return
            
        # Получаем центр поля ввода
        x = self.rect.x + self.rect.width // 2
        y = self.rect.y + self.rect.height // 2
        
        text_surface = self.font.render(self.text, True, (0, 255, 255))
        text_start_x = x - text_surface.get_width() // 2
        
        # Определяем, на какой символ кликнули
        click_x = mouse_pos[0]
        
        if click_x <= text_start_x:
            self.cursor_position = 0
        elif click_x >= text_start_x + text_surface.get_width():
            self.cursor_position = len(self.text)
        else:
            # Ищем позицию символа
            for i in range(len(self.text) + 1):
                text_before = self.text[:i]
                before_surface = self.font.render(text_before, True, (0, 255, 255))
                char_x = text_start_x + before_surface.get_width()
                
                if i == len(self.text):
                    self.cursor_position = i
                    break
                    
                next_char_x = text_start_x + self.font.render(self.text[:i+1], True, (0, 255, 255)).get_width()
                
                if click_x <= char_x + (next_char_x - char_x) // 2:
                    self.cursor_position = i
                    break
    
    def select_all(self):
        """Выделяет весь текст"""
        if self.text:
            self.text_selected = True
            self.selection_start = 0
            self.selection_end = len(self.text)
            self.cursor_position = len(self.text)

    def get_selected_text(self):
        """Возвращает выделенный текст"""
        if self.text_selected and self.selection_start != self.selection_end:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            return self.text[start:end]
        return ""

    def set_max_length(self, num):
        self.max_length = num

    def set_rect(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def on_active(self, event, index, n, text):
        self.id_cmd = index
        self.num_cmd = n
        self.text = text
        self.flag_end = False
        self.is_active = True
        self.select_all()

        x, y, type = self.ctx.get_cmd_data(index, n)
        self.handle_event(event, type)
    
    def off_active(self):
        self.flag_end = False
        self.id_cmd = None
        self.is_active = False
        self.text_selected = False
        


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Создаем фиктивный контекст для тестирования
    class DummyContext:
        class Pro:
            _values = {}
        pro = Pro()
        
        class Grid:
            def update_cell_image(self, id_cmd, cmd):
                pass
        grid = Grid()
        cmd_list = {}
        re_grid = False

    ctx = DummyContext()
    input_field = TextInput(ctx, screen, 400, 300, 200, 40, 20)
    input_field.id_cmd = 0
    input_field.on_active()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input_field.handle_event(event)
        
        input_field._update()
        
        screen.fill((30, 30, 30))
        input_field._draw()
        
        pygame.display.flip()
        clock.tick(60)