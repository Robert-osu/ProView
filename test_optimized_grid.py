import pygame
from utils import GetImage

class ImageGrid:
    def __init__(self, screen, size=64, cols=16):
        self.screen = screen
        self.img_size = size
        self.cols = cols
        
        # Загружаем изображения
        self.images = GetImage(32).get()  # {int: surface}
        self.rows = (len(self.images) + self.cols - 1) // self.cols
        
        # Создаем поверхность для всей сетки
        self.grid_width = self.cols * self.img_size
        self.grid_height = self.rows * self.img_size
        self.grid_surface = pygame.Surface((self.grid_width, self.grid_height))
        
        # Заполняем сетку
        self._create_grid()
    
    def _create_grid(self):
        """Создание сетки с изображениями"""
        image_items = list(self.images.items())
        
        for idx, (key, img) in enumerate(image_items):
            row = idx // self.cols
            col = idx % self.cols
            
            # Создаем ячейку
            cell = pygame.Surface((self.img_size, self.img_size))
            cell.fill((30, 30, 30))
            
            if img:
                # Масштабируем изображение
                scale = min(self.img_size / img.get_width(), 
                          self.img_size / img.get_height())
                new_size = (int(img.get_width() * scale), 
                          int(img.get_height() * scale))
                scaled = pygame.transform.scale(img, new_size)
                
                # Центрируем
                x = (self.img_size - new_size[0]) // 2
                y = (self.img_size - new_size[1]) // 2
                cell.blit(scaled, (x, y))
            
            # Рамка
            pygame.draw.rect(cell, (80, 80, 80), cell.get_rect(), 1)
            
            # Помещаем в сетку
            self.grid_surface.blit(cell, (col * self.img_size, row * self.img_size))
    
    def draw(self, x, y):
        """Отрисовка сетки на экране"""
        self.screen.blit(self.grid_surface, (x, y))
    
    def get_image_key(self, mouse_x, mouse_y, grid_x, grid_y):
        """Получить ключ изображения по координатам мыши"""
        rel_x = mouse_x - grid_x
        rel_y = mouse_y - grid_y
        
        if 0 <= rel_x < self.grid_width and 0 <= rel_y < self.grid_height:
            col = rel_x // self.img_size
            row = rel_y // self.img_size
            idx = row * self.cols + col
            
            if idx < len(self.images):
                return list(self.images.keys())[idx]
        return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((1250, 900))
    pygame.display.set_caption("Image Grid")
    clock = pygame.time.Clock()
    
    # Создаем сетку
    grid = ImageGrid(screen)
    grid_pos = (50, 50)
    
    # Шрифт для информации
    font = pygame.font.Font(None, 24)
    info_text = ""
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                key = grid.get_image_key(event.pos[0], event.pos[1], grid_pos[0], grid_pos[1])
                if key:
                    info_text = f"Selected: {key}"
        
        # Отрисовка
        screen.fill((30, 30, 30))
        grid.draw(grid_pos[0], grid_pos[1])
        
        if info_text:
            text = font.render(info_text, True, (255, 255, 255))
            screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()