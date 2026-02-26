import pygame
import os
import glob
from PIL import Image
import numpy as np
import pygame_gui

from Command import Command
from Programmator import Programmator
from Scrollbar import Scrollbar
from test_binding1 import KeyBindWindow
from InputController import *
from my_lib.GameObjectRenderer import GameObject, GameObjectManager # Импортируем новое

# --- Класс для сетки (будет рисовать команды) ---
class GridObject(GameObject):
    def __init__(self, viewer_context, z_order=1):
        super().__init__(z_order)
        self.ctx = viewer_context # Ссылка на главный класс с данными

    def _draw(self):
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
                
                self.ctx.draw_thumbnail_with_effects(i, x, y)

        self.ctx.scrollbar.draw(self.ctx.screen)

    def _update(self):
        # Обновление, связанное с сеткой (например, скролл)
        pass

    def _execute(self):
        # Логика сетки (проверка hover, клики)
        pass

# --- Класс для верхней панели ---
class TopPanelObject(GameObject):
    def __init__(self, viewer_context, z_order=10):
        super().__init__(z_order)
        self.ctx = viewer_context

    def _draw(self):
        # Рисует панель поверх сетки
        pass

    def _update(self):
        # Обновление, связанное с сеткой (например, скролл)
        pass

    def _execute(self):
        # Логика сетки (проверка hover, клики)
        pass

# --- Класс для UI (pygame_gui) ---
class UIManagerObject(GameObject):
    def __init__(self, viewer_context, z_order=20):
        super().__init__(z_order)
        self.ctx = viewer_context
        self.ui_manager = pygame_gui.UIManager((self.ctx.window_width, self.ctx.window_height))
        self.menu_buttons = [] # Кнопки будем хранить здесь
        self.key_bind_window = None

    def _draw(self):
        self.ui_manager.draw_ui(self.ctx.screen)
        if self.key_bind_window and self.key_bind_window.active:
            self.key_bind_window.draw()

    def _update(self):
        time_delta = self.ctx.clock.tick(60)/1000.0
        self.ui_manager.update(time_delta)

    def _execute(self):
        # Здесь обработка событий pygame_gui, которые приходят из viewer
        pass

    def create_menu_button(self):
        # Создание кнопок с использованием self.ui_manager
        pass

    def open_settings(self):
        if not self.key_bind_window or not self.key_bind_window.active:
            self.key_bind_window = KeyBindWindow(self.ui_manager, self.ctx)

# --- Обновленный ProgrammatorViewer ---
class ProgrammatorViewer(GameObject): # Теперь сам viewer тоже GameObject
    def __init__(self, image_paths, pro: Programmator, k_size=1):
        super().__init__(z_order=0) # Сам viewer ничего не рисует, z_order не важен
        
        # ... (инициализация параметров, загрузка изображений как и раньше) ...
        self.k_size = max(0.8, min(1.5, k_size))
        self.image_paths = image_paths
        self.cols = 16
        self.thumb_size = int(64 * self.k_size)
        # ... остальные параметры ...
        
        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption(f"Image Viewer - {len(self.images)} images")
        self.clock = pygame.time.Clock()
        
        # Загрузка данных
        self.load_images()
        self.cmd_list = pro._commands
        self.pro = pro
        self.create_thumbnails()
        
        # --- СОЗДАЕМ МЕНЕДЖЕРА ---
        self.manager = GameObjectManager()
        
        # --- СОЗДАЕМ И ДОБАВЛЯЕМ ОБЪЕКТЫ ---
        self.grid = GridObject(self, z_order=1)
        self.top_panel = TopPanelObject(self, z_order=10)
        self.ui = UIManagerObject(self, z_order=20)
        
        self.manager.add(self.grid, self.grid.z_order)
        self.manager.add(self.top_panel, self.top_panel.z_order)
        self.manager.add(self.ui, self.ui.z_order)
        
        # Инициализируем кнопки в UI объекте
        self.ui.create_menu_button()

        # ... остальная инициализация (скроллбар, трекеры значений, команды) ...
        # Скроллбар теперь, вероятно, часть GridObject

    def _draw(self):
        # 
        pass

    def _update(self):
        # 
        pass

    def _execute(self):
        # 
        pass

    def run(self):
        """Запускает основной цикл"""
        running = True
        
        while running:
            time_delta = self.clock.tick(60)/1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Обработка событий мыши/клавиатуры
                # Важно: события, влияющие на данные, должны менять состояние self (контекста)
                # Затем manager.run() отрисует все с новыми данными.
                
                # Например, изменение скролла:
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))
                    # Обновить скроллбар в grid объекте
                
                # Передаем события в UI объект для pygame_gui
                self.ui.ui_manager.process_events(event)
                if self.ui.key_bind_window:
                    self.ui.key_bind_window.handle_event(event)
            
            # --- ГЛАВНЫЙ ЦИКЛ МЕНЕДЖЕРА ---
            # 1. Сначала очищаем экран
            self.screen.fill((50, 50, 50))
            
            # 2. Запускаем менеджер (он выполнит _execute, _update, _draw всех объектов)
            self.manager.run()
            
            # 3. Обновляем экран
            pygame.display.flip()
            
            self.clock.tick(30)
        
        pygame.quit()

    # Остальные методы (load_images, create_thumbnails, и т.д.) остаются в основном классе,
    # так как они загружают данные, а не рисуют.
    # Методы, связанные с отрисовкой (draw_grid, draw_top_panel) переносятся в соответствующие объекты.

def get_images(dir_folder = "sprites_standart"):
    # Находим все изображения в папке
    # image_folder = "sprites_standart"
    image_files = glob.glob(os.path.join(dir_folder, "*.png"))
    image_files.sort()
    return image_files

if __name__ == "__name__":
    managerGO = GameObjectManager()

    img_files = get_images()
    encoded_string = "XQAAgACzAAAAAAAAAAAZADAMYCDURSxK8GR5e/2nd+V9B2fs+9LemstWZRQBmMQiE4IOuXqySGdcZtrDkPe00KEs+KiBkaH1Dx0a4GlBU6a90Uy5qp5AHk4BJ9dul//0RfUyVcEDj28w/394ryD97MbhFAMFuVwQPzKLgA=="
    v_k = [0.5, 1, 1.5]

    pro = Programmator()
    pro_view = ProgrammatorViewer(img_files, pro, k_size=v_k[1])
    grid = GridObject(pro_view)

    managerGO.add(pro, 100)
    managerGO.add(pro_view, 1000)
    managerGO.add(grid, 1000)

    running = True
    clock = pygame.Clock    
    
    while running:
        managerGO.run()
        
        clock.tick(30)
        

    pygame.quit()    