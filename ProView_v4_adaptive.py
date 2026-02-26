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

class ValueTracker:
    def __init__(self, initial_value=None):
        self.current = initial_value
        self.previous = None
        self.changed = False
    
    def update(self, new_value):
        if new_value != self.current:
            self.previous = self.current
            self.current = new_value
            self.changed = True
        else:
            self.changed = False

class ProgrammatorViewer:
    def __init__(self, image_paths, cmd_list, k_size=1):
        """
        Просмотрщик изображений в сетке с помощью Pygame
        image_paths: список путей к изображениям
        cols: количество столбцов в сетке
        thumb_size: размер миниатюр (в пикселях)
        padding: отступ между изображениями
        """
        self.k_size = max(0.8, min(1.5, k_size))
        self.image_paths = image_paths
        self.cols = 16
        self.thumb_size = int(64 * self.k_size)
        self.padding = int(8 * self.k_size)
        self.offsetW = int(64 * self.k_size)
        self.offsetH = int(32 * self.k_size)
        self.offsetScrll = int(16 * self.k_size)
        
        self.font_size = int(24 * self.k_size)
        self.line_font_size = int(28 * self.k_size)
        self.line_number_padding = int(0 * self.k_size)
        self.font_padding = int(-8 * self.k_size)
        self.need_redraw = True
        self.selected = ValueTracker()
        self.hovered = ValueTracker()
        
        # Загружаем все изображения
        self.images = []
        self.image_names = []
        self.cmd_images = {}
        self.load_images()
        self.cmd_list = cmd_list
        
        # Рассчитываем размер окна
        self.rows = (len(self.cmd_list) + self.cols - 1) // self.cols
        self.window_width = self.cols * (self.thumb_size + self.padding) + self.padding + self.offsetW + self.offsetScrll
        #self.window_height = min(800, self.rows * (self.thumb_size + self.padding) + self.padding)
        self.window_height = max(430, int((1080 / 1.5) * self.k_size))
        
        ### Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption(f"Image Viewer - {len(self.images)} images")
        self.clock = pygame.time.Clock()
        
        ### Для скроллинга
        self.scroll_y = 0
        self.max_scroll = max(0, self.rows * (self.thumb_size + self.padding) + self.padding - self.window_height)

        self.scrollbar = Scrollbar(
            x=self.window_width - (20 * self.k_size),  # Позиция справа
            y=self.offsetH,
            width=(15 * self.k_size),
            height=self.window_height - self.offsetH,
            content_height=self.rows * (self.thumb_size + self.padding) + self.padding,
            view_height=self.window_height - self.offsetH
        )

        ### Для бинда клавиш
        self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        self.key_bind_window = None 

        # Cловарь для хранения функций
        self.key_functions = {
            'ВВЕРХ': self.scroll_up,
            'ВНИЗ': self.scroll_down,
            'ВЛЕВО': None,  # Пока без функции
            'ВПРАВО': None,
            'ДЕЙСТВИЕ': self.select_current,
            'МЕНЮ': self.open_settings
        }

        # значения по умолчанию
        self.key_bindings = {
            'ВВЕРХ': pygame.K_UP,
            'ВНИЗ': pygame.K_DOWN,
            'ВЛЕВО': pygame.K_LEFT,
            'ВПРАВО': pygame.K_RIGHT,
            'ДЕЙСТВИЕ': pygame.K_SPACE,
            'МЕНЮ': pygame.K_ESCAPE
        }
        
        ### Создаем поверхности для миниатюр
        self.thumbnails = []
        self.create_thumbnails()
        
        # Рассчитываем позиции
        self.calculate_positions()

    def handle_resize(self, new_width, new_height):
        """Обработка изменения размера окна"""
        print(f"Изменение размера: {new_width}x{new_height}")
        
        # Обновляем размеры окна
        self.window_width = new_width
        self.window_height = new_height
        
        # Пересоздаем окно с новым размером
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )
        
        # Обновляем параметры адаптивности
        
        # Обновляем позицию скроллбара
        self.scrollbar.x = self.window_width - (20 * self.k_size)
        self.scrollbar.height = self.window_height
        self.scrollbar.update_size(
            self.window_height,
            self.rows * (self.thumb_size + self.padding) + self.padding
        )
        
        # Пересчитываем максимальный скролл
        self.max_scroll = max(0, self.rows * (self.thumb_size + self.padding) + 
                            self.padding - self.window_height)
        self.scroll_y = min(self.scroll_y, self.max_scroll)
        
        # Обновляем UI менеджер
        self.ui_manager.set_window_resolution((self.window_width, self.window_height))
        
        self.need_redraw = True

    # Добавьте методы-функции:
    def scroll_up(self):
        self.scroll_y = max(0, self.scroll_y - 50)
        self.scrollbar.scroll_y = self.scroll_y
        self.scrollbar.update_handle()
        self.need_redraw = True
        print("Скролл вверх")

    def scroll_down(self):
        self.scroll_y = min(self.max_scroll, self.scroll_y + 50)
        self.scrollbar.scroll_y = self.scroll_y
        self.scrollbar.update_handle()
        self.need_redraw = True
        print("Скролл вниз")

    def select_current(self):
        if self.selected.current is not None:
            print(f"Выбрана команда: {self.cmd_list[self.selected.current]}")
            # Здесь ваша логика выбора

    def input(self):
        pass

    def open_settings(self):
        if not self.key_bind_window or not self.key_bind_window.active:
            self.open_key_bindings()
        else:
            # Если окно уже открыто, закрываем его
            self.key_bind_window.active = False
            self.key_bind_window.window.kill()
            self.key_bind_window = None
        self.need_redraw = True
        #pygame.event.post(pygame.event.Event(pygame.QUIT))

    def open_key_bindings(self):
        """Открывает окно настройки горячих клавиш"""
        if self.key_bind_window and self.key_bind_window.active:
            return  # Если уже открыто, ничего не делаем
        
        self.key_bind_window = KeyBindWindow(self.ui_manager, self)

    def calculate_positions(self):
        """
        Рассчитывает позиции для всех миниатюр
        Сохраняет словарь {i: (x, y)} для всех индексов
        """
        self.positions = {}
        
        for row in range(self.rows):
            for col in range(self.cols):
                i = row * self.cols + col
                if i >= len(self.thumbnails):
                    break
                
                x = self.padding + col * (self.thumb_size + self.padding) + self.offsetW
                y = self.padding + row * (self.thumb_size + self.padding) + self.offsetH
                
                self.positions[i] = (x, y)
        
    def load_images(self):
        """Загружает изображения с помощью PIL"""
        for path in self.image_paths:
            try:
                img = Image.open(path)
                self.images.append(img)
                print(f"Загружено: {os.path.basename(path)}")
                # Сохраняем имя файла без пути
                name = os.path.splitext(os.path.basename(path))[0]
                self.image_names.append(name)
            except Exception as e:
                print(f"Ошибка загрузки {path}: {e}")
        
    def pil_to_pygame(self, pil_image):
        """Конвертирует PIL Image в pygame Surface"""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        img_array = np.array(pil_image)
        surface = pygame.surfarray.make_surface(img_array.swapaxes(0, 1))
        return surface
    
    def create_thumbnails(self):
        """Создает миниатюры для всех изображений"""
        i = 0
        for img in self.images:
            img_copy = img.copy()
            img_copy.thumbnail((self.thumb_size, self.thumb_size), Image.Resampling.LANCZOS)
            
            thumb = Image.new('RGB', (self.thumb_size, self.thumb_size), (255, 255, 255))
            
            offset_x = (self.thumb_size - img_copy.width) // 2
            offset_y = (self.thumb_size - img_copy.height) // 2
            thumb.paste(img_copy, (offset_x, offset_y))
            
            surface = self.pil_to_pygame(thumb)
            self.thumbnails.append(surface)

            try:
                cmd = Command[self.image_names[i]]
                self.cmd_images[cmd] = surface
            except KeyError:
                # Пропустить или использовать значение по умолчанию
                print(f"Команда {self.image_names[i]} не найдена, пропускаем")
                # или
                self.cmd_images[Command.EMPTY] = surface  # значение по умолчанию
            i += 1
    
    def update_visible_range(self):
        """Обновляет диапазон видимых строк"""
        self.first_visible_row = max(0, int(self.scroll_y // (self.thumb_size + self.padding)))
        visible_rows = self.window_height // (self.thumb_size + self.padding) + 2
        self.last_visible_row = min(self.rows, self.first_visible_row + int(visible_rows))

    def draw_thumbnail_with_effects(self, index, x, y):
        """Рисует одну миниатюру с рамкой и номером"""
        # Рисуем миниатюру
        #self.screen.blit(self.thumbnails[index], (x, y))
        cmd = self.cmd_list[index]
        self.screen.blit(self.cmd_images[cmd], (x, y))
        
        # Рисуем номер
        font = pygame.font.Font(None, self.font_size)
        text = font.render(str(index+1), True, (255, 255, 255))
        self.screen.blit(text, (x+self.font_padding, y+self.font_padding))

    def draw_grid(self):
        """Рисует сетку с изображениями"""
        # Очищаем экран
        self.screen.fill((50, 50, 50))
        self.update_visible_range()
        
        # Определяем шрифт для номеров строк
        line_font = pygame.font.Font(None, self.line_font_size)
        
        # Рисуем номера строк (только для видимых строк)
        for row in range(self.first_visible_row, self.last_visible_row):
            y = self.padding + row * (self.thumb_size + self.padding) + self.offsetH - self.scroll_y
            
            if y + self.thumb_size > 0 and y < self.window_height:
                line_number_x = self.padding + self.line_number_padding
                line_number_y = y +  self.thumb_size // 2
                
                if row < 9:
                    pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * self.k_size), line_number_y - (12 * self.k_size), (30 * self.k_size), (26 * self.k_size)), border_top_right_radius=int(5 * self.k_size))
                elif row < 99:
                    pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * self.k_size), line_number_y - (12 * self.k_size), (40 * self.k_size), (26 * self.k_size)), border_top_right_radius=int(5 * self.k_size))
                else:
                    pygame.draw.rect(self.screen, (70, 70, 70), 
                               (line_number_x - (5 * self.k_size), line_number_y - (12 * self.k_size), (45 * self.k_size), (26 * self.k_size)), border_top_right_radius=int(5 * self.k_size))
                
                line_text = line_font.render(f"{row + 1}", True, (200, 200, 200))
                self.screen.blit(line_text, (line_number_x, line_number_y - (8 * self.k_size)))
        
        # Рисуем только видимые миниатюры
        for row in range(self.first_visible_row, self.last_visible_row):
            for col in range(self.cols):
                i = row * self.cols + col
                if i >= len(self.cmd_list):
                    break
                
                x = self.padding + col * (self.thumb_size + self.padding) + self.offsetW
                y = self.padding + row * (self.thumb_size + self.padding) + self.offsetH - self.scroll_y
                
                if y + self.thumb_size < 0 or y > self.window_height:
                    continue
                
                self.draw_thumbnail_with_effects(i, x, y)

        self.scrollbar.draw(self.screen)

        # Рисуем UI поверх всего
        self.ui_manager.draw_ui(self.screen)
    
    def run(self):
        """Запускает основной цикл"""
        running = True
        
        while running:
            # Проверяем hover
            new_hovered = self.check_hover()
            time_delta = self.clock.tick(60)/1000.0
            
            # Обновляем hovered если изменился
            if new_hovered != self.hovered.current:
                self.hovered.update(new_hovered)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                
                elif event.type == pygame.KEYDOWN:
                    print(f"Нажата клавиша: {pygame.key.name(event.key)}")  # Отладка
                    print(f"Текущие назначения: {self.key_bindings}")  # Отладка
                    
                    # Проверяем все назначенные клавиши
                    for action, key in self.key_bindings.items():
                        if event.key == key:
                            print(f"Найдено действие: {action}")  # Отладка
                            if self.key_functions.get(action):
                                self.key_functions[action]()
                                print(f"Выполнено: {action}")  # Отладка
                                break
                    else:  # Если ни одна клавиша не найдена в назначениях
                        # Старая обработка для клавиш без назначений
                        if event.key == pygame.K_ESCAPE:
                            running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        if self.selected.current != new_hovered:
                            self.selected.update(new_hovered)
                    
                    elif event.button in (4, 5):  # Колесико мыши
                        old_scroll = self.scroll_y
                        if event.button == 4:
                            self.scroll_y = max(0, self.scroll_y - 30)
                        else:
                            self.scroll_y = min(self.max_scroll, self.scroll_y + 30)
                        if old_scroll != self.scroll_y:
                            self.need_redraw = True

                # Обработка событий pygame_gui
                if self.key_bind_window:
                    self.key_bind_window.handle_event(event)
                self.ui_manager.process_events(event)

                if self.scrollbar.handle_event(event):
                    self.scroll_y = self.scrollbar.scroll_y
                    self.need_redraw = True
                    continue  # Пропускаем остальные обработчики для этого события
            
            # Обновляем pygame_gui
            self.ui_manager.update(time_delta)  

            if self.scroll_y != self.scrollbar.scroll_y:
                self.scrollbar.scroll_y = self.scroll_y
                self.scrollbar.update_handle()
                self.need_redraw = True

            # Рисуем
            if self.need_redraw or (self.key_bind_window and self.key_bind_window.active):
                self.draw_grid()
                
                # Рисуем окно настроек поверх
                if self.key_bind_window and self.key_bind_window.active:
                    self.key_bind_window.draw()
                
                pygame.display.flip()
                self.need_redraw = False
            
            self.clock.tick(30)
        
        pygame.quit()

    def check_hover(self):
        """Проверяет hover математически, без перебора"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Вычисляем возможный ряд и колонку по позиции мыши
        rel_x = mouse_x - self.padding - self.offsetW
        rel_y = mouse_y - self.padding + self.scroll_y
        
        if rel_x < 0 or rel_y < 0:
            return None
        
        col = rel_x // (self.thumb_size + self.padding)
        row = rel_y // (self.thumb_size + self.padding)
        
        # Проверяем границы
        if col >= self.cols or row >= self.rows:
            return None
        
        index = row * self.cols + col
        if index >= len(self.cmd_list):
            return None
        
        # Проверяем, точно ли мышь внутри миниатюры (а не в отступах)
        x = self.padding + col * (self.thumb_size + self.padding) + self.offsetW
        y = self.padding + row * (self.thumb_size + self.padding) - self.scroll_y
        
        if (x <= mouse_x <= x + self.thumb_size and 
            y <= mouse_y <= y + self.thumb_size):
            return index
        
        return None

# Использование
if __name__ == "__main__":
    # Находим все изображения в папке
    image_folder = "sprites_standart"
    image_files = glob.glob(os.path.join(image_folder, "*.png"))
    image_files.sort()
    cmd_list = list(Command)

    pro = Programmator()
    
    if not image_files:
        print(f"Нет изображений в папке {image_folder}")
    else:
        print(f"Найдено {len(image_files)} изображений")
        viewer = ProgrammatorViewer(image_files, pro.getCommands(), k_size=1.2)
        viewer.run()