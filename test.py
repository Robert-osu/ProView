import pygame
from my_lib.GameObjectRenderer import GameObject

class SideMenu(GameObject):
    def __init__(self, viewer_context, z_order=10):  # Высокий z_order для отображения поверх всего
        super().__init__(z_order)
        self.ctx = viewer_context
        self.screen = self.ctx.screen
        
        # Состояние меню
        self.is_visible = False
        self.animation_progress = 0.0  # 0 - скрыто, 1 - полностью открыто
        self.animation_speed = 0.1
        
        # Параметры меню
        self.menu_width = 300
        self.menu_height = self.ctx.window_height - 100
        self.menu_x = -self.menu_width  # Начальная позиция за левым краем
        self.menu_y = 50
        
        # Цвета
        self.bg_color = (30, 30, 30)
        self.border_color = (100, 100, 100)
        self.header_color = (50, 50, 50)
        self.item_color = (40, 40, 40)
        self.item_hover_color = (60, 60, 60)
        self.text_color = (220, 220, 220)
        self.text_color_bright = (255, 255, 255)
        
        # Шрифты
        self.header_font = pygame.font.SysFont('arial', 20, bold=True)
        self.item_font = pygame.font.SysFont('arial', 16)
        
        # Элементы меню
        self.menu_items = []
        self.current_hover = -1
        self.create_menu_items()
        
        # Кнопка закрытия
        self.close_button_rect = None
        
        # Поверхность для меню (кэширование)
        self.menu_surface = None
        self.need_redraw = True
    
    def create_menu_items(self):
        """Создает элементы меню"""
        self.menu_items = [
            {"type": "header", "text": "ФАЙЛ"},
            {"type": "item", "text": "Новый проект", "action": "new_project", "icon": "📄"},
            {"type": "item", "text": "Открыть...", "action": "open_project", "icon": "📂"},
            {"type": "item", "text": "Сохранить", "action": "save_project", "icon": "💾"},
            {"type": "item", "text": "Сохранить как...", "action": "save_as", "icon": "📁"},
            {"type": "separator"},
            
            {"type": "header", "text": "ПРАВКА"},
            {"type": "item", "text": "Копировать", "action": "copy", "icon": "📋"},
            {"type": "item", "text": "Вставить", "action": "paste", "icon": "📌"},
            {"type": "item", "text": "Удалить", "action": "delete", "icon": "❌"},
            {"type": "separator"},
            
            {"type": "header", "text": "ВИД"},
            {"type": "item", "text": "Увеличить", "action": "zoom_in", "icon": "🔍+"},
            {"type": "item", "text": "Уменьшить", "action": "zoom_out", "icon": "🔍-"},
            {"type": "item", "text": "Сбросить масштаб", "action": "zoom_reset", "icon": "🔄"},
            {"type": "separator"},
            
            {"type": "header", "text": "ПОМОЩЬ"},
            {"type": "item", "text": "О программе", "action": "about", "icon": "ℹ️"},
            {"type": "item", "text": "Документация", "action": "docs", "icon": "📚"},
        ]
    
    def toggle(self):
        """Переключает видимость меню"""
        self.is_visible = not self.is_visible
        self.need_redraw = True
    
    def show(self):
        """Показывает меню"""
        self.is_visible = True
        self.need_redraw = True
    
    def hide(self):
        """Скрывает меню"""
        self.is_visible = False
        self.need_redraw = True
    
    def _draw(self):
        """Отрисовка меню"""
        if not self.is_visible and self.animation_progress <= 0:
            return
        
        # Анимация появления/исчезновения
        if self.is_visible and self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
            self.need_redraw = True
        elif not self.is_visible and self.animation_progress > 0:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)
            self.need_redraw = True
        
        if self.need_redraw:
            self._create_menu_surface()
        
        if self.menu_surface:
            # Вычисляем текущую позицию меню с учетом анимации
            current_x = -self.menu_width + int(self.menu_width * self.animation_progress)
            
            # Затемнение фона под меню
            if self.animation_progress > 0:
                overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                overlay.set_alpha(int(100 * self.animation_progress))
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
            
            # Отрисовываем меню
            self.screen.blit(self.menu_surface, (current_x, self.menu_y))
    
    def _create_menu_surface(self):
        """Создает поверхность меню"""
        # Создаем поверхность для меню
        self.menu_surface = pygame.Surface((self.menu_width, self.menu_height))
        self.menu_surface.fill(self.bg_color)
        
        # Рисуем границу
        pygame.draw.rect(self.menu_surface, self.border_color, 
                        self.menu_surface.get_rect(), 2, border_radius=10)
        
        # Заголовок меню
        header_rect = pygame.Rect(0, 0, self.menu_width, 40)
        pygame.draw.rect(self.menu_surface, self.header_color, header_rect, 
                        border_top_left_radius=10, border_top_right_radius=10)
        
        title_text = self.header_font.render("МЕНЮ", True, self.text_color_bright)
        title_rect = title_text.get_rect(center=(self.menu_width // 2, 20))
        self.menu_surface.blit(title_text, title_rect)
        
        # Кнопка закрытия (X)
        self.close_button_rect = pygame.Rect(self.menu_width - 35, 10, 25, 25)
        pygame.draw.rect(self.menu_surface, (80, 80, 80), self.close_button_rect, border_radius=5)
        pygame.draw.line(self.menu_surface, (200, 200, 200), 
                        (self.menu_width - 30, 15), (self.menu_width - 15, 30), 2)
        pygame.draw.line(self.menu_surface, (200, 200, 200), 
                        (self.menu_width - 15, 15), (self.menu_width - 30, 30), 2)
        
        # Рисуем элементы меню
        y_offset = 50
        item_height = 30
        separator_height = 10
        
        for i, item in enumerate(self.menu_items):
            if item["type"] == "header":
                # Заголовок раздела
                header_text = self.header_font.render(item["text"], True, (150, 150, 150))
                self.menu_surface.blit(header_text, (15, y_offset))
                y_offset += 25
                
            elif item["type"] == "item":
                # Элемент меню
                item_rect = pygame.Rect(5, y_offset, self.menu_width - 10, item_height)
                
                # Подсветка при наведении
                if i == self.current_hover:
                    pygame.draw.rect(self.menu_surface, self.item_hover_color, item_rect, border_radius=5)
                
                # Иконка
                if "icon" in item:
                    icon_text = self.item_font.render(item["icon"], True, self.text_color)
                    self.menu_surface.blit(icon_text, (15, y_offset + 5))
                
                # Текст
                text = self.item_font.render(item["text"], True, self.text_color)
                self.menu_surface.blit(text, (45, y_offset + 5))
                
                # Сохраняем прямоугольник для обработки кликов
                item["rect"] = pygame.Rect(self.menu_x + 5, self.menu_y + y_offset, 
                                         self.menu_width - 10, item_height)
                
                y_offset += item_height
                
            elif item["type"] == "separator":
                # Разделитель
                pygame.draw.line(self.menu_surface, (60, 60, 60), 
                               (10, y_offset + separator_height // 2), 
                               (self.menu_width - 10, y_offset + separator_height // 2), 1)
                y_offset += separator_height
        
        self.need_redraw = False
    
    def _update(self):
        """Обновление состояния меню"""
        if not self.is_visible and self.animation_progress == 0:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        current_x = -self.menu_width + int(self.menu_width * self.animation_progress)
        
        # Проверяем наведение на элементы
        if self.is_visible and self.animation_progress > 0.9:
            # Корректируем координаты мыши для локальной системы меню
            local_x = mouse_x - current_x
            local_y = mouse_y - self.menu_y
            
            if 0 <= local_x <= self.menu_width and 0 <= local_y <= self.menu_height:
                # Проверяем наведение на элементы меню
                new_hover = -1
                y_offset = 50
                item_height = 30
                
                for i, item in enumerate(self.menu_items):
                    if item["type"] == "header":
                        y_offset += 25
                    elif item["type"] == "item":
                        if y_offset <= local_y <= y_offset + item_height:
                            new_hover = i
                            break
                        y_offset += item_height
                    elif item["type"] == "separator":
                        y_offset += 10
                
                if new_hover != self.current_hover:
                    self.current_hover = new_hover
                    self.need_redraw = True
                
                # Проверяем наведение на кнопку закрытия
                close_local_rect = pygame.Rect(self.menu_width - 35, 10, 25, 25)
                if close_local_rect.collidepoint(local_x, local_y):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            else:
                if self.current_hover != -1:
                    self.current_hover = -1
                    self.need_redraw = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _execute(self):
        """Обработка событий"""
        pass
    
    def handle_event(self, event):
        """Обрабатывает события для меню"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.is_visible:
                self.hide()
                return True
            elif event.key == pygame.K_m:  # Нажатие M для открытия меню
                self.toggle()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_visible and self.animation_progress > 0.9:
                mouse_x, mouse_y = event.pos
                current_x = -self.menu_width + int(self.menu_width * self.animation_progress)
                
                # Корректируем координаты для локальной системы меню
                local_x = mouse_x - current_x
                local_y = mouse_y - self.menu_y
                
                # Проверяем клик по кнопке закрытия
                close_local_rect = pygame.Rect(self.menu_width - 35, 10, 25, 25)
                if close_local_rect.collidepoint(local_x, local_y):
                    self.hide()
                    return True
                
                # Проверяем клик по элементам меню
                y_offset = 50
                item_height = 30
                
                for i, item in enumerate(self.menu_items):
                    if item["type"] == "header":
                        y_offset += 25
                    elif item["type"] == "item":
                        if y_offset <= local_y <= y_offset + item_height:
                            self.handle_menu_action(item["action"])
                            self.hide()
                            return True
                        y_offset += item_height
                    elif item["type"] == "separator":
                        y_offset += 10
            
            # Клик вне меню - закрываем
            elif self.is_visible:
                self.hide()
                return True
        
        return False
    
    def handle_menu_action(self, action):
        """Обрабатывает действия меню"""
        print(f"Выполняется действие: {action}")
        
        # Здесь можно добавить вызовы соответствующих методов
        if action == "new_project":
            # Очистка текущего проекта
            self.ctx.pro._commands.clear()
            self.ctx.re_grid = True
            
        elif action == "save_project":
            # Сохранение проекта
            print("Сохранение проекта...")
            
        elif action == "open_project":
            # Открытие проекта
            print("Открытие проекта...")
            
        elif action == "zoom_in":
            # Увеличение масштаба
            self.ctx.thumb_size = min(100, self.ctx.thumb_size + 10)
            self.ctx.re_grid = True
            
        elif action == "zoom_out":
            # Уменьшение масштаба
            self.ctx.thumb_size = max(30, self.ctx.thumb_size - 10)
            self.ctx.re_grid = True
            
        elif action == "zoom_reset":
            # Сброс масштаба
            self.ctx.thumb_size = 50
            self.ctx.re_grid = True
            
        elif action == "about":
            # Информация о программе
            print("Моя программа v1.0")
