import pygame
import pygame_gui

from my_lib.GameObjectRenderer import GameObject
from test_binding1 import KeyBindWindow

# --- Класс для UI (pygame_gui) ---
class UIManagerObject(GameObject):
    def __init__(self, viewer_context, z_order=20):
        super().__init__(z_order)
        print(f"[DEBUG] UIManagerObject.__init__: viewer_context={viewer_context}, z_order={z_order}")
        self.ctx = viewer_context
        self.ui_manager = pygame_gui.UIManager((self.ctx.window_width, self.ctx.window_height))
        self.menu_buttons = [] # Кнопки будем хранить здесь
        self.key_bind_window = None
        self.create_menu_button()

    def _draw(self):
        if self.ctx.re_ui:
            # Рисуем UI поверх всего
            self.ui_manager.draw_ui(self.ctx.screen)

            pygame.display.flip()
            self.ctx.re_ui = False
        if self.key_bind_window and self.key_bind_window.active:
            self.key_bind_window.draw()

    def _update(self):
        time_delta = self.ctx.clock.tick(60)/1000.0
        self.ui_manager.update(time_delta)

    def _execute(self):
        # Здесь обработка событий pygame_gui, которые приходят из viewer
        pass

    def create_menu_button(self):
        """Создание нескольких кнопок на панели"""
        print(f"[DEBUG] UIManagerObject.create_menu_button: создание кнопок")
        button_width = int(100 * self.ctx.k_size)
        button_height = int(30 * self.ctx.k_size)
        button_margin = int(10 * self.ctx.k_size)
        
        self.menu_buttons = []
        
        # Кнопка "Меню"
        btn1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.ctx.padding, 
                (self.ctx.panel_height - button_height) // 2, 
                button_width, 
                button_height
            ),
            text="Меню",
            manager=self.ui_manager
        )
        self.menu_buttons.append(btn1)
        
        # Кнопка "Настройки"
        btn2 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.ctx.padding + button_width + button_margin, 
                (self.ctx.panel_height - button_height) // 2, 
                button_width, 
                button_height
            ),
            text='Настройки',
            manager=self.ui_manager
        )
        self.menu_buttons.append(btn2)
        
        # Кнопка "Помощь"
        btn3 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.ctx.padding + (button_width + button_margin) * 2, 
                (self.ctx.panel_height - button_height) // 2, 
                button_width, 
                button_height
            ),
            text='Помощь',
            manager=self.ui_manager
        )
        self.menu_buttons.append(btn3)
        print(f"[DEBUG] UIManagerObject.create_menu_button: создано {len(self.menu_buttons)} кнопок")

    def open_settings(self):
        """Открывает окно настройки горячих клавиш"""
        print(f"[DEBUG] UIManagerObject.open_settings: открытие окна настроек")
        if self.key_bind_window and self.key_bind_window.active:
            return
        
        self.key_bind_window = KeyBindWindow(self.ui_manager, self)
