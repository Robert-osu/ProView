import pygame
import pygame_gui

from utils import GetImage
from Command import Command

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
gui_manager = pygame_gui.UIManager((800, 600))

# Загружаем изображения
images = GetImage(32).get()
list_command = list(Command)

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
gui_manager = pygame_gui.UIManager((800, 600))

# Загрузка изображений (подготовьте свои или создайте поверхности)
# Вместо загрузки файлов создадим простые поверхности для примера
default_surface = pygame.Surface((200, 200))
default_surface.fill((100, 100, 200))  # Синий цвет
pygame.draw.circle(default_surface, (255, 255, 255), (100, 100), 50)

hover_surface = pygame.Surface((200, 200))
hover_surface.fill((200, 100, 100))  # Красный цвет
pygame.draw.circle(hover_surface, (255, 255, 0), (100, 100), 50)

# Создание UIImage
image = pygame_gui.elements.UIImage(
    relative_rect=pygame.Rect(300, 200, 200, 200),
    image_surface=default_surface,
    manager=gui_manager
)

# Для отслеживания hover
is_hovered = False

running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    
    # Проверка наведения мыши
    mouse_pos = pygame.mouse.get_pos()
    new_hovered = image.rect.collidepoint(mouse_pos)
    
    # Меняем изображение при наведении
    if new_hovered != is_hovered:
        is_hovered = new_hovered
        if is_hovered:
            image.set_image(hover_surface)
            print("Мышь наведена на картинку!")
        else:
            image.set_image(default_surface)
            print("Мышь убрана с картинки")
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        gui_manager.process_events(event)
    
    gui_manager.update(time_delta)
    
    screen.fill((30, 30, 30))
    gui_manager.draw_ui(screen)
    
    pygame.display.update()

pygame.quit()