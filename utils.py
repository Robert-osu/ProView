import glob
import os
from PIL import Image
from Command import Command
import numpy as np
import pygame

class ValueTracker:
    def __init__(self, initial_value=None):
        self.current = initial_value
        self.previous = None
        self.changed = False
    
    def update(self, new_value):
        if new_value != self.current:
            self.previous = self.current
            self.current = new_value
            self.changed = True
        else:
            self.changed = False

class GetImage:
    def __init__(self, thumb_s, name_folder="sprites_standart"):
        self.thumb_size = thumb_s

        self.image_paths = self._get_paths(name_folder)
        self.images = []
        self.image_names = []
        self.cmd_images = {}

        self._load_images()

        self.thumbnails = []
        
        

        self._create_thumbnails()

    def get(self):
        return self.cmd_images

    def _get_paths(self, dir_folder="sprites_standart"):
        """Получение списка изображений из папки"""
        print(f"[DEBUG] get_images: поиск в папке {dir_folder}")
        image_files = glob.glob(os.path.join(dir_folder, "*.png"))
        image_files.sort()
        print(f"[DEBUG] Найдено изображений: {len(image_files)}")
        return image_files

    def _load_images(self):
        """Загружает изображения с помощью PIL"""
        print(f"[DEBUG] load_images: загрузка {len(self.image_paths)} изображений")
        for path in self.image_paths:
            try:
                img = Image.open(path)
                self.images.append(img)
                # Сохраняем имя файла без пути
                name = os.path.splitext(os.path.basename(path))[0]
                self.image_names.append(name)
                print(f"[DEBUG] Загружено: {name}")
            except Exception as e:
                print(f"[DEBUG] Ошибка загрузки {path}: {e}")
        
        print(f"[DEBUG] Всего загружено изображений: {len(self.images)}")
        
    def _create_thumbnails(self):
        """Создает миниатюры для всех изображений"""
        print(f"[DEBUG] create_thumbnails: создание миниатюр")
        i = 0
        for img in self.images:
            img_copy = img.copy()
            img_copy.thumbnail((self.thumb_size, self.thumb_size), Image.Resampling.LANCZOS)
            
            thumb = Image.new('RGB', (self.thumb_size, self.thumb_size), (255, 255, 255))
            
            offset_x = (self.thumb_size - img_copy.width) // 2
            offset_y = (self.thumb_size - img_copy.height) // 2
            thumb.paste(img_copy, (offset_x, offset_y))
            
            surface = self._pil_to_pygame(thumb)
            self.thumbnails.append(surface)

            try:
                cmd = Command[self.image_names[i]]
                self.cmd_images[cmd] = surface
                print(f"[DEBUG] Команда {cmd} связана с изображением {self.image_names[i]}")
            except KeyError:
                print(f"[DEBUG] Команда {self.image_names[i]} не найдена в Command")
                # Используем значение по умолчанию
                if hasattr(Command, 'EMPTY'):
                    self.cmd_images[Command.EMPTY] = surface
            i += 1
        
        print(f"[DEBUG] Создано миниатюр: {len(self.thumbnails)}")

    def _pil_to_pygame(self, pil_image):
        """Конвертирует PIL Image в pygame Surface"""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        img_array = np.array(pil_image)
        surface = pygame.surfarray.make_surface(img_array.swapaxes(0, 1))
        return surface


def test_vtrack():
    # Пример использования
    v = ValueTracker(10)
    print(v.current)  # 10
    print(v.previous)  # None

    v.update(20)  # Значение изменено: 10 -> 20
    print(f"Текущее: {v.current}, Предыдущее: {v.previous}")
    v.update(20)  # Значение не изменилось
    print(f"Текущее: {v.current}, Предыдущее: {v.previous}")
    v.update(30)  # Значение изменено: 20 -> 30

    print(f"Текущее: {v.current}, Предыдущее: {v.previous}")  # Текущее: 30, Предыдущее: 20

def test_images():
    k_images = GetImage(16).get()
    print(k_images)

if __name__ == "__main__":
    test_images()