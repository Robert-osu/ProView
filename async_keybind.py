import pygame
import sys

class KeyCommand:
    """Базовый класс для команд клавиш"""
    def execute(self):
        pass

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
        
        # Пытаемся найти константу клавиши
        try:
            # Проверяем, является ли key_name буквой
            if len(key_name) == 1 and key_name.isalpha():
                # Для букв используем символьную привязку
                if mods:
                    # Для комбинаций с модификаторами сохраняем в mod_bindings как строку
                    self.mod_bindings[(mods, key_name)] = command
                else:
                    # Обычная клавиша
                    self.bind_char(key_name, command)
            else:
                # Для специальных клавиш (f1, space и т.д.)
                key_const = getattr(pygame, f"K_{key_name}")
                if mods:
                    self.bind_mod_key(mods, key_const, command)
                else:
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
            if self.debug_mode:
                self._debug_print(event)
            
            self.held_keys.add(event.key)
            key_char = self.get_key_char(event)
            
            # 1. Проверяем комбинации (самый высокий приоритет)
            if self._check_combo_bindings(event, key_char):
                return
            
            # 2. Скан-коды
            if self._check_scan_bindings(event):
                return
            
            # 3. Комбинации с модификаторами
            if self._check_mod_bindings(event, key_char):
                return
            
            # 4. Привязка по символу
            if key_char and self._check_char_bindings(key_char, event.mod):
                return
            
            # 5. Обычные клавиши по коду
            self._check_key_bindings(event.key)
        
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
    
    def _check_combo_bindings(self, event, key_char):
        """Проверка комбинаций клавиш"""
        if not key_char:
            return False
        
        mods = []
        if event.mod & pygame.KMOD_CTRL:
            mods.append('ctrl')
        if event.mod & pygame.KMOD_SHIFT:
            mods.append('shift')
        if event.mod & pygame.KMOD_ALT:
            mods.append('alt')
        
        # Формируем строку комбинации
        combo = '+'.join(mods + [key_char.lower()])
        
        if combo in self.combo_bindings:
            if self.debug_mode:
                print(f"Комбинация: {combo} -> команда")
            self.combo_bindings[combo].execute()
            return True
        
        return False
    
    def _check_mod_bindings(self, event, key_char):
        """Проверка комбинаций с модификаторами"""
        # Нормализуем символ для сравнения
        norm_char = self.normalize_key(key_char) if key_char else None
        
        for (req_mods, req_key), command in self.mod_bindings.items():
            # Проверяем совпадение модификаторов
            if (event.mod & req_mods) != req_mods:
                continue
            
            # Проверяем совпадение клавиши
            key_matches = False
            
            # По коду клавиши
            if isinstance(req_key, int):
                key_matches = (event.key == req_key)
            
            # По символу (с поддержкой русской раскладки)
            if norm_char and isinstance(req_key, str):
                key_matches = (norm_char.lower() == req_key.lower())
            
            if key_matches:
                if self.debug_mode:
                    mod_names = self._get_mod_names(req_mods)
                    key_name = self._get_key_name(event.key, norm_char)
                    print(f"Комбинация: {'+'.join(mod_names + [key_name])} -> команда")
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


# Пример использования
class SaveCommand(KeyCommand):
    def execute(self):
        print("💾 Файл сохранен!")

class CopyCommand(KeyCommand):
    def execute(self):
        print("📋 Скопировано!")

class PasteCommand(KeyCommand):
    def execute(self):
        print("📌 Вставлено!")

class UndoCommand(KeyCommand):
    def execute(self):
        print("↩️ Отмена!")

class ExitCommand(KeyCommand):
    def execute(self):
        print("👋 Выход...")
        pygame.quit()
        sys.exit()

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
    keyboard.bind_combo('ctrl+s', SaveCommand())
    keyboard.bind_combo('ctrl+c', CopyCommand())
    keyboard.bind_combo('ctrl+v', PasteCommand())
    keyboard.bind_combo('ctrl+z', UndoCommand())
    keyboard.bind_combo('ctrl+q', ExitCommand())
    
    # Привязка по символам (работает в любой раскладке)
    keyboard.bind_char('a', SaveCommand())  # A или Ф вызовут Save
    
    # Привязка по скан-коду (не зависит от раскладки)
    # Скан-код 22 = S в английской, Ы в русской
    keyboard.bind_scan_code(22, pygame.KMOD_CTRL, SaveCommand())
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Передаем события в фасад
            keyboard.handle_event(event)
        
        # Отрисовка
        screen.fill((30, 30, 30))
        
        text = font.render("KeyInputFacade Demo", True, (0, 255, 0))
        screen.blit(text, (20, 50))
        
        text2 = font.render("Ctrl+S, Ctrl+C, Ctrl+V, Ctrl+Z, Ctrl+Q", True, (255, 255, 0))
        screen.blit(text2, (20, 100))
        
        text3 = font.render("Работает в русской и английской раскладке!", True, (100, 255, 100))
        screen.blit(text3, (20, 150))
        
        text4 = font.render("Нажмите A (Ф) - тоже Save", True, (200, 200, 200))
        screen.blit(text4, (20, 200))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()