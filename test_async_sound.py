import pygame
import numpy as np
import asyncio
from typing import Dict, List, Optional, Callable
import time

class AsyncProgrammerSounds:
    def __init__(self):
        # Инициализация звука
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Словарь для хранения созданных звуков
        self.sounds: Dict[str, any] = {}
        
        # Очередь воспроизведения
        self.play_queue = asyncio.Queue()
        self.is_playing = False
        
        # Кэш для ограничения частоты звуков
        self.last_played: Dict[str, float] = {}
        
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
        try:
            from scipy import signal
            b, a = signal.butter(4, 0.1, 'low')
            wave = signal.filtfilt(b, a, wave)
        except ImportError:
            # Если scipy не доступен, используем простой фильтр
            kernel = np.ones(5) / 5
            wave = np.convolve(wave, kernel, mode='same')
        
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
    
    async def play_async(self, sound_name: str, cooldown: float = 0) -> bool:
        """Асинхронно воспроизводит звук по имени с возможным кулдауном"""
        current_time = time.time()
        
        # Проверяем кулдаун
        if cooldown > 0:
            last_time = self.last_played.get(sound_name, 0)
            if current_time - last_time < cooldown:
                return False
        
        sound = self.sounds.get(sound_name)
        if sound:
            if isinstance(sound, list):
                # Последовательное воспроизведение нескольких звуков
                for s in sound:
                    s.play()
                    await asyncio.sleep(0.05)  # 50ms между звуками
            else:
                sound.play()
            
            self.last_played[sound_name] = current_time
            return True
        return False
    
    async def play_sequence_async(self, sound_names: List[str], delay: float = 0.05):
        """Асинхронно воспроизводит последовательность звуков"""
        for name in sound_names:
            await self.play_async(name)
            await asyncio.sleep(delay)
    
    async def play_with_fade(self, sound_name: str, fade_in: float = 0, fade_out: float = 0):
        """Воспроизводит звук с затуханием"""
        sound = self.sounds.get(sound_name)
        if sound:
            if isinstance(sound, list):
                sound = sound[0]
            
            channel = sound.play()
            if channel and (fade_in > 0 or fade_out > 0):
                if fade_in > 0:
                    channel.set_volume(0)
                    # Плавное увеличение громкости
                    steps = 10
                    for i in range(steps + 1):
                        channel.set_volume(i / steps)
                        await asyncio.sleep(fade_in / steps)
                
                if fade_out > 0:
                    await asyncio.sleep(sound.get_length() - fade_out)
                    # Плавное уменьшение громкости
                    steps = 10
                    for i in range(steps, -1, -1):
                        channel.set_volume(i / steps)
                        await asyncio.sleep(fade_out / steps)
    
    async def play_loop_async(self, sound_name: str, times: int = -1, interval: float = 0):
        """Асинхронно воспроизводит звук по кругу"""
        count = 0
        while times == -1 or count < times:
            await self.play_async(sound_name)
            count += 1
            if interval > 0:
                await asyncio.sleep(interval)
    
    async def stop_all(self):
        """Останавливает все звуки"""
        pygame.mixer.stop()
    
    async def demo_all_sounds_async(self):
        """Асинхронная демонстрация всех звуков"""
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
                await self.play_async(sound_name)
                await asyncio.sleep(0.3)

# Асинхронный класс для интеграции с визуальным программатором
class AsyncVisualProgrammerAudio:
    def __init__(self):
        self.sounds = AsyncProgrammerSounds()
        self.last_played: Dict[str, float] = {}
        
        # Очередь событий
        self.event_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        # Настройки кулдаунов для разных типов звуков (в секундах)
        self.cooldowns = {
            'hover': 0.1,
            'drag': 0.05,
            'load_step': 0.1,
            'increment': 0.02,
            'decrement': 0.02,
        }
    
    async def start_processing(self):
        """Запускает обработку очереди событий"""
        if not self.processing_task or self.processing_task.done():
            self.processing_task = asyncio.create_task(self._process_event_queue())
    
    async def stop_processing(self):
        """Останавливает обработку очереди событий"""
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
    
    async def _process_event_queue(self):
        """Обрабатывает очередь событий"""
        while True:
            try:
                event_data = await self.event_queue.get()
                sound_name = event_data.get('sound')
                cooldown = self.cooldowns.get(sound_name, 0)
                
                await self.sounds.play_async(sound_name, cooldown)
                
                # Дополнительная задержка для последовательности
                if 'delay' in event_data:
                    await asyncio.sleep(event_data['delay'])
                
                self.event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка обработки звука: {e}")
    
    async def queue_sound(self, sound_name: str, delay: float = 0):
        """Добавляет звук в очередь"""
        await self.event_queue.put({'sound': sound_name, 'delay': delay})
    
    async def on_operator_change(self, operator_id: str, old_value: float, new_value: float):
        """Вызывается при изменении оператора"""
        if new_value > old_value:
            await self.queue_sound('increment')
        elif new_value < old_value:
            await self.queue_sound('decrement')
        else:
            await self.queue_sound('value_change')
    
    async def on_operator_selected(self, operator_id: str):
        """Вызывается при выборе оператора"""
        await self.queue_sound('operator_switch')
    
    async def on_mode_change(self, new_mode: str):
        """Вызывается при смене режима"""
        await self.queue_sound('mode_change')
    
    async def on_connection_created(self, from_op: str, to_op: str):
        """Вызывается при создании соединения"""
        await self.queue_sound('connect')
        await asyncio.sleep(0.05)
        await self.queue_sound('success')
    
    async def on_connection_removed(self, from_op: str, to_op: str):
        """Вызывается при удалении соединения"""
        await self.queue_sound('disconnect')
    
    async def on_compile_success(self):
        """Вызывается при успешной компиляции"""
        await self.sounds.play_sequence_async(['load_complete', 'success'], 0.1)
    
    async def on_compile_error(self, error_msg: str):
        """Вызывается при ошибке компиляции"""
        await self.sounds.play_async('error')
        await asyncio.sleep(0.1)
        await self.sounds.play_async('warning')
    
    async def on_value_drag_start(self, value: float):
        """Вызывается при начале перетаскивания значения"""
        await self.sounds.play_async('drag', cooldown=0.05)
    
    async def on_value_drag_end(self, value: float):
        """Вызывается при окончании перетаскивания"""
        await self.sounds.play_async('drop')
    
    async def on_ui_hover(self, element: str):
        """Вызывается при наведении на элемент"""
        await self.sounds.play_async('hover', cooldown=0.1)
    
    async def on_ui_click(self, element: str):
        """Вызывается при клике на элемент"""
        await self.sounds.play_async('select')
    
    async def on_progress_update(self, progress: int):
        """Вызывается при обновлении прогресса"""
        if progress % 25 == 0 and progress > 0:
            await self.sounds.play_async('load_step', cooldown=0.1)
        
        if progress == 100:
            await self.sounds.play_async('load_complete')
    
    async def on_special_action(self, action_name: str):
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
            await self.sounds.play_async(sound_name)
    
    
    async def fade_out_background(self, channel, duration: float = 1.0):
        """Плавно убирает фоновый звук"""
        if channel:
            steps = 20
            for i in range(steps, -1, -1):
                channel.set_volume(i / steps * 0.2)
                await asyncio.sleep(duration / steps)
            channel.stop()

# Асинхронное демо
async def async_demo():
    """Асинхронная демонстрация"""
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption("Асинхронное демо звуков программатора")
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    
    # Создаем аудиосистему
    audio = AsyncVisualProgrammerAudio()
    
    # Запускаем обработку очереди
    await audio.start_processing()
    
    # Переменные для демо
    progress = 0
    last_progress_time = 0
    selected_button = None
    demo_text = ""
    
    print("Запуск асинхронного демо звуков...")
    print("Нажмите:")
    print("1-9 - цифровые звуки")
    print("C - компиляция успех")
    print("E - ошибка")
    print("H - наведение")
    print("S - выбор")
    print("P - прогресс")
    print("T - телепорт")
    print("M - фоновая музыка")
    print("F - остановить музыку")
    print("ESC - выход")
    
    running = True
    while running:
        # Обработка событий pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    await audio.on_compile_success()
                    demo_text = "Компиляция успешна!"
                elif event.key == pygame.K_e:
                    await audio.on_compile_error("Test error")
                    demo_text = "Ошибка компиляции!"
                elif event.key == pygame.K_h:
                    await audio.on_ui_hover("button")
                    demo_text = "Наведение на кнопку"
                elif event.key == pygame.K_s:
                    await audio.on_ui_click("button")
                    demo_text = "Клик по кнопке"
                elif event.key == pygame.K_p:
                    demo_text = "Запуск прогресса..."
                    # Имитация прогресса
                    for p in [25, 50, 75, 100]:
                        await audio.on_progress_update(p)
                        await asyncio.sleep(0.5)
                elif event.key == pygame.K_t:
                    await audio.on_special_action('teleport')
                    demo_text = "Телепортация!"
                elif event.key == pygame.K_m:
                    channel = await audio.play_background_music('power_up', 0.15)
                    audio.background_channel = channel
                    demo_text = "Фоновая музыка включена"
                elif event.key == pygame.K_f:
                    if hasattr(audio, 'background_channel'):
                        await audio.fade_out_background(audio.background_channel, 0.5)
                        demo_text = "Музыка выключена"
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0
                    await audio.sounds.play_async(f'digit_{num}')
                    demo_text = f"Цифра {num}"
        
        # Автоматический прогресс для демо
        current_time = pygame.time.get_ticks()
        if current_time - last_progress_time > 3000:
            progress = (progress + 10) % 110
            if progress <= 100:
                await audio.on_progress_update(progress)
            last_progress_time = current_time
        
        # Отрисовка
        screen.fill((30, 30, 40))
        
        y = 20
        lines = [
            "Асинхронный звуковой движок",
            "для визуального программатора",
            "",
            f"Прогресс: {progress}%",
            "",
            f"Последнее действие: {demo_text}",
            "",
            "Управление:",
            "C - успех | E - ошибка",
            "H - наведение | S - выбор",
            "P - прогресс | T - телепорт",
            "M - музыка | F - стоп",
            "1-9 - цифры | ESC - выход"
        ]
        
        for i, line in enumerate(lines):
            if i == 0:
                color = (100, 255, 100)  # Зеленый для заголовка
            elif i == len(lines) - 1:
                color = (255, 100, 100)  # Красный для выхода
            elif ":" in line:
                color = (200, 200, 100)  # Желтый для команд
            else:
                color = (200, 200, 200)  # Серый для остального
            
            text = font.render(line, True, color)
            screen.blit(text, (20, y))
            y += 25
        
        pygame.display.flip()
        
        # Асинхронное ожидание
        await asyncio.sleep(0)
        clock.tick(30)
    
    # Очистка
    await audio.stop_processing()
    await audio.sounds.stop_all()
    pygame.quit()



# Пример использования в основном коде:
async def main():
    audio = AsyncVisualProgrammerAudio()
    await audio.start_processing()
    running = True
    
    # Ваш основной код здесь
    while running:
        # Обработка событий
        await audio.on_ui_hover("button")
        await asyncio.sleep(2)
    
    await audio.stop_processing()


# # Запуск
# asyncio.run(main())

# Точка входа
if __name__ == "__main__":
    # Запуск асинхронного демо
    asyncio.run(main())