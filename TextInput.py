import pygame
import sys
from my_lib.GameObjectRenderer import GameObject


class TextInput(GameObject):
    def __init__(self, viewer_context, x, y, width, height, max_length=20):
        super().__init__(1000)
        self.ctx = viewer_context
        self.screen = self.ctx.screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.color_inactive = (100, 100, 100)
        self.color_active = (200, 200, 200)
        self.color = self.color_inactive
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = font = pygame.font.SysFont('arial', 12)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                print(f"Введенный текст: {self.text}")
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
            self.ctx.re_grid = True

    def _execute(self):
        pass

    def _update(self):
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

    def _draw(self):
        # Матричный зеленый
        text_color = (0, 255, 255)  # Ярко-зеленый
        glow_color = (0, 150, 0)  # Темно-зеленый для свечения
        
        text_surface = self.font.render(self.text, True, text_color)
        
        # Эффект свечения
        glow_surface = self.font.render(self.text, True, glow_color)
        self.screen.blit(glow_surface, (self.rect.x + 4, self.rect.y + 4))
        self.screen.blit(glow_surface, (self.rect.x + 6, self.rect.y + 6))
        
        # Основной текст поверх
        self.screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # Курсор
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surface.get_width()
            cursor_y = self.rect.y + 5
            cursor_height = text_surface.get_height()
            pygame.draw.line(self.screen, text_color, 
                        (cursor_x, cursor_y), 
                        (cursor_x, cursor_y + cursor_height), 3)
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    input_field = TextInput(100, 100, 64, 20)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            input_field.handle_event(event)
        
        input_field._update()
        
        screen.fill((30, 30, 30))
        input_field._draw(screen)
        
        pygame.display.flip()
        clock.tick(60)