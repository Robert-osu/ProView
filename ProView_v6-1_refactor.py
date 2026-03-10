import pygame
import pygame_gui
import asyncio
import threading

from Command import Command
from Programmator import Programmator
from InputController import *

from my_lib.GameObjectRenderer import GameObject, GameObjectManager

from Grid import GridObject

from utils import ValueTracker, GetImage
from TextInput import TextInput
from cmd_with_img_config import CommandConfig
from test_async_sound import AsyncProgrammerSounds, SoundEffect



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
        self.on_audio = None
        self.cmd_list = pro._commands # commands
        self.cols = 16
        self.rows = (len(self.cmd_list) + self.cols - 1) // self.cols
        self.cmd_images = GetImage(self.thumb_size).get() # шаблон команд
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.x = 0
        self.y = 0
        self.config_cmd = CommandConfig()

        
        self.is_input = False
        
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
        
        # Обработка событий
        for event in pygame.event.get():
            # Обновляем hovered если изменился
            if new_hovered != self.hovered.current:
                self.hovered.update(new_hovered)

            if event.type == pygame.QUIT:
                print(f"[DEBUG] Получен сигнал QUIT")
                return False  # Сигнал для выхода
                
            # Обработка клавиш
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                print(f"[DEBUG] {event.type} Событие клавиши: {event.key}")
                if self.is_input:
                    id = self.selected.current
                    x, y, type = self.get_cmd_data(id, self.text.num_cmd)
                    self.text.handle_event(event, type)
                    self.re_grid = True
                else:
                    self.key_facade.handle_event(event)
                
            # Обработка мыши
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_input:
                    self.close_input()
                print(f"[DEBUG] Нажатие мыши: кнопка {event.button}")
                if event.button == 1:  # Левая кнопка мыши
                    self.on_audio = SoundEffect.CLICK
                    if self.selected.current != new_hovered:
                        self.selected.update(new_hovered)
                        print(f"[DEBUG] Выбран элемент: {new_hovered}")
                    
                    self.grid.handle_page_click()
                    self.handle_text_input(event)
                
        
        if self.text.flag_end:
            self.close_input()
            

        return True  # Продолжаем работу

    def get_cmd_data(self, id, num=0):
        id = self.selected.current
        return self.config_cmd.get(self.cmd_list[id], num)

    def handle_text_input(self, event):
        # активирует ввод текста при клике на ячейку
        # 

        id = self.hovered.current
        if self.is_input and id != self.text.id_cmd:
            self.close_input()
        elif not id != None:
            pass
        elif not (self.cmd_list[id] in Command.NO_ARGS):
            if self.is_input:
                self.close_input()
            
            self.open_input(event, id)

    def open_input(self, event, id):
        cmd_list = list(Command) # список команд
        cmd = self.cmd_list[id] # текущая команда
        type = 0 # тип вводимого значения: 0метка/1переменная/2значение
        num = 0 # первое или второе значение оператора
        
        x, y = 0, 0
        width = self.thumb_size // 2
        height = self.thumb_size // 3
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if cmd in Command.ONE_ARGS:
            x, y, type = self.config_cmd.get_one_args_config(cmd)

        elif cmd in Command.TWO_ARGS:
            is_above = self.y + 32 > mouse_y
            num = 0 if is_above else 1
            x, y, type = self.config_cmd.get_two_args_config(cmd, is_above)

        if type == 0: # label
            self.text.set_max_length(3)
        elif type == 1: # variable
            self.text.set_max_length(3)
        elif type == 2: # value
            self.text.set_max_length(5)

        x += self.x
        y += self.y
        self.text.set_rect(x - width // 2, y - height // 2, width, height)

        if self.text.rect.collidepoint(event.pos):
            valueT = self.pro.getValue(id, num)
            self.text.on_active(event, id, num, valueT)
            self.grid._create_cell(id, cmd, not num)
            self.is_input = True
            self.re_grid = True

    def close_input(self):
        id = self.text.id_cmd
        cmd = self.cmd_list[id]
        num = self.text.num_cmd
        self.pro._values[id][num] = self.text.text
        self.text.off_active()
        self.grid._create_cell(id, cmd, 2)
            
        self.is_input = False
        self.re_grid = True

    def _init_all(self):
        # === 2. UI размеры и константы ===
        self._init_ui_dimensions()
        
        # === 3. Состояние и трекеры ===
        self._init_state_trackers()
        
        
        # === 7. Команды и фасад ===
        self._init_commands_and_facade()
        
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

    def _init_commands_and_facade(self):
        """Инициализация команд и фасада для клавиш"""
        print(f"[DEBUG] _init_commands_and_facade")

        # self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        self.key_bind_window = None 
        
        # Команды
        self._create_commands()
        
        # Фасад
        self.key_facade = KeyInputFacade()
        self._setup_key_facade()
        
        # Словарь для обратной совместимости
        self.key_functions = {
            'ВВЕРХ': None,
            'ВНИЗ': None,
            'ВЛЕВО': None,
            'ВПРАВО': None,
            'ДЕЙСТВИЕ': None,
            'МЕНЮ': None
        }
        
        self.key_bindings = {
            'ВВЕРХ': pygame.K_UP,
            'ВНИЗ': pygame.K_DOWN,
            'ВЛЕВО': pygame.K_LEFT,
            'ВПРАВО': pygame.K_RIGHT,
            'ДЕЙСТВИЕ': pygame.K_SPACE,
            'МЕНЮ': pygame.K_ESCAPE
        }

    def _init_manager(self):
        """Создание менеджера и добавление объектов"""
        print(f"[DEBUG] _init_manager: создание менеджера объектов")
        
        # --- СОЗДАЕМ МЕНЕДЖЕРА ---
        self.manager = GameObjectManager()
        
        # --- СОЗДАЕМ И ДОБАВЛЯЕМ ОБЪЕКТЫ ---
        self.grid = GridObject(self, z_order=1)
        self.text = TextInput(self, self.screen, 0, 0, 0, 0)
        
        self.manager.add(self.grid, self.grid.z_order)
        self.manager.add(self.text, self.text.z_order)

    def change_cell(self, cmd:Command):
        id = self.hovered.current
        if id != None and id < len(self.pro._commands):
            id = int(id)
            self.cmd_list[id] = cmd
            self.pro.addCommand(id, cmd)
            self.grid.update_cell_image(id, cmd)
            self.on_audio = SoundEffect.DIGIT_3
            self.re_grid = True

    def check_hover(self):
        """Проверяет hover математически, без перебора"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Проверяем, не наведена ли мышь на область кнопок меню
        if mouse_y < self.panel_height:
            page = self.grid.get_nav_button_at_position(mouse_x, mouse_y)
            if page != None and self.grid.pagehover != page:
                self.on_audio = SoundEffect.HOVER
                self.grid.pagehover = page
                self.re_top = True
        elif self.grid.pagehover != None:
            self.grid.pagehover = None
            self.re_top = True
        # Вычисляем возможный ряд и колонку по позиции мыши
        rel_x = mouse_x - self.padding - self.offsetW
        rel_y = mouse_y - self.padding - self.offsetH
        
        if rel_x < 0 or rel_y < 0:
            return None
        
        # Получаем номер страницы
        current_page = self.grid.page
        
        # Вычисляем колонку
        col = rel_x // (self.thumb_size + self.padding)
        if col >= self.cols:
            return None
        
        # Вычисляем ряд на текущей странице (0-11)
        page_row = rel_y // (self.thumb_size + self.padding)
        if page_row >= 12:  # rows_per_page
            return None
        
        # Вычисляем глобальный ряд с учетом страницы
        # Для 1-й страницы (page=0): global_row = 0 + page_row = 0..11
        # Для 2-й страницы (page=1): global_row = 12 + page_row = 12..23
        global_row = current_page * 12 + page_row
        
        # Проверяем границы
        if global_row >= self.rows:
            return None
        
        # Вычисляем индекс
        index = int(global_row * self.cols + col)
        
        if index >= len(self.pro._commands):
            return None
        
        # Проверяем, точно ли мышь внутри миниатюры (а не в отступах)
        x = self.padding + col * (self.thumb_size + self.padding) + self.offsetW
        # Для Y используем page_row, а не global_row!
        y = self.padding + page_row * (self.thumb_size + self.padding) + self.offsetH
        
        if (x <= mouse_x <= x + self.thumb_size and 
            y <= mouse_y <= y + self.thumb_size):
            self.x = x
            self.y = y
                
            return index
        
        return None

    def on_menu_click(self):
        """Обработчик нажатия на кнопку меню"""
        print("[DEBUG] on_menu_click: кнопка меню нажата!")
        self.open_settings()

    def update_visible_range(self):
        """Обновляет диапазон видимых строк"""
        pass
        # print(f"[DEBUG] Видимые строки: {self.first_visible_row}-{self.last_visible_row}")

    def copy_to_clipboard(self):
        """Копирование в буфер обмена"""
        print("[DEBUG] copy_to_clipboard вызван!")
        try:
            pygame.scrap.put_text(self.pro.getEncode())
            self.on_audio = SoundEffect.LOAD_START
            print("[DEBUG] Скопировано в буфер обмена!")
        except Exception as e:
            self.on_audio = SoundEffect.ERROR
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
                self.on_audio = SoundEffect.SUCCESS
            else:
                self.on_audio = SoundEffect.ERROR
                print("[DEBUG] Буфер обмена пуст или содержит не текст")
        except Exception as e:
            self.on_audio = SoundEffect.ERROR
            print(f"[DEBUG] Ошибка вставки: {e}")

    def open_settings(self):
        """Открывает окно настройки горячих клавиш"""
        print("[DEBUG] open_settings: открытие окна настроек")
        pass

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass

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
        
        
        # Отмечаем необходимость перерисовки
        self.re_grid = True
        
        print(f"[DEBUG] Программа обновлена. Команд: {len(self.cmd_list)}, строк: {self.rows}")

    def _create_commands(self):
        """Создание всех команд"""
        # self.scroll_up_cmd = ScrollUpCommand(self)
        # self.scroll_down_cmd = ScrollDownCommand(self)
        # self.select_cmd = SelectCommand(self)
        # self.open_settings_cmd = OpenSettingsCommand(self)
        self.copy_clipboard_cmd = CopyToClipboardCommand(self)
        self.paste_clipboard_cmd = PasteFromClipboardCommand(self)
        # ввод команд программатора
        self.change_cell_shiftw_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_W)
        self.change_cell_shiftd_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_D)
        self.change_cell_shifts_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_S)
        self.change_cell_shifta_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_A)
        self.change_cell_w_cmd = ChangeCellCommand(self, command_group=Command.W)
        self.change_cell_d_cmd = ChangeCellCommand(self, command_group=Command.D)
        self.change_cell_s_cmd = ChangeCellCommand(self, command_group=Command.S)
        self.change_cell_a_cmd = ChangeCellCommand(self, command_group=Command.A)
        self.change_cell_q_cmd = ChangeCellCommand(self, command_group=Command.Q)
        self.change_cell_e_cmd = ChangeCellCommand(self, command_group=Command.E)
        self.change_cell_r_cmd = ChangeCellCommand(self, command_group=Command.R)
        self.change_cell_t_cmd = ChangeCellCommand(self, command_group=Command.T)
        self.change_cell_y_cmd = ChangeCellCommand(self, cmd=Command.FLIP)
        self.change_cell_i_cmd = ChangeCellCommand(self, command_group=Command.I)
        self.change_cell_o_cmd = ChangeCellCommand(self, command_group=Command.O)

        self.change_cell_shiftf_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_F)
        self.change_cell_f_cmd = ChangeCellCommand(self, cmd=Command.MOVE_FORWARD)
        self.change_cell_g_cmd = ChangeCellCommand(self, command_group=Command.G)
        self.change_cell_h_cmd = ChangeCellCommand(self, command_group=Command.H)
        self.change_cell_j_cmd = ChangeCellCommand(self, command_group=Command.J)
        self.change_cell_l_cmd = ChangeCellCommand(self, cmd=Command.LABEL)

        self.change_cell_shiftz_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_Z)
        self.change_cell_z_cmd = ChangeCellCommand(self, command_group=Command.Z)
        self.change_cell_shiftx_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_X)
        self.change_cell_x_cmd = ChangeCellCommand(self, command_group=Command.X)
        self.change_cell_shiftc_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_C)
        self.change_cell_c_cmd = ChangeCellCommand(self, command_group=Command.C)
        self.change_cell_v_cmd = ChangeCellCommand(self, command_group=Command.V)
        self.change_cell_shiftb_cmd = ChangeCellCommand(self, command_group=Command.SHIFT_B)
        self.change_cell_b_cmd = ChangeCellCommand(self, command_group=Command.B)
        self.change_cell_m_cmd = ChangeCellCommand(self, command_group=Command.M)

        self.change_cell_backspace_cmd = ChangeCellCommand(self, command_group=Command.BACKSPACE)
    
    def _setup_key_facade(self):
        """Настройка привязки клавиш к командам через фасад"""
        
        # Привязка обычных клавиш
        # self.key_facade.bind_key(pygame.K_UP, self.scroll_up_cmd)
        # self.key_facade.bind_key(pygame.K_DOWN, self.scroll_down_cmd)
        # self.key_facade.bind_key(pygame.K_SPACE, self.select_cmd)
        # self.key_facade.bind_key(pygame.K_ESCAPE, self.open_settings_cmd)
        
        # Привязка комбинаций с модификаторами
        self.key_facade.bind_scan_code(6, pygame.KMOD_CTRL, self.copy_clipboard_cmd)
        self.key_facade.bind_scan_code(25, pygame.KMOD_CTRL, self.paste_clipboard_cmd)

        self.key_facade.bind_scan_code(26, pygame.KMOD_SHIFT, self.change_cell_shiftw_cmd)
        self.key_facade.bind_scan_code(7, pygame.KMOD_SHIFT, self.change_cell_shiftd_cmd)
        self.key_facade.bind_scan_code(22, pygame.KMOD_SHIFT, self.change_cell_shifts_cmd)
        self.key_facade.bind_scan_code(4, pygame.KMOD_SHIFT, self.change_cell_shifta_cmd)

        self.key_facade.bind_scan_code(26, pygame.KMOD_NONE, self.change_cell_w_cmd)
        self.key_facade.bind_scan_code(7, pygame.KMOD_NONE, self.change_cell_d_cmd)
        self.key_facade.bind_scan_code(22, pygame.KMOD_NONE, self.change_cell_s_cmd)
        self.key_facade.bind_scan_code(4, pygame.KMOD_NONE, self.change_cell_a_cmd)
        self.key_facade.bind_scan_code(20, pygame.KMOD_NONE, self.change_cell_q_cmd)
        self.key_facade.bind_scan_code(8, pygame.KMOD_NONE, self.change_cell_e_cmd)
        self.key_facade.bind_scan_code(21, pygame.KMOD_NONE, self.change_cell_r_cmd)
        self.key_facade.bind_scan_code(23, pygame.KMOD_NONE, self.change_cell_t_cmd)
        self.key_facade.bind_scan_code(28, pygame.KMOD_NONE, self.change_cell_y_cmd)
        self.key_facade.bind_scan_code(12, pygame.KMOD_NONE, self.change_cell_i_cmd)
        self.key_facade.bind_scan_code(18, pygame.KMOD_NONE, self.change_cell_o_cmd)

        self.key_facade.bind_scan_code(9, pygame.KMOD_SHIFT, self.change_cell_shiftf_cmd)
        self.key_facade.bind_scan_code(9, pygame.KMOD_NONE, self.change_cell_f_cmd)
        self.key_facade.bind_scan_code(10, pygame.KMOD_NONE, self.change_cell_g_cmd)
        self.key_facade.bind_scan_code(11, pygame.KMOD_NONE, self.change_cell_h_cmd)
        self.key_facade.bind_scan_code(13, pygame.KMOD_NONE, self.change_cell_j_cmd)
        self.key_facade.bind_scan_code(15, pygame.KMOD_NONE, self.change_cell_l_cmd)

        self.key_facade.bind_scan_code(29, pygame.KMOD_SHIFT, self.change_cell_shiftz_cmd)
        self.key_facade.bind_scan_code(29, pygame.KMOD_NONE, self.change_cell_z_cmd)
        self.key_facade.bind_scan_code(27, pygame.KMOD_SHIFT, self.change_cell_shiftx_cmd)
        self.key_facade.bind_scan_code(27, pygame.KMOD_NONE, self.change_cell_x_cmd)
        self.key_facade.bind_scan_code(6, pygame.KMOD_SHIFT, self.change_cell_shiftc_cmd)
        self.key_facade.bind_scan_code(6, pygame.KMOD_NONE, self.change_cell_c_cmd)
        self.key_facade.bind_scan_code(25, pygame.KMOD_NONE, self.change_cell_v_cmd)
        self.key_facade.bind_scan_code(5, pygame.KMOD_SHIFT, self.change_cell_shiftb_cmd)
        self.key_facade.bind_scan_code(5, pygame.KMOD_NONE, self.change_cell_b_cmd)
        self.key_facade.bind_scan_code(16, pygame.KMOD_NONE, self.change_cell_m_cmd)

        self.key_facade.bind_scan_code(42, pygame.KMOD_NONE, self.change_cell_backspace_cmd)
        

def run_audio_processing(audio):
    """Функция для запуска в отдельном потоке"""
    # Создаем новый цикл событий для потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Запускаем асинхронную функцию в этом потоке
    loop.run_until_complete(audio.start_processing())
        
async def main():
    window_width, window_height = 1250, 910

    audio = AsyncProgrammerSounds()

    # Запускаем audio в отдельном потоке
    audio_thread = threading.Thread(
        target=run_audio_processing, 
        args=(audio,),
        daemon=True  # Поток завершится при выходе из main
    )
    audio_thread.start()

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

        sound = pro_view.on_audio
        if sound != None:
            await audio.play_async(sound)
            pro_view.on_audio = None
            
        # Асинхронная "задержка" не блокирует цикл
        await asyncio.sleep(1/30)
        # clock.tick(30)

    await audio.stop_processing()

    pygame.quit()


if __name__ == "__main__":
    
    

    # Запуск асинхронного цикла
    asyncio.run(main())