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

# --- Класс для сетки (будет рисовать команды) ---
class GridObject(GameObject):
    def __init__(self, viewer_context, z_order=1):
        super().__init__(z_order)
        print(f"[DEBUG] GridObject.__init__: viewer_context={viewer_context}, z_order={z_order}")
        self.ctx = viewer_context # Ссылка на главный класс с данными
        self.screen = self.ctx.screen
        self.isdraw = self.ctx.need_redraw

    def _draw(self):
        if self.ctx.need_redraw:
            self.draw_grid()
            pygame.display.flip()
            self.ctx.need_redraw = False

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

# --- Класс для верхней панели ---
class TopPanelObject(GameObject):
    def __init__(self, viewer_context, z_order=10):
        super().__init__(z_order)
        print(f"[DEBUG] TopPanelObject.__init__: viewer_context={viewer_context}, z_order={z_order}")
        self.ctx = viewer_context
        self.screen = viewer_context.screen

    def _draw(self):
        # Рисует панель поверх сетки
        self.draw_top_panel()

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
        text = font.render(f"Привет от Majin'а. Команд: {len(self.ctx.cmd_list)}", True, (200, 200, 200))
        text_x = self.ctx.window_width - text.get_width() - self.ctx.padding * 2
        text_y = (self.ctx.panel_height - text.get_height()) // 2
        self.screen.blit(text, (text_x, text_y))

# --- Класс для UI (pygame_gui) ---
class UIManagerObject(GameObject):
    def __init__(self, viewer_context, z_order=20):
        super().__init__(z_order)
        print(f"[DEBUG] UIManagerObject.__init__: viewer_context={viewer_context}, z_order={z_order}")
        self.ctx = viewer_context
        self.ui_manager = pygame_gui.UIManager((self.ctx.window_width, self.ctx.window_height))
        self.menu_buttons = [] # Кнопки будем хранить здесь
        self.key_bind_window = None
        self.create_menu_button()

    def _draw(self):
        if self.ctx.menu_need_redraw:
            # Рисуем UI поверх всего
            self.ui_manager.draw_ui(self.ctx.screen)

            pygame.display.flip()
            self.ctx.menu_need_redraw = False
        if self.key_bind_window and self.key_bind_window.active:
            self.key_bind_window.draw()

    def _update(self):
        time_delta = self.ctx.clock.tick(60)/1000.0
        self.ui_manager.update(time_delta)

    def _execute(self):
        # Здесь обработка событий pygame_gui, которые приходят из viewer
        pass

    def create_menu_button(self):
        """Создание нескольких кнопок на панели"""
        print(f"[DEBUG] UIManagerObject.create_menu_button: создание кнопок")
        button_width = int(100 * self.ctx.k_size)
        button_height = int(30 * self.ctx.k_size)
        button_margin = int(10 * self.ctx.k_size)
        
        self.menu_buttons = []
        
        # Кнопка "Меню"
        btn1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.ctx.padding, 
                (self.ctx.panel_height - button_height) // 2, 
                button_width, 
                button_height
            ),
            text="Меню",
            manager=self.ui_manager
        )
        self.menu_buttons.append(btn1)
        
        # Кнопка "Настройки"
        btn2 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.ctx.padding + button_width + button_margin, 
                (self.ctx.panel_height - button_height) // 2, 
                button_width, 
                button_height
            ),
            text='Настройки',
            manager=self.ui_manager
        )
        self.menu_buttons.append(btn2)
        
        # Кнопка "Помощь"
        btn3 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.ctx.padding + (button_width + button_margin) * 2, 
                (self.ctx.panel_height - button_height) // 2, 
                button_width, 
                button_height
            ),
            text='Помощь',
            manager=self.ui_manager
        )
        self.menu_buttons.append(btn3)
        print(f"[DEBUG] UIManagerObject.create_menu_button: создано {len(self.menu_buttons)} кнопок")

    def open_settings(self):
        """Открывает окно настройки горячих клавиш"""
        print(f"[DEBUG] UIManagerObject.open_settings: открытие окна настроек")
        if self.key_bind_window and self.key_bind_window.active:
            return
        
        self.key_bind_window = KeyBindWindow(self.ui_manager, self)

# --- Обновленный ProgrammatorViewer ---
class ProgrammatorViewer(GameObject): # Теперь сам viewer тоже GameObject
    """
        Просмотрщик изображений в сетке с помощью Pygame
        image_paths: список путей к изображениям
        cols: количество столбцов в сетке
        thumb_size: размер миниатюр (в пикселях)
        padding: отступ между изображениями
    """
    def __init__(self, screen, image_paths, pro: Programmator, k_size=1):
        super().__init__(z_order=0)
        print(f"[DEBUG] ProgrammatorViewer.__init__: начало инициализации")
        
        # === 1. Базовые параметры ===
        self.k_size = max(0.8, min(1.5, k_size))
        self.image_paths = image_paths
        self.pro = pro
        self.cmd_list = pro._commands
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        print(f"[DEBUG] ProgrammatorViewer: k_size={self.k_size}, команд={len(self.cmd_list)}")
        
        # === 2. UI размеры и константы ===
        self._init_ui_dimensions()
        
        # === 3. Состояние и трекеры ===
        self._init_state_trackers()
        
        # === 4. Загрузка ресурсов ===
        self._init_resources()
        
        # === 7. Команды и фасад ===
        self._init_commands_and_facade()
        
        # === 8. UI элементы (pygame_gui) ===
        self._init_ui_elements()
        
        # === 9. Финальные вычисления ===
        self._init_final_calculations()
        
        # === 10. Создание менеджера и добавление объектов ===
        self._init_manager()
        
        print(f"[DEBUG] ProgrammatorViewer.__init__: инициализация завершена")

    def _draw(self):
        # Очищаем экран
        self.screen.fill((50, 50, 50))

    def _update(self):
        # Обновление
        pass

    def _execute(self):
        # Основной цикл обработки
        self.run()
        self.manager.run()
        
    def run(self):
        new_hovered = self.check_hover()
        time_delta = self.clock.tick(60)/1000.0
        
        # Обновляем hovered если изменился
        if new_hovered != self.hovered.current:
            self.hovered.update(new_hovered)
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(f"[DEBUG] Получен сигнал QUIT")
                return False  # Сигнал для выхода
                
            # Обработка событий кнопок UI
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    print(f"[DEBUG] Нажата кнопка UI")
                    if len(self.ui.menu_buttons) > 0 and event.ui_element == self.ui.menu_buttons[0]:
                        self.on_menu_click()
                    elif len(self.ui.menu_buttons) > 1 and event.ui_element == self.ui.menu_buttons[1]:
                        print("[DEBUG] Нажата кнопка Настройки")
                        self.open_settings()
            
            # Обработка клавиш
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                print(f"[DEBUG] Событие клавиши: {event.key}")
                self.key_facade.handle_event(event)
                
            # Обработка мыши
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"[DEBUG] Нажатие мыши: кнопка {event.button}")
                if event.button == 1:  # Левая кнопка мыши
                    if self.selected.current != new_hovered:
                        self.selected.update(new_hovered)
                        print(f"[DEBUG] Выбран элемент: {new_hovered}")
                
                elif event.button in (4, 5):  # Колесико мыши
                    old_scroll = self.scroll_y
                    if event.button == 4:
                        self.scroll_y = max(0, self.scroll_y - 30)
                    else:
                        self.scroll_y = min(self.max_scroll, self.scroll_y + 30)
                    if old_scroll != self.scroll_y:
                        self.re_grid = True
                        print(f"[DEBUG] Скролл изменен: {self.scroll_y}")
            
            # Обработка событий scrollbar
            if hasattr(self, 'scrollbar') and self.scrollbar.handle_event(event):
                self.scroll_y = self.scrollbar.scroll_y
                self.re_grid = True
                print(f"[DEBUG] Скроллбар обновлен: {self.scroll_y}")
            
            # Обработка событий окна настроек
            if self.ui.key_bind_window:
                self.ui.key_bind_window.handle_event(event)
            
            # Обработка событий pygame_gui
            self.ui.ui_manager.process_events(event)
        
        # Обновляем pygame_gui
        self.ui.ui_manager.update(time_delta)
        
        # Синхронизация скролла
        if self.scroll_y != self.scrollbar.scroll_y:
            self.scrollbar.scroll_y = self.scroll_y
            self.scrollbar.update_handle()
            self.re_grid = True
        
        return True  # Продолжаем работу

    def _init_ui_dimensions(self):
        """Инициализация UI размеров"""
        print(f"[DEBUG] _init_ui_dimensions")
        self.window_width, self.window_height = self.screen.get_size()
        print(f"[DEBUG] Размер окна: {self.window_width}x{self.window_height}")
        
        self.thumb_size = int(64 * self.k_size)
        self.padding = int(8 * self.k_size)
        self.offsetW = int(64 * self.k_size)
        self.offsetH = int(40 * self.k_size)
        self.offsetScrll = int(16 * self.k_size)
        self.panel_height = int(32 * self.k_size)
        
        # Размеры шрифтов
        self.font_size = int(24 * self.k_size)
        self.line_font_size = int(28 * self.k_size)
        self.line_number_padding = int(0 * self.k_size)
        self.font_padding = int(-8 * self.k_size)
        
        print(f"[DEBUG] thumb_size={self.thumb_size}, panel_height={self.panel_height}")

    def _init_state_trackers(self):
        """Инициализация трекеров состояния"""
        print(f"[DEBUG] _init_state_trackers")
        self.re_grid = True
        self.re_ui = True
        self.re_top = True

        self.selected = ValueTracker()
        self.hovered = ValueTracker()
        self.scroll_y = 0

    def _init_resources(self):
        """Загрузка изображений и ресурсов"""
        print(f"[DEBUG] _init_resources: загрузка изображений")
        self.images = []
        self.image_names = []
        self.cmd_images = {}
        self.load_images()
        
        self.cols = 16
        self.rows = (len(self.cmd_list) + self.cols - 1) // self.cols
        print(f"[DEBUG] Сетка: {self.cols} колонок, {self.rows} строк")

    def _init_commands_and_facade(self):
        """Инициализация команд и фасада для клавиш"""
        print(f"[DEBUG] _init_commands_and_facade")

        self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        self.key_bind_window = None 
        
        # Команды
        self._create_commands()
        
        # Фасад
        self.key_facade = KeyInputFacade()
        self._setup_key_facade()
        
        # Словарь для обратной совместимости
        self.key_functions = {
            'ВВЕРХ': self.scroll_up,
            'ВНИЗ': self.scroll_down,
            'ВЛЕВО': None,
            'ВПРАВО': None,
            'ДЕЙСТВИЕ': self.select_current,
            'МЕНЮ': self.open_settings
        }
        
        self.key_bindings = {
            'ВВЕРХ': pygame.K_UP,
            'ВНИЗ': pygame.K_DOWN,
            'ВЛЕВО': pygame.K_LEFT,
            'ВПРАВО': pygame.K_RIGHT,
            'ДЕЙСТВИЕ': pygame.K_SPACE,
            'МЕНЮ': pygame.K_ESCAPE
        }

    def _init_ui_elements(self):
        """Инициализация UI элементов (будет создано в UIManagerObject)"""
        print(f"[DEBUG] _init_ui_elements")
        # UI элементы будут созданы в UIManagerObject
        pass

    def _init_final_calculations(self):
        """Финальные вычисления и создание поверхностей"""
        print(f"[DEBUG] _init_final_calculations")
        self.thumbnails = []
        self.create_thumbnails()
        self.calculate_positions()
        
        # Инициализация скроллбара
        total_content_height = self.rows * (self.thumb_size + self.padding) + self.padding
        self.max_scroll = max(0, total_content_height - (self.window_height - self.offsetH))
        
        self.scrollbar = Scrollbar(
            x=self.window_width - (20 * self.k_size),
            y=self.offsetH,
            width=(15 * self.k_size),
            height=self.window_height - self.offsetH,
            content_height=total_content_height,
            view_height=self.window_height - self.offsetH
        )
        print(f"[DEBUG] Скроллбар создан: max_scroll={self.max_scroll}")

    def _init_manager(self):
        """Создание менеджера и добавление объектов"""
        print(f"[DEBUG] _init_manager: создание менеджера объектов")
        
        # --- СОЗДАЕМ МЕНЕДЖЕРА ---
        self.manager = GameObjectManager()
        
        # --- СОЗДАЕМ И ДОБАВЛЯЕМ ОБЪЕКТЫ ---
        self.grid = GridObject(self, z_order=1)
        self.top_panel = TopPanelObject(self, z_order=10)
        self.ui = UIManagerObject(self, z_order=20)
        
        self.manager.add(self.grid, self.grid.z_order)
        self.manager.add(self.ui, self.ui.z_order)
        self.manager.add(self.top_panel, self.top_panel.z_order)

    def check_hover(self):
        """Проверяет hover математически, без перебора"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Проверяем, не наведена ли мышь на область кнопок меню
        if mouse_y < self.panel_height:
            self.re_ui = True
            return None
        
        # Вычисляем возможный ряд и колонку по позиции мыши
        rel_x = mouse_x - self.padding - self.offsetW
        rel_y = mouse_y - self.padding + self.scroll_y - self.offsetH
        
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
        y = self.padding + row * (self.thumb_size + self.padding) - self.scroll_y + self.offsetH
        
        if (x <= mouse_x <= x + self.thumb_size and 
            y <= mouse_y <= y + self.thumb_size):
            return index
        
        return None

    def on_menu_click(self):
        """Обработчик нажатия на кнопку меню"""
        print("[DEBUG] on_menu_click: кнопка меню нажата!")
        self.open_settings()

    def update_visible_range(self):
        """Обновляет диапазон видимых строк"""
        self.first_visible_row = max(0, int(self.scroll_y // (self.thumb_size + self.padding)))
        visible_rows = self.window_height // (self.thumb_size + self.padding) + 2
        self.last_visible_row = min(self.rows, self.first_visible_row + int(visible_rows))
        # print(f"[DEBUG] Видимые строки: {self.first_visible_row}-{self.last_visible_row}")

    def copy_to_clipboard(self):
        """Копирование в буфер обмена"""
        print("[DEBUG] copy_to_clipboard вызван!")
        try:
            pygame.scrap.init()
            pygame.scrap.put_text(self.pro.getEncode())
            print("[DEBUG] Скопировано в буфер обмена!")
        except Exception as e:
            print(f"[DEBUG] Ошибка копирования: {e}")

    def paste_from_clipboard(self):
        """Вставка из буфера обмена"""
        print("[DEBUG] paste_from_clipboard вызван!")
        try:
            pygame.scrap.init()
            clipboard_text = pygame.scrap.get_text()
            if clipboard_text:
                print(f"[DEBUG] Текст из буфера: {clipboard_text[:50]}...")
                self.pro.copy(clipboard_text)
                self.update_from_pro()
                self.re_grid = True
            else:
                print("[DEBUG] Буфер обмена пуст или содержит не текст")
        except Exception as e:
            print(f"[DEBUG] Ошибка вставки: {e}")

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
        
        print(f"[DEBUG] Рассчитано позиций: {len(self.positions)}")
        
    def load_images(self):
        """Загружает изображения с помощью PIL"""
        print(f"[DEBUG] load_images: загрузка {len(self.image_paths)} изображений")
        for path in self.image_paths:
            try:
                img = Image.open(path)
                self.images.append(img)
                # Сохраняем имя файла без пути
                name = os.path.splitext(os.path.basename(path))[0]
                self.image_names.append(name)
                print(f"[DEBUG] Загружено: {name}")
            except Exception as e:
                print(f"[DEBUG] Ошибка загрузки {path}: {e}")
        
        print(f"[DEBUG] Всего загружено изображений: {len(self.images)}")
        
    def pil_to_pygame(self, pil_image):
        """Конвертирует PIL Image в pygame Surface"""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        img_array = np.array(pil_image)
        surface = pygame.surfarray.make_surface(img_array.swapaxes(0, 1))
        return surface
    
    def create_thumbnails(self):
        """Создает миниатюры для всех изображений"""
        print(f"[DEBUG] create_thumbnails: создание миниатюр")
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
                print(f"[DEBUG] Команда {cmd} связана с изображением {self.image_names[i]}")
            except KeyError:
                print(f"[DEBUG] Команда {self.image_names[i]} не найдена в Command")
                # Используем значение по умолчанию
                if hasattr(Command, 'EMPTY'):
                    self.cmd_images[Command.EMPTY] = surface
            i += 1
        
        print(f"[DEBUG] Создано миниатюр: {len(self.thumbnails)}")

    def open_settings(self):
        """Открывает окно настройки горячих клавиш"""
        print("[DEBUG] open_settings: открытие окна настроек")
        if self.ui.key_bind_window and self.ui.key_bind_window.active:
            return
        
        self.ui.key_bind_window = KeyBindWindow(self.ui.ui_manager, self)

    def scroll_up(self):
        self.scroll_y = max(0, self.scroll_y - 50)
        if hasattr(self, 'scrollbar'):
            self.scrollbar.scroll_y = self.scroll_y
            self.scrollbar.update_handle()
        self.re_grid = True
        print(f"[DEBUG] scroll_up: {self.scroll_y}")

    def scroll_down(self):
        self.scroll_y = min(self.max_scroll, self.scroll_y + 50)
        if hasattr(self, 'scrollbar'):
            self.scrollbar.scroll_y = self.scroll_y
            self.scrollbar.update_handle()
        self.re_grid = True
        print(f"[DEBUG] scroll_down: {self.scroll_y}")

    def select_current(self):
        if self.selected.current is not None:
            print(f"[DEBUG] select_current: выбрана команда {self.cmd_list[self.selected.current]}")

    def update_from_pro(self):
        """
        Обновляет все зависимости после изменения self.pro
        Вызывать после изменения команд в Programmator
        """
        print(f"[DEBUG] update_from_pro: обновление из Programmator")
        
        # Обновляем список команд
        self.cmd_list = self.pro._commands
        
        # Пересчитываем количество строк
        new_rows = (len(self.cmd_list) + self.cols - 1) // self.cols
        
        # Проверяем, изменилось ли количество строк
        if new_rows != self.rows:
            self.rows = new_rows
            print(f"[DEBUG] Количество строк изменилось: {self.rows}")
            
            # Пересчитываем максимальный скролл
            total_content_height = self.rows * (self.thumb_size + self.padding) + self.padding
            self.max_scroll = max(0, total_content_height - (self.window_height - self.offsetH))
            
            # Корректируем текущий скролл, если он вышел за пределы
            self.scroll_y = min(self.scroll_y, self.max_scroll)
            
            # Обновляем скроллбар
            if hasattr(self, 'scrollbar'):
                self.scrollbar.content_height = total_content_height
                self.scrollbar.view_height = self.window_height - self.offsetH
                self.scrollbar.scroll_y = self.scroll_y
                self.scrollbar.update_handle()
        
        # Пересчитываем позиции (на случай изменения размеров)
        self.calculate_positions()
        
        # Отмечаем необходимость перерисовки
        self.re_grid = True
        
        print(f"[DEBUG] Программа обновлена. Команд: {len(self.cmd_list)}, строк: {self.rows}")

    def _create_commands(self):
        """Создание всех команд"""
        print(f"[DEBUG] _create_commands: создание команд")
        self.scroll_up_cmd = ScrollUpCommand(self)
        self.scroll_down_cmd = ScrollDownCommand(self)
        self.select_cmd = SelectCommand(self)
        self.open_settings_cmd = OpenSettingsCommand(self)
        self.copy_clipboard_cmd = CopyToClipboardCommand(self)
        self.paste_clipboard_cmd = PasteFromClipboardCommand(self)
    
    def _setup_key_facade(self):
        """Настройка привязки клавиш к командам через фасад"""
        print(f"[DEBUG] _setup_key_facade: настройка горячих клавиш")
        
        # Привязка обычных клавиш
        self.key_facade.bind_key(pygame.K_UP, self.scroll_up_cmd)
        self.key_facade.bind_key(pygame.K_DOWN, self.scroll_down_cmd)
        self.key_facade.bind_key(pygame.K_SPACE, self.select_cmd)
        self.key_facade.bind_key(pygame.K_ESCAPE, self.open_settings_cmd)
        
        # Привязка комбинаций с модификаторами
        self.key_facade.bind_scan_code(6, pygame.KMOD_CTRL, self.copy_clipboard_cmd)
        self.key_facade.bind_scan_code(25, pygame.KMOD_CTRL, self.paste_clipboard_cmd)
        
        print(f"[DEBUG] Горячие клавиши настроены")

def get_images(dir_folder="sprites_standart"):
    """Получение списка изображений из папки"""
    print(f"[DEBUG] get_images: поиск в папке {dir_folder}")
    image_files = glob.glob(os.path.join(dir_folder, "*.png"))
    image_files.sort()
    print(f"[DEBUG] Найдено изображений: {len(image_files)}")
    return image_files

if __name__ == "__main__":
    print("[DEBUG] Запуск программы")
    
    window_width, window_height = 1280, 760

    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Programmator Viewer v6")
    print(f"[DEBUG] Окно создано: {window_width}x{window_height}")

    img_files = get_images()
    encoded_string = "XQAAgACzAAAAAAAAAAAZADAMYCDURSxK8GR5e/2nd+V9B2fs+9LemstWZRQBmMQiE4IOuXqySGdcZtrDkPe00KEs+KiBkaH1Dx0a4GlBU6a90Uy5qp5AHk4BJ9dul//0RfUyVcEDj28w/394ryD97MbhFAMFuVwQPzKLgA=="
    v_k = [0.5, 1, 1.5]

    pro = Programmator()
    print("[DEBUG] Programmator создан")
    
    pro_view = ProgrammatorViewer(screen, img_files, pro, k_size=v_k[1])
    print("[DEBUG] ProgrammatorViewer создан")

    managerGO = GameObjectManager()
    #managerGO.add(pro, 100)
    managerGO.add(pro_view, 1000)

    running = True
    clock = pygame.time.Clock()    

    print("[DEBUG] Запуск главного цикла")
    
    while running:
        # Запускаем менеджер и получаем сигнал о продолжении
        result = managerGO.run()
            
        clock.tick(30)

    pygame.quit()
    print("[DEBUG] Программа завершена")