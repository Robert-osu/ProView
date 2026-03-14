from enum import IntEnum
import pygame

class ScanCode(IntEnum):
    """Скан-коды клавиш для pygame"""
    
    # Буквы (A-Z)
    A = 4
    B = 5
    C = 6
    D = 7
    E = 8
    F = 9
    G = 10
    H = 11
    I = 12
    J = 13
    K = 14
    L = 15
    M = 16
    N = 17
    O = 18
    P = 19
    Q = 20
    R = 21
    S = 22
    T = 23
    U = 24
    V = 25
    W = 26
    X = 27
    Y = 28
    Z = 29
    
    # Цифры (верхний ряд)
    NUM_1 = 30
    NUM_2 = 31
    NUM_3 = 32
    NUM_4 = 33
    NUM_5 = 34
    NUM_6 = 35
    NUM_7 = 36
    NUM_8 = 37
    NUM_9 = 38
    NUM_0 = 39
    
    # Цифры на дополнительной клавиатуре
    KP_1 = 89
    KP_2 = 90
    KP_3 = 91
    KP_4 = 92
    KP_5 = 93
    KP_6 = 94
    KP_7 = 95
    KP_8 = 96
    KP_9 = 97
    KP_0 = 98

    # DOP
    BACKSPACE = 42
    
    @classmethod
    def from_pygame_key(cls, key_code):
        """
        Получить скан-код из кода клавиши pygame
        """
        return cls(key_code)
    
    @classmethod
    def from_name(cls, name):
        """
        Получить скан-код по имени клавиши
        Например: ScanCode.from_name('a') -> ScanCode.A
                 ScanCode.from_name('5') -> ScanCode.NUM_5
                 ScanCode.from_name('KP_1') -> ScanCode.KP_1
        """
        name = name.upper()
        
        # Если это буква (один символ)
        if len(name) == 1 and name.isalpha():
            # Прямое обращение к атрибуту enum
            return cls[name]
        
        # Если это цифра (один символ)
        elif len(name) == 1 and name.isdigit():
            return cls[f'NUM_{name}']
        
        # Если это специальное имя (например, KP_1)
        elif hasattr(cls, name):
            return cls[name]
        
        else:
            raise ValueError(f"Unknown key name: {name}")
    
    def is_letter(self):
        """Проверка, является ли клавиша буквой"""
        return 4 <= self.value <= 29
    
    def is_digit(self):
        """Проверка, является ли клавиша цифрой (верхний ряд)"""
        return 30 <= self.value <= 39
    
    def is_keypad_digit(self):
        """Проверка, является ли клавиша цифрой на дополнительной клавиатуре"""
        return 89 <= self.value <= 98
    
    @classmethod
    def get_all_letters(cls):
        """Получить все буквенные клавиши"""
        return [member for member in cls if member.is_letter()]
    
    @classmethod
    def get_all_digits(cls):
        """Получить все цифровые клавиши (верхний ряд)"""
        return [member for member in cls if member.is_digit()]
    
    @classmethod
    def get_all_keypad_digits(cls):
        """Получить все цифры дополнительной клавиатуры"""
        return [member for member in cls if member.is_keypad_digit()]


# Словарь для обратного преобразования (скан-код -> имя)
SCANCODE_TO_NAME = {code.value: code.name for code in ScanCode}


def get_key_name(scancode):
    """Получить имя клавиши по скан-коду"""
    return SCANCODE_TO_NAME.get(scancode, f"Unknown_{scancode}")


# Пример использования в pygame
def pygame_example():
    """Пример использования ScanCode в pygame"""
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 36)
    
    last_key = "No key pressed"
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                # Получаем скан-код нажатой клавиши
                scancode = event.scancode
                
                # Пытаемся найти клавишу в нашем enum
                try:
                    key = ScanCode(scancode)
                    key_name = key.name
                    
                    # Дополнительная информация о клавише
                    key_info = []
                    if key.is_letter():
                        key_info.append("letter")
                    if key.is_digit():
                        key_info.append("digit")
                    if key.is_keypad_digit():
                        key_info.append("keypad")
                    
                    info_str = f" ({', '.join(key_info)})" if key_info else ""
                    last_key = f"{key_name}{info_str} (scan: {scancode})"
                    
                except ValueError:
                    last_key = f"Unknown key (scan: {scancode})"
        
        # Отрисовка
        screen.fill((30, 30, 30))
        text = font.render(last_key, True, (255, 255, 255))
        text_rect = text.get_rect(center=(200, 150))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    # Демонстрация работы исправленного метода
    print("=== Тестирование ScanCode.from_name() ===")

    pygame_example()
    
    test_names = ['a', 'b', 'z', '5', '0', 'KP_1', 'KP_9']
    
    for name in test_names:
        try:
            code = ScanCode.from_name(name)
            print(f"from_name('{name}') -> {code.name} (значение: {code.value})")
        except ValueError as e:
            print(f"from_name('{name}') -> Ошибка: {e}")
    
    print("\n=== Все буквенные клавиши ===")
    for key in ScanCode.get_all_letters():
        print(f"{key.name}: {key.value}")
    
    print("\n=== Все цифровые клавиши (верхний ряд) ===")
    for key in ScanCode.get_all_digits():
        print(f"{key.name}: {key.value}")
    
    print("\n=== Все цифры дополнительной клавиатуры ===")
    for key in ScanCode.get_all_keypad_digits():
        print(f"{key.name}: {key.value}")
    
    print("\n=== Обратное преобразование (скан-код -> имя) ===")
    test_scancodes = [4, 5, 30, 34, 89, 97, 99]
    for sc in test_scancodes:
        name = get_key_name(sc)
        print(f"Скан-код {sc} -> {name}")