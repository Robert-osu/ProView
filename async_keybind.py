import asyncio
import pygame
from pynput import keyboard
import threading
from test_async_sound import AsyncVisualProgrammerAudio

class AsyncKeyboardHandler:
    def __init__(self):
        self.key_states = {}
        self.loop = None
        
    def on_press(self, key):
        """Callback для pynput"""
        self.key_states[key] = True
        if self.loop:
            # Можно создать корутину для обработки
            asyncio.run_coroutine_threadsafe(
                self.on_key_press_async(key), self.loop
            )
    
    def on_release(self, key):
        """Callback для отпускания"""
        self.key_states[key] = False
        if key == keyboard.Key.esc:
            return False
    
    async def on_key_press_async(self, key):
        """Асинхронная обработка нажатий"""
        print(f"Асинхронная обработка: {key}")
        # Здесь можно делать долгие операции
        await asyncio.sleep(0.1)
    
    def start(self, loop):
        self.loop = loop
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
    
    def stop(self):
        if self.listener:
            self.listener.stop()

async def async_game_loop():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    audio = AsyncVisualProgrammerAudio()
    await audio.start_processing()
    
    handler = AsyncKeyboardHandler()
    handler.start(asyncio.get_running_loop())
    
    player_pos = [400, 300]
    running = True
    
    while running:
        # Обработка pygame событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Управление
        if handler.key_states.get(keyboard.KeyCode.from_char('w')):
            await audio.on_ui_hover("button")
            player_pos[1] -= 5
        if handler.key_states.get(keyboard.KeyCode.from_char('s')):
            await audio.on_ui_hover("button")
            player_pos[1] += 5
        if handler.key_states.get(keyboard.KeyCode.from_char('a')):
            await audio.on_ui_hover("button")
            player_pos[0] -= 5
        if handler.key_states.get(keyboard.KeyCode.from_char('d')):
            await audio.on_ui_hover("button")
            player_pos[0] += 5
        
        if handler.key_states.get(keyboard.Key.esc):
            running = False
        
        # Отрисовка
        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, (0, 0, 255), player_pos, 20)
        pygame.display.flip()
        
        # Асинхронная "задержка" не блокирует цикл
        await asyncio.sleep(1/60)
    
    await audio.stop_processing()
    handler.stop()
    pygame.quit()

# Запуск асинхронного цикла
asyncio.run(async_game_loop())