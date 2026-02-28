
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
            if self.viewer.hovered.current:
                id = int(self.viewer.hovered.current)
            if id and self.viewer.cmd_list[id] in Command.CHECK_ORTO and self.command_group[0] in Command.CHECK_ORTO:
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
                    current_cmd = self.next(id)
            elif id and self.viewer.cmd_list[id] in self.command_group:
                current_cmd = self.next(id)
            else:
                self.current_index = 0
                current_cmd = self.command_group[self.current_index]
            # Используем команду из группы
            self.inc()
        else:
            # Используем переданную команду
            current_cmd = self.cmd
        
        # Выполняем действие
        if hasattr(self.viewer, 'change_cell'):
            self.viewer.change_cell(current_cmd)

    def next(self, id):
        current = self.viewer.cmd_list[id]
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
    """Фасад для работы с клавиатурой, использующий команды"""
    
    def __init__(self):
        self.key_bindings = {}  # {key: command}
        self.scan_bindings = {}
        self.mod_bindings = {}  # {(mod, key): command}
        self.held_keys = set()
        
        # Настройка повторения клавиш
        pygame.key.set_repeat(500, 50)
    
    def bind_key(self, key, command):
        """Привязать команду к клавише"""
        if isinstance(command, KeyCommand):
            self.key_bindings[key] = command
        else:
            raise ValueError("Объект должен быть экземпляром KeyCommand")
    
    def bind_mod_key(self, mod, key, command):
        """Привязать команду к комбинации с модификатором"""
        if isinstance(command, KeyCommand):
            self.mod_bindings[(mod, key)] = command
        else:
            raise ValueError("Объект должен быть экземпляром KeyCommand")
    
    def bind_combo(self, combo, command):
        """Привязать команду к комбинации (например 'ctrl+c')"""
        parts = combo.lower().split('+')
        key_name = parts[-1]
        mods = 0
        
        if 'ctrl' in parts:
            mods |= pygame.KMOD_CTRL
        if 'shift' in parts:
            mods |= pygame.KMOD_SHIFT
        if 'alt' in parts:
            mods |= pygame.KMOD_ALT
        
        try:
            key_const = getattr(pygame, f"K_{key_name}")
            if mods:
                self.bind_mod_key(mods, key_const, command)
            else:
                self.bind_key(key_const, command)
        except AttributeError:
            print(f"Предупреждение: клавиша {key_name} не найдена в pygame")
    
    def bind_scan_code(self, scan_code, mod, command):
        """Привязать команду к скан-коду (не зависит от раскладки)"""
        self.scan_bindings[(mod, scan_code)] = command

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            print(f"Scan code for {pygame.key.name(event.key)}: {event.scancode}")
            self.held_keys.add(event.key)
            
            # Проверка по скан-коду (приоритет)
            for (mod, scan), cmd in self.scan_bindings.items():
                if event.scancode == scan and (event.mod & mod):
                    cmd.execute()
                    return
            
            # Стандартная проверка
            self._trigger_command(event.key, event.mod)
        
        elif event.type == pygame.KEYUP:
            if event.key in self.held_keys:
                self.held_keys.remove(event.key)
    
    def _trigger_command(self, key, mods):
        """Запуск команды по нажатой клавише"""
        
        # Для отладки - преобразуем key в читаемый вид
        key_name = pygame.key.name(key) if hasattr(pygame.key, 'name') else str(key)
        print(f"DEBUG: key={key} ({key_name}), mods={mods}, mods & KMOD_CTRL={mods & pygame.KMOD_CTRL}")
        
        # Проверка комбинаций с модификаторами
        for (req_mods, req_key), command in self.mod_bindings.items():
            # Для клавиши 'c' используем и числовое значение, и символьное
            key_matches = (key == req_key or 
                        (req_key == pygame.K_c and key_name == 'c') or
                        (req_key == pygame.K_c and key == 99))  # ASCII код 'c'
            
            if key_matches:
                # Проверяем наличие Ctrl
                if req_mods & pygame.KMOD_CTRL:
                    if mods & pygame.KMOD_CTRL:
                        print(f"Найдена команда для Ctrl+{key_name}")
                        command.execute()
                        return
                # Для других модификаторов
                elif (mods & req_mods) == req_mods:
                    command.execute()
                    return
        
        # Проверка обычных клавиш
        if key in self.key_bindings:
            self.key_bindings[key].execute()
    
    def is_held(self, key):
        """Проверка, удерживается ли клавиша"""
        return key in self.held_keys
    
    def update_key_bindings(self, key_bindings_dict):
        """Обновление привязок из словаря (для совместимости)"""
        # Этот метод можно использовать для синхронизации с существующим key_bindings
        pass