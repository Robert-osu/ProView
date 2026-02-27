import pygame


class OptimizedImageGrid:
    def __init__(self, screen, rows, cols, cell_width, cell_height):
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.screen = screen
        
        # Основная поверхность
        self.grid_surface = pygame.Surface((cols * cell_width, rows * cell_height))
        
        # Кэш ячеек
        self.cell_cache = [[None for _ in range(cols)] for _ in range(rows)]
        self.cell_surfaces = [[None for _ in range(cols)] for _ in range(rows)]
        
        # Список измененных прямоугольников
        self.dirty_rects = []
    
    def set_image(self, row, col, image):
        """Установка изображения с созданием отдельной поверхности для ячейки"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cell_cache[row][col] = image
            
            if image:
                # Создаем поверхность для ячейки
                cell_surface = pygame.Surface((self.cell_width, self.cell_height))
                scaled_img = pygame.transform.scale(
                    image, 
                    (self.cell_width, self.cell_height)
                )
                cell_surface.blit(scaled_img, (0, 0))
                self.cell_surfaces[row][col] = cell_surface
            else:
                self.cell_surfaces[row][col] = None
            
            # Добавляем в dirty rects
            x = col * self.cell_width
            y = row * self.cell_height
            self.dirty_rects.append(pygame.Rect(x, y, self.cell_width, self.cell_height))
    
    def update(self, grid_x, grid_y):
        """Обновление только измененных областей на экране"""
        if self.dirty_rects:
            # Обновляем основную поверхность
            for rect in self.dirty_rects:
                row = rect.y // self.cell_height
                col = rect.x // self.cell_width
                
                if self.cell_surfaces[row][col]:
                    self.grid_surface.blit(self.cell_surfaces[row][col], rect.topleft)
                else:
                    pygame.draw.rect(self.grid_surface, (0, 0, 0), rect)
            
            # Обновляем экран
            for rect in self.dirty_rects:
                screen_rect = pygame.Rect(
                    grid_x + rect.x, 
                    grid_y + rect.y, 
                    rect.width, 
                    rect.height
                )
                self.screen.blit(self.grid_surface, screen_rect.topleft, rect)
            
            self.dirty_rects.clear()
            return True  # Были обновления
        
        return False  # Не было обновлений
    
    def update_all(self):
        """Обновление всех измененных ячеек"""
        for rect in list(self.dirty_rects):
            self.update(rect.y, rect.x)
    
import pygame
import random

class DirtyRectManager:
    def __init__(self, screen, background_color=(50, 50, 50)):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(background_color)
        self.dirty_rects = []
        
        # Начальная отрисовка фона
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
    
    def add_dirty_rect(self, rect):
        """Добавление области для обновления"""
        self.dirty_rects.append(rect)
    
    def add_dirty_rects(self, rects):
        """Добавление нескольких областей"""
        self.dirty_rects.extend(rects)
    
    def update_surface(self, surface, position):
        """Обновление конкретной поверхности"""
        rects_to_update = []
        
        for rect in self.dirty_rects:
            # Восстанавливаем фон
            self.screen.blit(self.background, rect.topleft, rect)
            # Рисуем новое содержимое
            self.screen.blit(surface, position, 
                           pygame.Rect(rect.x - position[0], 
                                      rect.y - position[1], 
                                      rect.width, rect.height))
            rects_to_update.append(rect)
        
        if rects_to_update:
            pygame.display.update(rects_to_update)
        
        self.dirty_rects.clear()
    
    def clear_all(self):
        """Полная очистка экрана"""
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

# Использование в основном коде
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Менеджер dirty rects
    dirty_manager = DirtyRectManager(screen)
    
    # Сетка
    grid = OptimizedImageGrid(screen, 4, 4, 100, 100)
    grid_position = (200, 100)
    
    # Заполняем сетку тестовыми изображениями
    image1 = pygame.Surface((50, 50))
    image1.fill((255, 0, 0))
    image2 = pygame.Surface((50, 50))
    image2.fill((0, 255, 0))
    
    for row in range(4):
        for col in range(4):
            if random.choice([True, False]):
                grid.set_image(row, col, image1)
            else:
                grid.set_image(row, col, image2)
    
    # Начальная отрисовка
    grid.update_all()
    screen.blit(grid.grid_surface, grid_position)
    pygame.display.flip()
    
    last_update = pygame.time.get_ticks()
    update_interval = 1000
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dirty_rects = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                grid_x = (x - grid_position[0]) // 100
                grid_y = (y - grid_position[1]) // 100
                
                if 0 <= grid_x < 4 and 0 <= grid_y < 4:
                    if random.choice([True, False]):
                        grid.set_image(grid_y, grid_x, image1)
                    else:
                        grid.set_image(grid_y, grid_x, image2)
                    
                    cell_rect = pygame.Rect(
                        grid_position[0] + grid_x * 100,
                        grid_position[1] + grid_y * 100,
                        100, 100
                    )
                    dirty_rects.append(cell_rect)
        
        if current_time - last_update > update_interval:
            row = random.randint(0, 3)
            col = random.randint(0, 3)
            if random.choice([True, False]):
                grid.set_image(row, col, image1)
            else:
                grid.set_image(row, col, image2)
            
            cell_rect = pygame.Rect(
                grid_position[0] + col * 100,
                grid_position[1] + row * 100,
                100, 100
            )
            dirty_rects.append(cell_rect)
            last_update = current_time
        
        # Обновление только измененных областей
        if dirty_rects:
            # Обновляем сетку для измененных ячеек
            for rect in dirty_rects:
                grid.update(
                    (rect.y - grid_position[1]) // 100,
                    (rect.x - grid_position[0]) // 100
                )
            
            # Обновляем экран
            dirty_manager.dirty_rects = dirty_rects
            dirty_manager.update_surface(grid.grid_surface, grid_position)
        
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()