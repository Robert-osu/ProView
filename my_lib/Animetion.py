from abc import ABC, abstractmethod
from typing import Callable, Any
import pygame

import math

class Animation(ABC):
    def __init__(self, duration_frames: int):
        self.duration_frames = duration_frames
        self.current_frame = 0
        self.is_active = False
        self.on_complete: Callable[[], None] = None
        self.easing_function: Callable[[float], float] = lambda x: x  # линейная по умолчанию
    
    def start(self):
        self.current_frame = 0
        self.is_active = True
    
    def update(self) -> bool:
        """Возвращает True если анимация завершена"""
        if not self.is_active:
            return False
            
        self.current_frame += 1
        progress = self.current_frame / self.duration_frames
        eased_progress = self.easing_function(progress)
        
        self._apply_animation(eased_progress)
        
        if self.current_frame >= self.duration_frames:
            self.is_active = False
            if self.on_complete:
                self.on_complete()
            return True
        return False
    
    @abstractmethod
    def _apply_animation(self, progress: float):
        """Применить анимацию с учетом прогресса (0.0 - 1.0)"""
        pass
    
    def set_easing(self, easing_func: Callable[[float], float]):
        self.easing_function = easing_func



class MoveAnimation(Animation):
    def __init__(self, target_obj, start_pos: tuple, end_pos: tuple, duration_frames: int):
        super().__init__(duration_frames)
        self.target_obj = target_obj
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def _apply_animation(self, progress: float):
        self.target_obj.rect.x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        self.target_obj.rect.y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

class ScaleAnimation(Animation):
    def __init__(self, target_obj, start_scale: float, end_scale: float, duration_frames: int):
        super().__init__(duration_frames)
        self.target_obj = target_obj
        self.start_scale = start_scale
        self.end_scale = end_scale
    
    def _apply_animation(self, progress: float):
        scale = self.start_scale + (self.end_scale - self.start_scale) * progress
        self.target_obj.image = pygame.transform.scale(
            self.original_image, 
            (int(self.original_rect.width * scale), int(self.original_rect.height * scale))
        )

class FadeAnimation(Animation):
    def __init__(self, target_obj, start_alpha: int, end_alpha: int, duration_frames: int):
        super().__init__(duration_frames)
        self.target_obj = target_obj
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
    
    def _apply_animation(self, progress: float):
        alpha = self.start_alpha + (self.end_alpha - self.start_alpha) * progress
        self.target_obj.image.set_alpha(alpha)

class RotateAnimation(Animation):
    def __init__(self, target_obj, start_angle: float, end_angle: float, duration_frames: int):
        super().__init__(duration_frames)
        self.target_obj = target_obj
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.original_image = target_obj.image.copy()
    
    def _apply_animation(self, progress: float):
        angle = self.start_angle + (self.end_angle - self.start_angle) * progress
        self.target_obj.image = pygame.transform.rotate(self.original_image, angle)




class Easing:
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def bounce(t: float) -> float:
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375