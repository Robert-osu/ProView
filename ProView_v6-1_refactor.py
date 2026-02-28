import pygame
import pygame_gui

from Command import Command
from Programmator import Programmator
from Scrollbar import Scrollbar
from InputController import *

from my_lib.GameObjectRenderer import GameObject, GameObjectManager # Импортируем новое

from Grid import GridObject
from TopPanel import TopPanelObject
from UIManager import UIManagerObject

from utils import ValueTracker, GetImage



# --- Обновленный ProgrammatorViewer ---
class ProgrammatorViewer(GameObject): # Теперь сам viewer тоже GameObject
    """
        Просмотрщик изображений в сетке с помощью Pygame
        image_paths: список путей к изображениям
        cols: количество столбцов в сетке
        thumb_size: размер миниатюр (в пикселях)
        padding: отступ между изображениями
    """
    def __init__(self, screen, pro: Programmator, k_size=1):
        super().__init__(z_order=0)
        
        # === 1. Базовые параметры ===
        self.k_size = max(0.8, min(1.5, k_size))
        
        self.thumb_size = int(64 * self.k_size)

        self.pro = pro
        self.cmd_list = pro._commands # commands
        self.cols = 8
        self.rows = (len(self.cmd_list) + self.cols - 1) // self.cols
        self.cmd_images = GetImage(self.thumb_size).get() # шаблон команд
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        self._init_all()

    def _draw(self):
        pass

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

    def _init_all(self):
        # === 2. UI размеры и константы ===
        self._init_ui_dimensions()
        
        # === 3. Состояние и трекеры ===
        self._init_state_trackers()
        
        
        # === 7. Команды и фасад ===
        self._init_commands_and_facade()
        
        # === 8. UI элементы (pygame_gui) ===
        self._init_ui_elements()
        
        # === 9. Финальные вычисления ===
        self._init_final_calculations()
        
        # === 10. Создание менеджера и добавление объектов ===
        self._init_manager()

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
            'ВПРАВО': self.change_cell,
            'ДЕЙСТВИЕ': self.change_cell,
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

    def change_cell(self, cmd:Command):
        id = self.hovered.current
        if id != None and id < len(self.cmd_list):
            id = int(id)
            self.cmd_list[id] = cmd
            self.grid.update_cell_image(id, cmd)
            self.re_grid = True

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
            pygame.scrap.put_text(self.pro.getEncode())
            print("[DEBUG] Скопировано в буфер обмена!")
        except Exception as e:
            print(f"[DEBUG] Ошибка копирования: {e}")

    def paste_from_clipboard(self):
        """Вставка из буфера обмена"""
        print("[DEBUG] paste_from_clipboard вызван!")
        try:
            clipboard_text = pygame.scrap.get_text()
            if clipboard_text:
                print(f"[DEBUG] Текст из буфера: {clipboard_text[:50]}...")
                self.pro.copy(clipboard_text)
                self.update_from_pro()
                self.grid._create_all_cells()
                self.re_grid = True
            else:
                print("[DEBUG] Буфер обмена пуст или содержит не текст")
        except Exception as e:
            print(f"[DEBUG] Ошибка вставки: {e}")

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
        
        
        # Отмечаем необходимость перерисовки
        self.re_grid = True
        
        print(f"[DEBUG] Программа обновлена. Команд: {len(self.cmd_list)}, строк: {self.rows}")

    def _create_commands(self):
        """Создание всех команд"""
        self.scroll_up_cmd = ScrollUpCommand(self)
        self.scroll_down_cmd = ScrollDownCommand(self)
        self.select_cmd = SelectCommand(self)
        self.open_settings_cmd = OpenSettingsCommand(self)
        self.copy_clipboard_cmd = CopyToClipboardCommand(self)
        self.paste_clipboard_cmd = PasteFromClipboardCommand(self)
        # ввод команд программатора
        self.change_cell_cmd = ChangeCellCommand(self, cmd=Command.ALARM)
        self.change_cell_twoargs_cmd = ChangeCellCommand(self, command_group=Command.TWO_ARGS)
        self.change_cell_shiftw_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_W)
        self.change_cell_shiftd_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_D)
    
    def _setup_key_facade(self):
        """Настройка привязки клавиш к командам через фасад"""
        
        # Привязка обычных клавиш
        self.key_facade.bind_key(pygame.K_UP, self.scroll_up_cmd)
        self.key_facade.bind_key(pygame.K_DOWN, self.scroll_down_cmd)
        self.key_facade.bind_key(pygame.K_SPACE, self.select_cmd)
        self.key_facade.bind_key(pygame.K_ESCAPE, self.open_settings_cmd)
        
        # Привязка комбинаций с модификаторами
        self.key_facade.bind_scan_code(6, pygame.KMOD_CTRL, self.copy_clipboard_cmd)
        self.key_facade.bind_scan_code(25, pygame.KMOD_CTRL, self.paste_clipboard_cmd)
        self.key_facade.bind_scan_code(29, pygame.KMOD_CTRL, self.change_cell_cmd)
        self.key_facade.bind_scan_code(6, pygame.KMOD_CTRL, self.change_cell_twoargs_cmd)
        self.key_facade.bind_scan_code(26, pygame.KMOD_SHIFT, self.change_cell_shiftw_cmd)
        self.key_facade.bind_scan_code(7, pygame.KMOD_SHIFT, self.change_cell_shiftd_cmd)
        



if __name__ == "__main__":
    
    window_width, window_height = 700, 760

    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Programmator Viewer v6")

    encoded_string = "XQAAgACzAAAAAAAAAAAZADAMYCDURSxK8GR5e/2nd+V9B2fs+9LemstWZRQBmMQiE4IOuXqySGdcZtrDkPe00KEs+KiBkaH1Dx0a4GlBU6a90Uy5qp5AHk4BJ9dul//0RfUyVcEDj28w/394ryD97MbhFAMFuVwQPzKLgA=="
    v_k = [0.5, 1, 1.5]

    pro = Programmator()
    
    pro_view = ProgrammatorViewer(screen, pro)

    managerGO = GameObjectManager()
    #managerGO.add(pro, 100)
    managerGO.add(pro_view, 1000)

    running = True
    clock = pygame.time.Clock()    

    
    while running:
        # Запускаем менеджер и получаем сигнал о продолжении
        result = managerGO.run()
            
        clock.tick(30)

    pygame.quit()