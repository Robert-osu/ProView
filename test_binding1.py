import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine

class KeyBindWindow:
    def __init__(self, manager, viewer):
        self.manager = manager
        self.viewer = viewer  # Ссылка на основной класс
        self.active = True
        self.waiting_for_key = None

        # Загружаем текущие назначения из viewer
        self.key_bindings = viewer.key_bindings if viewer.key_bindings else {
            'ВВЕРХ': pygame.K_UP,
            'ВНИЗ': pygame.K_DOWN,
            'ВЛЕВО': pygame.K_LEFT,
            'ВПРАВО': pygame.K_RIGHT,
            'ДЕЙСТВИЕ': pygame.K_SPACE,
            'МЕНЮ': pygame.K_ESCAPE
        }
        
        # Создаем окно
        self.window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(100, 50, 400, 500),
            manager=manager,
            window_display_title='Настройка горячих клавиш'
        )
        
        self.create_ui()
    
    def create_ui(self):
        y_offset = 50
        self.buttons = {}
        
        for i, (action, key) in enumerate(self.key_bindings.items()):
            # Название действия и функция
            func_name = self.viewer.key_functions.get(action, None)
            func_text = f" ({func_name.__name__})" if func_name else " (нет функции)"

            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, y_offset + i*40, 200, 30),
                text=action + func_text,
                manager=self.manager,
                container=self.window
            )
            
            # Кнопка с текущей клавишей
            key_name = pygame.key.name(key)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(230, y_offset + i*40, 100, 30),
                text=key_name.upper(),
                manager=self.manager,
                container=self.window,
                object_id=f'#key_{action}'
            )
            self.buttons[action] = button
        
        # Кнопка сохранения
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(175, 320, 100, 40),
            text='Сохранить',
            manager=self.manager,
            container=self.window
        )
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.waiting_for_key:
            # Запись новой клавиши
            self.key_bindings[self.waiting_for_key] = event.key
            self.buttons[self.waiting_for_key].set_text(pygame.key.name(event.key).upper())
            self.waiting_for_key = None
            return True
        
        elif event.type == pygame.USEREVENT:
            if hasattr(event, 'ui_element'):
                # Проверяем, не является ли элемент частью нашего окна
                element_container = getattr(event.ui_element, 'container', None)
                if element_container == self.window or event.ui_element == self.window:
                    
                    # Обработка закрытия окна (кнопка [X])
                    if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                        if event.ui_element == self.window:
                            self.close_window()
                            return True
                    
                    # Обработка нажатия на кнопки действий
                    elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        # Проверяем кнопки действий
                        for action, button in self.buttons.items():
                            if event.ui_element == button:
                                self.waiting_for_key = action
                                button.set_text('...')
                                return True
                        
                        # Проверяем кнопку сохранения
                        if event.ui_element == self.save_button:
                            self.save_bindings()
                            return True
        
        return False

    def show_warning(self, message):
        """Показывает предупреждение"""
        import pygame_gui.windows.ui_message_window as message_window
        message_window.UIMessageWindow(
            rect=pygame.Rect(200, 200, 300, 150),
            manager=self.manager,
            window_title='Предупреждение',
            html_message=message
        )

    def save_bindings(self):
        """Сохраняет назначения клавиш в viewer"""
        # Обновляем привязки в viewer
        self.viewer.key_bindings = self.key_bindings.copy()
        
        # Обновляем функции если нужно (опционально)
        # Можно добавить логику обновления key_functions если нужно
        
        self.close_window()
        print("Назначения клавиш сохранены!")

    def close_window(self):
        """Закрывает окно и очищает ресурсы"""
        self.active = False
        if self.window and self.window.alive():
            self.window.kill()
        self.viewer.need_redraw = True
        print("Окно закрыто")

    def draw(self):
        # pygame_gui сам рисует окно через manager.draw_ui()
        pass


if __name__ == "__main__":
    # Использование
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))
    key_window = KeyBindWindow(manager)

    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60)/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not key_window.handle_event(event):
                manager.process_events(event)
        
        manager.update(time_delta)
        
        screen.fill((0, 0, 0))
        manager.draw_ui(screen)
        pygame.display.update()