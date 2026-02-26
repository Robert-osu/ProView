import pygame

class Scrollbar:
    def __init__(self, x, y, width, height, content_height, view_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = content_height
        self.view_height = view_height
        self.scroll_y = 0
        self.dragging = False
        self.drag_offset = 0
        
        # Минимальная высота ползунка
        self.min_handle_height = 30
        self.update_handle()
        
    def update_handle(self):
        """Обновляет размер и позицию ползунка"""
        if self.content_height <= self.view_height:
            self.handle_height = self.min_handle_height
            self.handle_y = self.rect.y
        else:
            # Высота ползунка пропорциональна видимой области
            visible_ratio = self.view_height / self.content_height
            self.handle_height = max(self.min_handle_height, 
                                   self.rect.height * visible_ratio)
            
            # Позиция ползунка пропорциональна прокрутке
            scroll_ratio = self.scroll_y / (self.content_height - self.view_height)
            max_handle_y = self.rect.height - self.handle_height
            self.handle_y = self.rect.y + (max_handle_y * scroll_ratio)
    
    def handle_event(self, event):
        """Обрабатывает события мыши"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка
                mouse_x, mouse_y = event.pos
                # Проверяем, попали ли в ползунок
                handle_rect = pygame.Rect(self.rect.x, int(self.handle_y), 
                                        self.rect.width, int(self.handle_height))
                if handle_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = True
                    self.drag_offset = mouse_y - self.handle_y
                    return True
                
                # Проверяем, попали ли в область скролбара выше/ниже ползунка
                elif self.rect.collidepoint(mouse_x, mouse_y):
                    if mouse_y < self.handle_y:  # Выше ползунка
                        self.scroll_y -= self.view_height * 0.5
                    else:  # Ниже ползунка
                        self.scroll_y += self.view_height * 0.5
                    
                    self.scroll_y = max(0, min(self.scroll_y, 
                                            self.content_height - self.view_height))
                    self.update_handle()
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                # Вычисляем новую позицию ползунка
                new_handle_y = mouse_y - self.drag_offset
                new_handle_y = max(self.rect.y, 
                                min(new_handle_y, 
                                self.rect.y + self.rect.height - self.handle_height))
                
                # Конвертируем позицию ползунка в значение прокрутки
                scroll_range = self.content_height - self.view_height
                if scroll_range > 0:
                    handle_range = self.rect.height - self.handle_height
                    scroll_ratio = (new_handle_y - self.rect.y) / handle_range
                    self.scroll_y = scroll_ratio * scroll_range
                
                self.handle_y = new_handle_y
                return True
        
        return False
    
    def draw(self, screen):
        """Рисует скролбар"""
        # Фон скролбара
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 1)
        
        # Ползунок
        handle_rect = pygame.Rect(self.rect.x, int(self.handle_y), 
                                self.rect.width, int(self.handle_height))
        
        # Цвет ползунка зависит от состояния
        color = (150, 150, 150) if not self.dragging else (180, 180, 180)
        pygame.draw.rect(screen, color, handle_rect)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect, 1)
        
        # Рисуем небольшие стрелки или индикаторы
        center_x = self.rect.centerx
        
        # Верхняя стрелка (серый треугольник)
        if self.scroll_y > 0:
            pygame.draw.polygon(screen, (180, 180, 180), 
                            [(center_x, self.rect.y + 5),
                                (center_x - 5, self.rect.y + 15),
                                (center_x + 5, self.rect.y + 15)])
        
        # Нижняя стрелка
        if self.scroll_y < self.content_height - self.view_height:
            pygame.draw.polygon(screen, (180, 180, 180), 
                            [(center_x, self.rect.bottom - 5),
                                (center_x - 5, self.rect.bottom - 15),
                                (center_x + 5, self.rect.bottom - 15)])