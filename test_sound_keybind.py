import pygame
import numpy as np
import random

class ProgrammerSounds:
    def __init__(self):
        # Инициализация звука
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Словарь для хранения созданных звуков
        self.sounds = {}
        
        # Создаем все звуки при инициализации
        self.create_all_sounds()
    
    def create_sine_wave(self, frequency, duration, volume=0.5):
        """Создает синусоидальную волну"""
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        t = np.linspace(0, duration, frames)
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Применяем огибающую
        envelope = np.ones(frames)
        attack = int(0.01 * frames)
        decay = int(0.1 * frames)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-decay:] = np.linspace(1, 0, decay)
        
        wave = wave * envelope * 32767 * volume
        wave = wave.astype(np.int16)
        
        # Стерео
        stereo = np.repeat(wave.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(stereo)
    
    def create_square_wave(self, frequency, duration, volume=0.3):
        """Создает прямоугольную волну (пиксельный звук)"""
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        t = np.linspace(0, duration, frames)
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
        
        envelope = np.ones(frames)
        attack = int(0.005 * frames)
        envelope[:attack] = np.linspace(0, 1, attack)
        
        wave = wave * envelope * 32767 * volume
        wave = wave.astype(np.int16)
        
        stereo = np.repeat(wave.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(stereo)
    
    def create_sawtooth_wave(self, frequency, duration, volume=0.3):
        """Создает пилообразную волну"""
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        t = np.linspace(0, duration, frames)
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        
        envelope = np.ones(frames)
        attack = int(0.01 * frames)
        envelope[:attack] = np.linspace(0, 1, attack)
        
        wave = wave * envelope * 32767 * volume
        wave = wave.astype(np.int16)
        
        stereo = np.repeat(wave.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(stereo)
    
    def create_noise(self, duration, volume=0.2):
        """Создает шум (для ошибок/рандомных действий)"""
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        wave = np.random.uniform(-1, 1, frames)
        
        # Фильтруем шум для приятного звучания
        from scipy import signal
        b, a = signal.butter(4, 0.1, 'low')
        wave = signal.filtfilt(b, a, wave)
        
        envelope = np.ones(frames)
        attack = int(0.005 * frames)
        decay = int(0.05 * frames)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-decay:] = np.linspace(1, 0, decay)
        
        wave = wave * envelope * 32767 * volume
        wave = wave.astype(np.int16)
        
        stereo = np.repeat(wave.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(stereo)
    
    def create_click(self, volume=0.3):
        """Создает короткий клик"""
        sample_rate = 44100
        frames = int(0.02 * sample_rate)  # 20ms
        
        wave = np.random.uniform(-0.5, 0.5, frames)
        envelope = np.exp(-np.linspace(0, 5, frames))
        wave = wave * envelope * 32767 * volume
        
        wave = wave.astype(np.int16)
        stereo = np.repeat(wave.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(stereo)
    
    def create_beep(self, frequency=880, duration=0.1):
        """Создает простой звуковой сигнал"""
        return self.create_sine_wave(frequency, duration, 0.3)
    
    def create_all_sounds(self):
        """Создает все звуки для программатора"""
        
        # Звуки для разных операций
        self.sounds = {
            # Изменение значений (короткие звуки разной высоты)
            'increment': self.create_sine_wave(523.25, 0.05, 0.2),  # До
            'decrement': self.create_sine_wave(392.00, 0.05, 0.2),  # Соль
            'value_change': self.create_sine_wave(440.00, 0.03, 0.15),  # Ля
            
            # Переключение операторов/режимов
            'operator_switch': self.create_square_wave(660, 0.08, 0.25),
            'mode_change': self.create_sawtooth_wave(330, 0.1, 0.2),
            
            # Подтверждение/успех
            'success': self.create_sine_wave(523.25, 0.15, 0.3),  # До
            'confirm': [self.create_sine_wave(392, 0.1, 0.2),  # Соль
                       self.create_sine_wave(523.25, 0.1, 0.2)],  # До
            
            # Ошибка/предупреждение
            'error': self.create_noise(0.15, 0.25),
            'warning': self.create_square_wave(220, 0.2, 0.3),
            
            # Соединение/разъединение
            'connect': self.create_sine_wave(659.25, 0.12, 0.25),  # Ми
            'disconnect': self.create_sawtooth_wave(329.63, 0.12, 0.2),  # Ми ниже
            
            # Загрузка/прогресс
            'load_start': self.create_sine_wave(440, 0.2, 0.2),
            'load_step': self.create_click(0.15),
            'load_complete': self.create_sine_wave(880, 0.3, 0.3),
            
            # Специальные эффекты
            'glitch': self.create_noise(0.1, 0.15),
            'power_up': self.create_sawtooth_wave(200, 0.3, 0.2),
            'power_down': self.create_sawtooth_wave(100, 0.3, 0.15),
            'teleport': self.create_square_wave(440, 0.2, 0.2),
            
            # UI звуки
            'hover': self.create_sine_wave(880, 0.02, 0.1),
            'select': self.create_square_wave(440, 0.06, 0.2),
            'drag': self.create_sawtooth_wave(220, 0.05, 0.1),
            'drop': self.create_sine_wave(330, 0.1, 0.25),
            
            # Пиксельные/ретро звуки
            'pixel_jump': self.create_square_wave(330, 0.08, 0.2),
            'pixel_land': self.create_square_wave(220, 0.1, 0.15),
            'pixel_collect': self.create_sawtooth_wave(880, 0.05, 0.2),
        }
        
        # Добавляем звуки для числовых изменений (для счетчиков)
        for i in range(10):
            freq = 440 + i * 50
            self.sounds[f'digit_{i}'] = self.create_sine_wave(freq, 0.03, 0.15)
    
    def play(self, sound_name):
        """Воспроизводит звук по имени"""
        sound = self.sounds.get(sound_name)
        if sound:
            if isinstance(sound, list):
                # Последовательное воспроизведение нескольких звуков
                for s in sound:
                    s.play()
                    pygame.time.wait(50)
            else:
                sound.play()
    
    def play_sequence(self, sound_names, delay=50):
        """Воспроизводит последовательность звуков"""
        for name in sound_names:
            self.play(name)
            pygame.time.wait(delay)
    
    def demo_all_sounds(self):
        """Демонстрация всех звуков"""
        print("Демонстрация звуков программатора...")
        
        categories = {
            'Изменение значений': ['increment', 'decrement', 'value_change'],
            'Операторы': ['operator_switch', 'mode_change'],
            'Успех/Ошибка': ['success', 'confirm', 'error', 'warning'],
            'Соединения': ['connect', 'disconnect'],
            'Загрузка': ['load_start', 'load_step', 'load_complete'],
            'Эффекты': ['glitch', 'power_up', 'power_down', 'teleport'],
            'UI': ['hover', 'select', 'drag', 'drop'],
            'Ретро': ['pixel_jump', 'pixel_land', 'pixel_collect'],
            'Цифры': [f'digit_{i}' for i in range(10)]
        }
        
        for category, sound_list in categories.items():
            print(f"\n=== {category} ===")
            for sound_name in sound_list:
                print(f"▶ {sound_name}")
                self.play(sound_name)
                pygame.time.wait(300)

# Класс для интеграции с визуальным программатором
class VisualProgrammerAudio:
    def __init__(self):
        self.sounds = ProgrammerSounds()
        self.last_played = {}
        
    def on_operator_change(self, operator_id, old_value, new_value):
        """Вызывается при изменении оператора"""
        
        # Определяем тип изменения
        if new_value > old_value:
            self.sounds.play('increment')
        elif new_value < old_value:
            self.sounds.play('decrement')
        else:
            self.sounds.play('value_change')
    
    def on_operator_selected(self, operator_id):
        """Вызывается при выборе оператора"""
        self.sounds.play('operator_switch')
    
    def on_mode_change(self, new_mode):
        """Вызывается при смене режима"""
        self.sounds.play('mode_change')
    
    def on_connection_created(self, from_op, to_op):
        """Вызывается при создании соединения"""
        self.sounds.play('connect')
        self.sounds.play('success')
    
    def on_connection_removed(self, from_op, to_op):
        """Вызывается при удалении соединения"""
        self.sounds.play('disconnect')
    
    def on_compile_success(self):
        """Вызывается при успешной компиляции"""
        self.sounds.play_sequence(['load_complete', 'success'], 100)
    
    def on_compile_error(self, error_msg):
        """Вызывается при ошибке компиляции"""
        self.sounds.play('error')
        self.sounds.play('warning')
    
    def on_value_drag_start(self, value):
        """Вызывается при начале перетаскивания значения"""
        self.sounds.play('drag')
    
    def on_value_drag_end(self, value):
        """Вызывается при окончании перетаскивания"""
        self.sounds.play('drop')
    
    def on_ui_hover(self, element):
        """Вызывается при наведении на элемент"""
        # Ограничиваем частоту звуков при наведении
        current_time = pygame.time.get_ticks()
        if current_time - self.last_played.get('hover', 0) > 100:
            self.sounds.play('hover')
            self.last_played['hover'] = current_time
    
    def on_ui_click(self, element):
        """Вызывается при клике на элемент"""
        self.sounds.play('select')
    
    def on_progress_update(self, progress):
        """Вызывается при обновлении прогресса"""
        # Звуки для разных этапов прогресса
        if progress % 25 == 0:  # Каждые 25%
            self.sounds.play('load_step')
        
        if progress == 100:
            self.sounds.play('load_complete')
    
    def on_special_action(self, action_name):
        """Вызывается при специальных действиях"""
        special_sounds = {
            'glitch': 'glitch',
            'power_on': 'power_up',
            'power_off': 'power_down',
            'teleport': 'teleport',
            'collect': 'pixel_collect',
            'jump': 'pixel_jump',
        }
        
        sound_name = special_sounds.get(action_name)
        if sound_name:
            self.sounds.play(sound_name)

# Пример использования
if __name__ == "__main__":
    # Инициализация pygame для демо
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Демо звуков программатора")
    font = pygame.font.Font(None, 24)
    
    # Создаем аудиосистему
    audio = VisualProgrammerAudio()
    
    # Демонстрация всех звуков
    print("Запуск демо звуков...")
    print("Нажмите:")
    print("1-9 - цифровые звуки")
    print("C - компиляция успех")
    print("E - ошибка")
    print("H - наведение")
    print("S - выбор")
    print("P - прогресс")
    print("T - телепорт")
    print("ESC - выход")
    
    # Переменные для демо
    progress = 0
    last_progress_time = 0
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    audio.on_compile_success()
                elif event.key == pygame.K_e:
                    audio.on_compile_error("Test error")
                elif event.key == pygame.K_h:
                    audio.on_ui_hover("button")
                elif event.key == pygame.K_s:
                    audio.on_ui_click("button")
                elif event.key == pygame.K_p:
                    # Имитация прогресса
                    for p in [25, 50, 75, 100]:
                        audio.on_progress_update(p)
                        pygame.time.wait(500)
                elif event.key == pygame.K_t:
                    audio.on_special_action('teleport')
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0
                    audio.sounds.play(f'digit_{num}')
        
        # Автоматический прогресс для демо
        current_time = pygame.time.get_ticks()
        if current_time - last_progress_time > 2000:
            progress = (progress + 10) % 110
            if progress <= 100:
                audio.on_progress_update(progress)
            last_progress_time = current_time
        
        # Отрисовка
        screen.fill((30, 30, 40))
        
        y = 20
        for i, line in enumerate([
            "Звуки визуального программатора",
            "",
            "Активные звуки:",
            f"Прогресс: {progress}%",
            "",
            "Управление:",
            "C - успех | E - ошибка",
            "H - наведение | S - выбор",
            "P - прогресс | T - телепорт",
            "1-9 - цифры | ESC - выход"
        ]):
            color = (200, 200, 200) if i > 2 else (100, 255, 100)
            text = font.render(line, True, color)
            screen.blit(text, (20, y))
            y += 25
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()