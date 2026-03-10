import pygame
import numpy as np
import asyncio
from typing import Dict, List, Optional, Callable, Union
import time
from enum import Enum, auto
from dataclasses import dataclass

# Enum для всех звуков
class SoundEffect(Enum):
    # Изменение значений
    INCREMENT = "increment"
    DECREMENT = "decrement"
    VALUE_CHANGE = "value_change"
    
    # Переключение операторов/режимов
    OPERATOR_SWITCH = "operator_switch"
    MODE_CHANGE = "mode_change"
    
    # Подтверждение/успех
    SUCCESS = "success"
    CONFIRM = "confirm"
    
    # Ошибка/предупреждение
    ERROR = "error"
    WARNING = "warning"
    
    # Соединение/разъединение
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    
    # Загрузка/прогресс
    LOAD_START = "load_start"
    LOAD_STEP = "load_step"
    LOAD_COMPLETE = "load_complete"
    
    # Специальные эффекты
    GLITCH = "glitch"
    POWER_UP = "power_up"
    POWER_DOWN = "power_down"
    TELEPORT = "teleport"
    
    # UI звуки
    HOVER = "hover"
    SELECT = "select"
    DRAG = "drag"
    DROP = "drop"
    
    # Пиксельные/ретро звуки
    PIXEL_JUMP = "pixel_jump"
    PIXEL_LAND = "pixel_land"
    PIXEL_COLLECT = "pixel_collect"
    
    # Цифры
    DIGIT_0 = "digit_0"
    DIGIT_1 = "digit_1"
    DIGIT_2 = "digit_2"
    DIGIT_3 = "digit_3"
    DIGIT_4 = "digit_4"
    DIGIT_5 = "digit_5"
    DIGIT_6 = "digit_6"
    DIGIT_7 = "digit_7"
    DIGIT_8 = "digit_8"
    DIGIT_9 = "digit_9"
    
    # Системные
    BEEP = "beep"
    CLICK = "click"
    
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, name: str) -> Optional['SoundEffect']:
        """Получить SoundEffect из строки"""
        try:
            return cls(name)
        except ValueError:
            return None
    
    @classmethod
    def get_digit(cls, digit: int) -> Optional['SoundEffect']:
        """Получить звук для цифры"""
        if 0 <= digit <= 9:
            return cls(f"digit_{digit}")
        return None


@dataclass
class SoundConfig:
    """Конфигурация звука"""
    sound: SoundEffect
    cooldown: float = 0
    volume: float = 1.0
    fade_in: float = 0
    fade_out: float = 0
    delay: float = 0


class SoundSequence:
    """Последовательность звуков"""
    def __init__(self, sounds: List[Union[SoundEffect, SoundConfig]], loop: bool = False):
        self.sounds = sounds
        self.loop = loop
        self.current_index = 0
    
    def next(self) -> Optional[Union[SoundEffect, SoundConfig]]:
        """Получить следующий звук в последовательности"""
        if not self.sounds:
            return None
        
        if self.current_index >= len(self.sounds):
            if self.loop:
                self.current_index = 0
            else:
                return None
        
        sound = self.sounds[self.current_index]
        self.current_index += 1
        return sound
    
    def reset(self):
        """Сбросить индекс последовательности"""
        self.current_index = 0


class AsyncProgrammerSounds:
    def __init__(self):
        # Инициализация звука
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Словарь для хранения созданных звуков
        self.sounds: Dict[SoundEffect, Union[pygame.mixer.Sound, List[pygame.mixer.Sound]]] = {}
        
        # Очередь воспроизведения
        self.play_queue = asyncio.Queue()
        self.is_playing = False
        
        # Кэш для ограничения частоты звуков
        self.last_played: Dict[SoundEffect, float] = {}
        
        # Настройки по умолчанию для разных звуков
        self.default_cooldowns: Dict[SoundEffect, float] = {
            SoundEffect.HOVER: 0.1,
            SoundEffect.DRAG: 0.05,
            SoundEffect.LOAD_STEP: 0.1,
            SoundEffect.INCREMENT: 0.02,
            SoundEffect.DECREMENT: 0.02,
            SoundEffect.VALUE_CHANGE: 0.03,
        }
        
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
            # Изменение значений
            SoundEffect.INCREMENT: self.create_sine_wave(523.25, 0.05, 0.2),  # До
            SoundEffect.DECREMENT: self.create_sine_wave(392.00, 0.05, 0.2),  # Соль
            SoundEffect.VALUE_CHANGE: self.create_sine_wave(440.00, 0.03, 0.15),  # Ля
            
            # Переключение операторов/режимов
            SoundEffect.OPERATOR_SWITCH: self.create_square_wave(660, 0.08, 0.25),
            SoundEffect.MODE_CHANGE: self.create_sawtooth_wave(330, 0.1, 0.2),
            
            # Подтверждение/успех
            SoundEffect.SUCCESS: self.create_sine_wave(523.25, 0.15, 0.3),  # До
            SoundEffect.CONFIRM: [self.create_sine_wave(392, 0.1, 0.2),  # Соль
                                 self.create_sine_wave(523.25, 0.1, 0.2)],  # До
            
            # Ошибка/предупреждение
            SoundEffect.ERROR: self.create_noise(0.15, 0.25),
            SoundEffect.WARNING: self.create_square_wave(220, 0.2, 0.3),
            
            # Соединение/разъединение
            SoundEffect.CONNECT: self.create_sine_wave(659.25, 0.12, 0.25),  # Ми
            SoundEffect.DISCONNECT: self.create_sawtooth_wave(329.63, 0.12, 0.2),  # Ми ниже
            
            # Загрузка/прогресс
            SoundEffect.LOAD_START: self.create_sine_wave(440, 0.2, 0.2),
            SoundEffect.LOAD_STEP: self.create_click(0.15),
            SoundEffect.LOAD_COMPLETE: self.create_sine_wave(880, 0.3, 0.3),
            
            # Специальные эффекты
            SoundEffect.GLITCH: self.create_noise(0.1, 0.15),
            SoundEffect.POWER_UP: self.create_sawtooth_wave(200, 0.3, 0.2),
            SoundEffect.POWER_DOWN: self.create_sawtooth_wave(100, 0.3, 0.15),
            SoundEffect.TELEPORT: self.create_square_wave(440, 0.2, 0.2),
            
            # UI звуки
            SoundEffect.HOVER: self.create_sine_wave(880, 0.02, 0.1),
            SoundEffect.SELECT: self.create_square_wave(440, 0.06, 0.2),
            SoundEffect.DRAG: self.create_sawtooth_wave(220, 0.05, 0.1),
            SoundEffect.DROP: self.create_sine_wave(330, 0.1, 0.25),
            
            # Пиксельные/ретро звуки
            SoundEffect.PIXEL_JUMP: self.create_square_wave(330, 0.08, 0.2),
            SoundEffect.PIXEL_LAND: self.create_square_wave(220, 0.1, 0.15),
            SoundEffect.PIXEL_COLLECT: self.create_sawtooth_wave(880, 0.05, 0.2),
            
            # Дополнительные звуки
            SoundEffect.BEEP: self.create_beep(),
            SoundEffect.CLICK: self.create_click(),
        }
        
        # Добавляем звуки для цифр
        for i in range(10):
            freq = 440 + i * 50
            self.sounds[SoundEffect(f"digit_{i}")] = self.create_sine_wave(freq, 0.03, 0.15)
    
    def get_sound(self, sound: Union[SoundEffect, str]) -> Optional[Union[pygame.mixer.Sound, List[pygame.mixer.Sound]]]:
        """Получить звук по SoundEffect или строке"""
        if isinstance(sound, str):
            sound_effect = SoundEffect.from_string(sound)
            if sound_effect is None:
                return None
            return self.sounds.get(sound_effect)
        return self.sounds.get(sound)
    
    def get_cooldown(self, sound: SoundEffect) -> float:
        """Получить кулдаун для звука"""
        return self.default_cooldowns.get(sound, 0)
    
    async def play_async(self, 
                        sound: Union[SoundEffect, str, SoundConfig], 
                        cooldown: Optional[float] = None) -> bool:
        """Асинхронно воспроизводит звук"""
        current_time = time.time()
        
        # Обработка разных типов входных данных
        if isinstance(sound, SoundConfig):
            sound_effect = sound.sound
            effective_cooldown = cooldown if cooldown is not None else sound.cooldown
            volume = sound.volume
            fade_in = sound.fade_in
            fade_out = sound.fade_out
        elif isinstance(sound, SoundEffect):
            sound_effect = sound
            effective_cooldown = cooldown if cooldown is not None else self.get_cooldown(sound_effect)
            volume = 1.0
            fade_in = 0
            fade_out = 0
        else:  # str
            sound_effect = SoundEffect.from_string(sound)
            if sound_effect is None:
                return False
            effective_cooldown = cooldown if cooldown is not None else self.get_cooldown(sound_effect)
            volume = 1.0
            fade_in = 0
            fade_out = 0
        
        # Проверяем кулдаун
        if effective_cooldown > 0:
            last_time = self.last_played.get(sound_effect, 0)
            if current_time - last_time < effective_cooldown:
                return False
        
        sound_data = self.sounds.get(sound_effect)
        if sound_data:
            if isinstance(sound_data, list):
                # Последовательное воспроизведение нескольких звуков
                for s in sound_data:
                    if volume != 1.0:
                        s.set_volume(volume)
                    s.play()
                    await asyncio.sleep(0.05)
            else:
                if volume != 1.0:
                    sound_data.set_volume(volume)
                
                if fade_in > 0 or fade_out > 0:
                    await self._play_with_fade_impl(sound_data, fade_in, fade_out)
                else:
                    sound_data.play()
            
            self.last_played[sound_effect] = current_time
            return True
        return False
    
    async def _play_with_fade_impl(self, sound: pygame.mixer.Sound, fade_in: float, fade_out: float):
        """Реализация воспроизведения с затуханием"""
        channel = sound.play()
        if channel:
            if fade_in > 0:
                channel.set_volume(0)
                steps = 10
                for i in range(steps + 1):
                    channel.set_volume(i / steps)
                    await asyncio.sleep(fade_in / steps)
            
            if fade_out > 0:
                await asyncio.sleep(sound.get_length() - fade_out)
                steps = 10
                for i in range(steps, -1, -1):
                    channel.set_volume(i / steps)
                    await asyncio.sleep(fade_out / steps)
    
    async def play_sequence_async(self, 
                                 sounds: List[Union[SoundEffect, str, SoundConfig]], 
                                 default_delay: float = 0.05):
        """Асинхронно воспроизводит последовательность звуков"""
        for sound in sounds:
            if isinstance(sound, SoundConfig):
                await self.play_async(sound)
                await asyncio.sleep(sound.delay if sound.delay > 0 else default_delay)
            else:
                await self.play_async(sound)
                await asyncio.sleep(default_delay)
    
    async def play_sequence_obj_async(self, sequence: SoundSequence, default_delay: float = 0.05):
        """Воспроизводит объект SoundSequence"""
        while True:
            sound = sequence.next()
            if sound is None:
                break
            
            if isinstance(sound, SoundConfig):
                await self.play_async(sound)
                await asyncio.sleep(sound.delay if sound.delay > 0 else default_delay)
            else:
                await self.play_async(sound)
                await asyncio.sleep(default_delay)
            
            if sequence.loop:
                await asyncio.sleep(0.1)  # Небольшая пауза между повторами
    
    async def play_with_config_async(self, config: SoundConfig):
        """Воспроизводит звук с полной конфигурацией"""
        await self.play_async(config)
    
    async def play_for_digit_async(self, digit: int, **kwargs):
        """Воспроизводит звук для конкретной цифры"""
        sound = SoundEffect.get_digit(digit)
        if sound:
            await self.play_async(sound, **kwargs)
    
    async def stop_all(self):
        """Останавливает все звуки"""
        pygame.mixer.stop()
    
    async def demo_all_sounds_async(self):
        """Асинхронная демонстрация всех звуков"""
        print("Демонстрация звуков программатора...")
        
        categories = {
            'Изменение значений': [
                SoundEffect.INCREMENT, 
                SoundEffect.DECREMENT, 
                SoundEffect.VALUE_CHANGE
            ],
            'Операторы': [
                SoundEffect.OPERATOR_SWITCH, 
                SoundEffect.MODE_CHANGE
            ],
            'Успех/Ошибка': [
                SoundEffect.SUCCESS, 
                SoundEffect.CONFIRM, 
                SoundEffect.ERROR, 
                SoundEffect.WARNING
            ],
            'Соединения': [
                SoundEffect.CONNECT, 
                SoundEffect.DISCONNECT
            ],
            'Загрузка': [
                SoundEffect.LOAD_START, 
                SoundEffect.LOAD_STEP, 
                SoundEffect.LOAD_COMPLETE
            ],
            'Эффекты': [
                SoundEffect.GLITCH, 
                SoundEffect.POWER_UP, 
                SoundEffect.POWER_DOWN, 
                SoundEffect.TELEPORT
            ],
            'UI': [
                SoundEffect.HOVER, 
                SoundEffect.SELECT, 
                SoundEffect.DRAG, 
                SoundEffect.DROP
            ],
            'Ретро': [
                SoundEffect.PIXEL_JUMP, 
                SoundEffect.PIXEL_LAND, 
                SoundEffect.PIXEL_COLLECT
            ],
            'Цифры': [SoundEffect(f"digit_{i}") for i in range(10)],
            'Системные': [
                SoundEffect.BEEP,
                SoundEffect.CLICK
            ]
        }
        
        for category, sound_list in categories.items():
            print(f"\n=== {category} ===")
            for sound_effect in sound_list:
                print(f"▶ {sound_effect.value}")
                await self.play_async(sound_effect)
                await asyncio.sleep(0.3)


# Улучшенная версия VisualProgrammerAudio с Enum
class AsyncVisualProgrammerAudio:
    def __init__(self):
        self.sounds = AsyncProgrammerSounds()
        self.last_played: Dict[SoundEffect, float] = {}
        
        # Очередь событий
        self.processing_task: Optional[asyncio.Task] = None
        
        # Предопределенные последовательности
        self.sequences = {
            'compile_success': SoundSequence([
                SoundEffect.LOAD_COMPLETE,
                SoundConfig(SoundEffect.SUCCESS, delay=0.1)
            ]),
            'compile_error': SoundSequence([
                SoundEffect.ERROR,
                SoundConfig(SoundEffect.WARNING, delay=0.1)
            ]),
            'connection_made': SoundSequence([
                SoundEffect.CONNECT,
                SoundConfig(SoundEffect.SUCCESS, delay=0.05)
            ]),
            'power_on': SoundSequence([
                SoundEffect.POWER_UP,
                SoundEffect.CLICK,
                SoundEffect.BEEP
            ]),
        }
    
    async def start_processing(self):
        """Запускает обработку очереди событий"""
        # if not self.processing_task or self.processing_task.done():
        #     self.processing_task = asyncio.create_task(self._process_event_queue())
        pass
    
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
                
                if 'sound' in event_data:
                    sound = event_data['sound']
                    cooldown = event_data.get('cooldown')
                    await self.sounds.play_async(sound, cooldown)
                
                elif 'sequence' in event_data:
                    sequence_name = event_data['sequence']
                    if sequence_name in self.sequences:
                        await self.sounds.play_sequence_obj_async(self.sequences[sequence_name])
                
                # Дополнительная задержка
                if 'delay' in event_data:
                    await asyncio.sleep(event_data['delay'])
                
                self.event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка обработки звука: {e}")
    
    async def queue_sound(self, sound: Union[SoundEffect, str, SoundConfig], delay: float = 0):
        """Воспроизводит звук сразу"""
        await self.sounds.play_async(sound)
        if delay > 0:
            await asyncio.sleep(delay)
    
    async def queue_sequence(self, sequence_name: str, delay: float = 0):
        """Воспроизводит последовательность сразу"""
        if sequence_name in self.sequences:
            await self.sounds.play_sequence_obj_async(self.sequences[sequence_name])
        if delay > 0:
            await asyncio.sleep(delay)
    
    async def on_operator_change(self, operator_id: str, old_value: float, new_value: float):
        """Вызывается при изменении оператора"""
        if new_value > old_value:
            await self.queue_sound(SoundEffect.INCREMENT)
        elif new_value < old_value:
            await self.queue_sound(SoundEffect.DECREMENT)
        else:
            await self.queue_sound(SoundEffect.VALUE_CHANGE)
    
    async def on_operator_selected(self, operator_id: str):
        """Вызывается при выборе оператора"""
        await self.queue_sound(SoundEffect.OPERATOR_SWITCH)
    
    async def on_mode_change(self, new_mode: str):
        """Вызывается при смене режима"""
        await self.queue_sound(SoundEffect.MODE_CHANGE)
    
    async def on_connection_created(self, from_op: str, to_op: str):
        """Вызывается при создании соединения"""
        await self.queue_sequence('connection_made')
    
    async def on_connection_removed(self, from_op: str, to_op: str):
        """Вызывается при удалении соединения"""
        await self.queue_sound(SoundEffect.DISCONNECT)
    
    async def on_compile_success(self):
        """Вызывается при успешной компиляции"""
        await self.queue_sequence('compile_success')
    
    async def on_compile_error(self, error_msg: str):
        """Вызывается при ошибке компиляции"""
        await self.queue_sequence('compile_error')
    
    async def on_value_drag_start(self, value: float):
        """Вызывается при начале перетаскивания значения"""
        await self.queue_sound(SoundConfig(SoundEffect.DRAG, cooldown=0.05))
    
    async def on_value_drag_end(self, value: float):
        """Вызывается при окончании перетаскивания"""
        await self.queue_sound(SoundEffect.DROP)
    
    async def on_ui_hover(self, element: str):
        """Вызывается при наведении на элемент"""
        await self.queue_sound(SoundConfig(SoundEffect.HOVER, cooldown=0.1))
    
    async def on_ui_click(self, element: str):
        """Вызывается при клике на элемент"""
        await self.queue_sound(SoundEffect.SELECT)
    
    async def on_progress_update(self, progress: int):
        """Вызывается при обновлении прогресса"""
        if progress % 25 == 0 and progress > 0:
            await self.queue_sound(SoundConfig(SoundEffect.LOAD_STEP, cooldown=0.1))
        
        if progress == 100:
            await self.queue_sound(SoundEffect.LOAD_COMPLETE)
    
    async def on_special_action(self, action_name: str):
        """Вызывается при специальных действиях"""
        special_sounds = {
            'glitch': SoundEffect.GLITCH,
            'power_on': SoundEffect.POWER_UP,
            'power_off': SoundEffect.POWER_DOWN,
            'teleport': SoundEffect.TELEPORT,
            'collect': SoundEffect.PIXEL_COLLECT,
            'jump': SoundEffect.PIXEL_JUMP,
        }
        
        sound = special_sounds.get(action_name)
        if sound:
            await self.queue_sound(sound)
    
    async def play_background_music(self, sound: SoundEffect, volume: float = 0.2):
        """Запускает фоновую музыку (зацикленный звук)"""
        sound_obj = self.sounds.get_sound(sound)
        if sound_obj and not isinstance(sound_obj, list):
            sound_obj.set_volume(volume)
            channel = sound_obj.play(loops=-1)
            return channel
        return None
    
    async def fade_out_background(self, channel, duration: float = 1.0):
        """Плавно убирает фоновый звук"""
        if channel:
            steps = 20
            for i in range(steps, -1, -1):
                channel.set_volume(i / steps * 0.2)
                await asyncio.sleep(duration / steps)
            channel.stop()


# Пример использования
async def enum_demo():
    """Демонстрация использования Enum"""
    audio = AsyncVisualProgrammerAudio()
    await audio.start_processing()
    
    print("Демонстрация использования Enum для звуков:")
    
    # Прямое воспроизведение по Enum
    print("\n1. Прямое воспроизведение:")
    await audio.sounds.play_async(SoundEffect.SUCCESS)
    await asyncio.sleep(0.3)
    
    # Использование SoundConfig
    print("\n2. С конфигурацией:")
    config = SoundConfig(
        sound=SoundEffect.BEEP,
        volume=0.8,
        fade_in=0.05,
        fade_out=0.1,
        delay=0.2
    )
    await audio.sounds.play_with_config_async(config)
    await asyncio.sleep(0.5)
    
    # Последовательность
    print("\n3. Последовательность:")
    await audio.sounds.play_sequence_async([
        SoundEffect.CLICK,
        SoundEffect.BEEP,
        SoundConfig(SoundEffect.SUCCESS, volume=0.7)
    ])
    await asyncio.sleep(0.8)
    
    # Использование предопределенных последовательностей
    print("\n4. Предопределенная последовательность:")
    await audio.queue_sequence('power_on')
    await asyncio.sleep(1)
    
    # Цифры
    print("\n5. Цифры:")
    for i in range(10):
        await audio.sounds.play_for_digit_async(i)
        await asyncio.sleep(0.1)
    
    # Обработка событий
    print("\n6. Имитация событий программатора:")
    await audio.on_operator_change("op1", 5, 10)
    await asyncio.sleep(0.2)
    await audio.on_connection_created("op1", "op2")
    await asyncio.sleep(0.3)
    await audio.on_compile_success()
    await asyncio.sleep(0.5)
    await audio.on_compile_error("Syntax error")
    
    await asyncio.sleep(1)
    await audio.stop_processing()


async def example():
    # Прямое использование Enum
    audio = AsyncProgrammerSounds()

    await audio.play_async(SoundEffect.SUCCESS)

    # С конфигурацией
    config = SoundConfig(SoundEffect.BEEP, volume=0.5, fade_in=0.1)
    await audio.play_with_config_async(config)

    # Последовательность
    await audio.play_sequence_async([
        SoundEffect.CLICK,
        SoundEffect.BEEP,
        SoundConfig(SoundEffect.SUCCESS, delay=0.2)
    ])

    # Цифры
    await audio.play_for_digit_async(5)

if __name__ == "__main__":
    # Запуск демо
    asyncio.run(enum_demo())