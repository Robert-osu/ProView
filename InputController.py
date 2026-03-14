
from abc import ABC, abstractmethod
import pygame

from test_binding1 import KeyBindWindow
from Command import Command

class KeyCommand(ABC):
    @abstractmethod
    def execute(self):
        pass

class ScrollUpCommand(KeyCommand):
    def __init__(self, viewer):
        self.viewer = viewer
    
    def execute(self):        
        self.viewer.scroll_y = max(0, self.viewer.scroll_y - 50)
        self.viewer.scrollbar.scroll_y = self.viewer.scroll_y
        self.viewer.scrollbar.update_handle()
        self.viewer.need_redraw = True
        print("Скролл вверх")

class ScrollDownCommand(KeyCommand):
    def __init__(self, viewer):
        self.viewer = viewer
    
    def execute(self):
        self.viewer.scroll_y = min(self.viewer.max_scroll, self.viewer.scroll_y + 50)
        self.viewer.scrollbar.scroll_y = self.viewer.scroll_y
        self.viewer.scrollbar.update_handle()
        self.viewer.need_redraw = True
        print("Скролл вниз")

class SelectCommand(KeyCommand):
    def __init__(self, viewer):
        self.viewer = viewer
    
    def execute(self):
        if self.viewer.selected.current is not None:
            print(f"Выбрана команда: {self.viewer.cmd_list[self.viewer.selected.current]}")

class OpenSettingsCommand(KeyCommand):
    def __init__(self, viewer):
        self.viewer = viewer
    
    def execute(self):
        if not (self.viewer.key_bind_window and self.viewer.key_bind_window.active):
            self.viewer.key_bind_window = KeyBindWindow(self.viewer.ui_manager, self.viewer)
            self.viewer.need_redraw = True

class CopyToClipboardCommand(KeyCommand):
    def __init__(self, viewer):
        self.viewer = viewer
    
    def execute(self):
        print("Копирование в буфер обмена")
        # Логика копирования
        if hasattr(self.viewer, 'copy_to_clipboard'):
            self.viewer.copy_to_clipboard()

class PasteFromClipboardCommand(KeyCommand):
    def __init__(self, viewer):
        self.viewer = viewer
    
    def execute(self):
        print("Копирование в буфер обмена")
        # Логика копирования
        if hasattr(self.viewer, 'paste_from_clipboard'):
            self.viewer.paste_from_clipboard()

# class ChangeCellCommand(KeyCommand):
#     def __init__(self, viewer, cmd):
#         self.viewer = viewer
#         self.cmd = cmd
    
#     def execute(self):
#         print("изменение клетки")
#         # Логика
#         if hasattr(self.viewer, 'change_cell'):
#             self.viewer.change_cell(self.cmd)


class ChangeCellCommand(KeyCommand):
    def __init__(self, viewer, cmd=None, command_group=None):
        self.viewer = viewer
        self.cmd = cmd
        self.command_group = list(command_group) if command_group else None
        self.current_index = 0
    
    def execute(self):
        current_cmd = Command.EMPTY
        id = None
        # Определяем какую команду выполнять
        if self.command_group:
            # костыль
            if self.viewer.hovered.current != None:
                id = int(self.viewer.hovered.current)
                print(2, id)
            if id != None and self.viewer.cmd_list[id] in Command.CHECK_ORTO and self.command_group[0] in Command.CHECK_ORTO:
                # Комбинирует два ортогональных направления в диагональное
                dir1 = self.viewer.cmd_list[id]
                dir2 = self.command_group[0]
                
                # Проверяем, что направления не одинаковые
                if dir1 != dir2:
                    # Ищем комбинацию в словаре
                    key = (dir1, dir2)
                    if key in Command.CHECK_DIAGONAL:
                        current_cmd = Command.CHECK_DIAGONAL[key]
                    else:
                        current_cmd = dir2
                else:
                    current_cmd = self.next(id)
            elif id != None and self.viewer.pro._commands[id] in self.command_group:
                current_cmd = self.next(id)
                print(3)
            else:
                self.current_index = 0
                current_cmd = self.command_group[self.current_index]
                print(id, id != None, self.viewer.pro._commands[0] in self.command_group, self.viewer.pro._commands[0])
            # Используем команду из группы
            self.inc()
        else:
            # Используем переданную команду
            current_cmd = self.cmd
            print(5)
        
        # Выполняем действие
        if hasattr(self.viewer, 'change_cell'):
            self.viewer.change_cell(current_cmd)
            print(6)

    def next(self, id):
        current = self.viewer.pro._commands[id]
        i = self.command_group.index(current)
        next = (i + 1) % len(self.command_group)  # % для циклического перехода
        return self.command_group[next]

    def inc(self):
        if self.current_index + 1 >= len(self.command_group):
            self.current_index = 0
        else:
            self.current_index += 1

# ========== ПАТТЕРН ФАСАД ==========
class KeyInputFacade:
    """Фасад для работы с клавиатурой с поддержкой русской раскладки"""
    
    def __init__(self):
        self.key_bindings = {}  # {key: command}
        self.scan_bindings = {}  # {(mod, scan): command}
        self.char_bindings = {}  # {'char': command} - привязка по символу
        self.combo_bindings = {}  # {'combo_string': command}
        self.mod_bindings = {}
        self.held_keys = set()
        
        # Маппинг русских символов на английские
        self.ru_to_en = {
            # Строчные
            'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 'e', 'н': 'n',
            'г': 'g', 'ш': 'i', 'щ': 'o', 'з': 'z', 'х': 'x', 'ъ': ']',
            'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h',
            'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';', 'э': "'", 'ё': '`',
            'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n',
            'ь': 'm', 'б': ',', 'ю': '.',
            
            # Заглавные
            'Й': 'Q', 'Ц': 'W', 'У': 'E', 'К': 'R', 'Е': 'E', 'Н': 'N',
            'Г': 'G', 'Ш': 'I', 'Щ': 'O', 'З': 'Z', 'Х': 'X', 'Ъ': '}',
            'Ф': 'A', 'Ы': 'S', 'В': 'D', 'А': 'F', 'П': 'G', 'Р': 'H',
            'О': 'J', 'Л': 'K', 'Д': 'L', 'Ж': ':', 'Э': '"', 'Ё': '~',
            'Я': 'Z', 'Ч': 'X', 'С': 'C', 'М': 'V', 'И': 'B', 'Т': 'N',
            'Ь': 'M', 'Б': '<', 'Ю': '>',
        }
        
        # Обратный маппинг (английские на русские)
        self.en_to_ru = {v: k for k, v in self.ru_to_en.items()}
        
        # Кэш для быстрого доступа
        self.key_names_cache = {}
        
        # Настройка повторения клавиш
        pygame.key.set_repeat(500, 50)
        
        # Режим отладки
        self.debug_mode = False
    
    def normalize_key(self, key_char):
        """Преобразует русский символ в английский"""
        if key_char in self.ru_to_en:
            return self.ru_to_en[key_char]
        return key_char
    
    def get_key_char(self, event):
        """Получает символ клавиши с учетом раскладки"""
        if event.unicode:
            return event.unicode
        return None
    
    def bind_key(self, key, command):
        """Привязать команду к клавише (по коду клавиши)"""
        if isinstance(command, KeyCommand):
            self.key_bindings[key] = command
        else:
            raise ValueError("Объект должен быть экземпляром KeyCommand")
    
    def bind_char(self, char, command):
        """Привязать команду к символу (работает в любой раскладке)"""
        if isinstance(command, KeyCommand):
            # Сохраняем привязку для символа
            self.char_bindings[char.lower()] = command
        else:
            raise ValueError("Объект должен быть экземпляром KeyCommand")
    
    def bind_mod_key(self, mod, key, command):
        """Привязать команду к комбинации с модификатором"""
        if isinstance(command, KeyCommand):
            self.mod_bindings[(mod, key)] = command
        else:
            raise ValueError("Объект должен быть экземпляром KeyCommand")
    
    def bind_combo(self, combo, command):
        """Привязать команду к комбинации (например 'ctrl+c') с поддержкой русской раскладки"""
        parts = combo.lower().split('+')
        key_name = parts[-1]
        mods = 0
        
        if 'ctrl' in parts:
            mods |= pygame.KMOD_CTRL
        if 'shift' in parts:
            mods |= pygame.KMOD_SHIFT
        if 'alt' in parts:
            mods |= pygame.KMOD_ALT
        
        # Сохраняем строковое представление комбинации
        self.combo_bindings[combo.lower()] = command
        
        # Для комбинаций с модификаторами сохраняем в mod_bindings
        if mods:
            # Сохраняем key_name как строку для последующего сравнения
            self.mod_bindings[(mods, key_name)] = command
        else:
            # Без модификаторов
            if len(key_name) == 1 and key_name.isalpha():
                self.bind_char(key_name, command)
            else:
                try:
                    key_const = getattr(pygame, f"K_{key_name}")
                    self.bind_key(key_const, command)
                except AttributeError:
                    print(f"Предупреждение: клавиша {key_name} не найдена в pygame")
    
    def bind_scan_code(self, scan_code, mod, command):
        """Привязать команду к скан-коду (не зависит от раскладки)"""
        if isinstance(command, KeyCommand):
            self.scan_bindings[(mod, scan_code)] = command
        else:
            raise ValueError("Объект должен быть экземпляром KeyCommand")
    
    def handle_event(self, event):
        """Обработка событий клавиатуры"""
        if event.type == pygame.KEYDOWN:
            # Отладка
            if self.debug_mode:
                self._debug_print(event)
            
            self.held_keys.add(event.key)
            
            # Получаем символ клавиши
            key_char = self.get_key_char(event)
            
            # 1. Приоритет: скан-коды (самые надежные)
            if self._check_scan_bindings(event):
                return
            
            # 2. Комбинации с модификаторами
            if self._check_mod_bindings(event, key_char):
                return
            
            # 3. Привязка по символу (с нормализацией русских букв)
            if key_char and self._check_char_bindings(key_char, event.mod):
                return
            
            # 4. Обычные клавиши по коду
            if self._check_key_bindings(event.key):
                return
        
        elif event.type == pygame.KEYUP:
            if event.key in self.held_keys:
                self.held_keys.remove(event.key)
    
    def _check_scan_bindings(self, event):
        """Проверка привязок по скан-коду"""
        for (mod, scan), cmd in self.scan_bindings.items():
            if event.scancode == scan:
                if mod == pygame.KMOD_NONE or (event.mod & mod):
                    if self.debug_mode:
                        print(f"Скан-код: {scan} -> команда")
                    cmd.execute()
                    return True
        return False
    
    def _check_mod_bindings(self, event, key_char):
        """Проверка комбинаций с модификаторами"""
        # Нормализуем символ для сравнения
        norm_char = self.normalize_key(key_char) if key_char else None
        print("event.key:", event.key, "norm_char:", norm_char, "key_char:", key_char)

        print("UNICODE:", event.unicode, "KEY:", event.key, "MOD:", event.mod)
        
        # Получаем состояние всех клавиш
        keys = pygame.key.get_pressed()
        
        # Определяем текущие модификаторы по состоянию клавиш
        ctrl_pressed = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        alt_pressed = keys[pygame.K_LALT] or keys[pygame.K_RALT]
        
        current_mods = 0
        if ctrl_pressed:
            current_mods |= pygame.KMOD_CTRL
        if shift_pressed:
            current_mods |= pygame.KMOD_SHIFT
        if alt_pressed:
            current_mods |= pygame.KMOD_ALT
        
        print(f"DEBUG: current_mods={current_mods}, event.mod={event.mod}, key_char={repr(key_char)}")
        
        for (req_mods, req_key), command in self.mod_bindings.items():
            print(f"EXECUTE:0 - проверка req_mods={req_mods}, req_key={req_key}")
            
            # Проверяем совпадение модификаторов
            if (current_mods & req_mods) != req_mods:
                print(f"Модификаторы не совпадают: current_mods={current_mods}, req_mods={req_mods}")
                continue
            
            print("EXECUTE:1 - модификаторы совпали")
            
            # Проверяем совпадение клавиши
            key_matches = False
            
            # 1. Проверка по символу (для обычных букв)
            if key_char and key_char.isprintable() and isinstance(req_key, str):
                # Для Ctrl+буква в event.unicode может быть управляющий символ (например, \x03 для Ctrl+C)
                # Поэтому для Ctrl используем альтернативный способ
                if current_mods & pygame.KMOD_CTRL:
                    # Получаем имя клавиши из event
                    key_name = pygame.key.name(event.key)
                    key_matches = (key_name.lower() == req_key.lower())
                    print(f"EXECUTE:2a - Ctrl: сравнение имен: {key_name} vs {req_key} = {key_matches}")
                else:
                    # Обычное сравнение символов
                    key_matches = (norm_char.lower() == req_key.lower()) if norm_char else False
                    print(f"EXECUTE:2b - сравнение символов: {norm_char} vs {req_key} = {key_matches}")
            
            # 2. Для специальных клавиш (если нет символа)
            elif not key_char and isinstance(req_key, str):
                key_name = pygame.key.name(event.key)
                key_matches = (key_name.lower() == req_key.lower())
                print(f"EXECUTE:2c - спец. клавиша: {key_name} vs {req_key} = {key_matches}")
            
            # 3. Для числовых кодов клавиш
            elif isinstance(req_key, int):
                key_matches = (event.key == req_key)
                print(f"EXECUTE:2d - сравнение кодов: {event.key} vs {req_key} = {key_matches}")
            
            if key_matches:
                print(f"EXECUTE:3 - НАЙДЕНО СОВПАДЕНИЕ!")
                command.execute()
                return True
        
        return False
    
    def _check_char_bindings(self, key_char, mods):
        """Проверка привязок по символу"""
        # Проверяем оригинальный символ
        if key_char.lower() in self.char_bindings:
            # Проверяем, не является ли это частью комбинации с модификатором
            if mods & pygame.KMOD_CTRL:
                # Для Ctrl+буква используем отдельную обработку
                combo = f"ctrl+{key_char.lower()}"
                if combo in self.combo_bindings:
                    return False  # Пусть обработается через combo_bindings
            
            if self.debug_mode:
                print(f"Символ: {key_char} -> команда")
            self.char_bindings[key_char.lower()].execute()
            return True
        
        # Проверяем нормализованный символ (русский -> английский)
        norm_char = self.normalize_key(key_char)
        if norm_char != key_char and norm_char.lower() in self.char_bindings:
            if self.debug_mode:
                print(f"Символ (норм.): {key_char} -> {norm_char} -> команда")
            self.char_bindings[norm_char.lower()].execute()
            return True
        
        return False
    
    def _check_key_bindings(self, key):
        """Проверка привязок по коду клавиши"""
        if key in self.key_bindings:
            if self.debug_mode:
                print(f"Код клавиши: {key} -> команда")
            self.key_bindings[key].execute()
            return True
        return False
    
    def is_held(self, key):
        """Проверка, удерживается ли клавиша"""
        if isinstance(key, str):
            # Поиск по символу
            for held_key in self.held_keys:
                key_name = pygame.key.name(held_key)
                if key_name.lower() == key.lower():
                    return True
            return False
        return key in self.held_keys
    
    def get_pressed_mods(self):
        """Получить текущие нажатые модификаторы"""
        mods = 0
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            mods |= pygame.KMOD_CTRL
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            mods |= pygame.KMOD_SHIFT
        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
            mods |= pygame.KMOD_ALT
        
        return mods
    
    def clear_bindings(self):
        """Очистить все привязки"""
        self.key_bindings.clear()
        self.scan_bindings.clear()
        self.char_bindings.clear()
        self.combo_bindings.clear()
    
    def set_debug(self, enabled=True):
        """Включить/выключить режим отладки"""
        self.debug_mode = enabled
    
    def _debug_print(self, event):
        """Вывод отладочной информации"""
        key_name = pygame.key.name(event.key)
        key_char = self.get_key_char(event)
        mod_names = self._get_mod_names(event.mod)
        
        print(f"KEYDOWN: код={event.key}, имя={key_name}, скан={event.scancode}, "
              f"символ={key_char or 'None'}, моды={mod_names}")
    
    def _get_mod_names(self, mods):
        """Получить список названий модификаторов"""
        names = []
        if mods & pygame.KMOD_CTRL:
            names.append('Ctrl')
        if mods & pygame.KMOD_SHIFT:
            names.append('Shift')
        if mods & pygame.KMOD_ALT:
            names.append('Alt')
        return names
    
    def _get_key_name(self, key_code, key_char=None):
        """Получить имя клавиши для отладки"""
        if key_char:
            return key_char
        return pygame.key.name(key_code)



def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("KeyInputFacade Demo")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    
    # Создаем фасад
    keyboard = KeyInputFacade()
    keyboard.set_debug(True)  # Включаем отладку
    
    # Привязываем команды
    # keyboard.bind_combo('ctrl+s', SaveCommand())
    # keyboard.bind_combo('ctrl+c', CopyCommand())
    # keyboard.bind_combo('ctrl+v', PasteCommand())
    # keyboard.bind_combo('ctrl+z', UndoCommand())
    # keyboard.bind_combo('ctrl+q', ExitCommand())
    
    # Привязка по символам (работает в любой раскладке)
    # keyboard.bind_char('a', SaveCommand())  # A или Ф вызовут Save
    
    # Привязка по скан-коду (не зависит от раскладки)
    # Скан-код 22 = S в английской, Ы в русской
    # keyboard.bind_scan_code(22, pygame.KMOD_CTRL, SaveCommand())
 