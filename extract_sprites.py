from PIL import Image
import os

def extract_grid_sprites(sprite_sheet_path, rows, cols, output_dir):
    """
    Извлечение спрайтов из равномерной сетки
    sprite_sheet_path: путь к изображению
    rows: количество строк
    cols: количество столбцов
    output_dir: папка для сохранения
    """
    # Открываем изображение
    sheet = Image.open(sprite_sheet_path)
    sheet_width, sheet_height = sheet.size
    
    # Вычисляем размер одного спрайта
    sprite_width = 32
    sprite_height = 32
    
    # Создаем папку для результатов
    os.makedirs(output_dir, exist_ok=True)
    
    # Проходим по всем ячейкам сетки
    for row in range(rows):
        for col in range(cols):
            # Координаты текущего спрайта
            left = col * sprite_width + 20
            top = row * sprite_height + 38
            right = left + sprite_width
            bottom = top + sprite_height
            
            # Вырезаем спрайт
            sprite = sheet.crop((left, top, right, bottom))
            
            # Сохраняем с именем по позиции
            filename = f"sprite_row{row}_col{col}.png"
            sprite.save(os.path.join(output_dir, filename))
    
    print(f"Извлечено {rows * cols} спрайтов в {output_dir}")

# Использование
extract_grid_sprites("prog_icons.jpg", rows=12, cols=16, output_dir="sprites")