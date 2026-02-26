from PIL import Image
import os

def extract_and_rename_sprites(sprite_sheet_path, rows, cols, output_dir, command_enum):
    """
    Извлечение спрайтов из равномерной сетки и переименование согласно порядку в Command
    """
    # Открываем изображение
    sheet = Image.open(sprite_sheet_path)
    
    # Размер одного спрайта
    sprite_width = 32
    sprite_height = 32
    
    # Создаем папку для результатов
    os.makedirs(output_dir, exist_ok=True)
    
    # Получаем все имена из Command Enum в порядке возрастания значений
    # Сортируем по байтовому значению
    command_names = []
    for cmd in command_enum:
        command_names.append(cmd.name)
    
    print(f"Найдено команд в Enum: {len(command_names)}")
    
    # Счетчик для отслеживания позиции
    index = 0
    
    # Проходим по всем ячейкам сетки
    for row in range(rows):
        for col in range(cols):
            # Координаты текущего спрайта (с вашими смещениями)
            left = col * sprite_width + 20
            top = row * sprite_height + 38
            right = left + sprite_width
            bottom = top + sprite_height
            
            # Вырезаем спрайт
            sprite = sheet.crop((left, top, right, bottom))
            
            # Определяем имя файла
            if index < len(command_names):
                # Берем имя из Command Enum
                filename = f"{command_names[index]}.png"
            else:
                # Стандартное имя для остальных
                filename = f"icon_row{row}_col{col}.png"
            
            # Сохраняем
            filepath = os.path.join(output_dir, filename)
            sprite.save(filepath)
            
            print(f"Сохранено: {filename}")
            
            index += 1
    
    print(f"\nИзвлечено {rows * cols} спрайтов в {output_dir}")
    print(f"Из них названы по Command: {min(len(command_names), rows*cols)}")
    print(f"Остальные названы стандартно: {max(0, rows*cols - len(command_names))}")

# Ваш класс Command
from enum import Enum

class Command(Enum):
    EMPTY = b'\x00'
    NEWLINE = b'\x01'
    START = b'\x02'
    STOP = b'\x03'
    MOVE_TOP = b'\x04'
    MOVE_LEFT = b'\x05'
    MOVE_BOTTOM = b'\x06'
    MOVE_RIGHT = b'\x07'
    DIG = b'\x08'
    DIR_TOP = b'\x09'
    DIR_LEFT = b'\x0A'
    DIR_BOTTOM = b'\x0B'
    DIR_RIGHT = b'\x0C'
    REPEAT = b'\x0D'
    MOVE_FORWARD = b'\x0E'
    ROTATE_LEFT = b'\x0F'

    ROTATE_RIGHT = b'\x10'
    BUILD_BLOCK = b'\x11'
    GEO = b'\x12'
    BUILD_ROAD = b'\x13'
    HEAL = b'\x14'
    BUILD_QUADRO = b'\x15'
    DIR_RANDOM = b'\x16'
    ALARM = b'\x17'
    GO_TO = b'\x18'
    CALL_FUNC = b'\x19'
    CALL_FUNC_CONDITION = b'\x1A'
    RETURN = b'\x1B'
    RETURN_ARGUMENT = b'\x1C'
    CHECK_TOP_LEFT = b'\x1D'
    CHECK_BOTTOM_RIGHT = b'\x1E'
    CHECK_TOP = b'\x1F'

    CHECK_TOP_RIGHT = b'\x20'
    CHECK_LEFT = b'\x21'
    CHECK_CENTER = b'\x22'
    CHECK_RIGHT = b'\x23'
    CHECK_BOTTOM_LEFT = b'\x24'
    CHECK_BOTTOM = b'\x25'
    OR = b'\x26'
    AND = b'\x27'
    LABEL = b'\x28'
    YES_NO_RETURN = b'\x29'
    NO_YES_RETURN = b'\x2A'
    IS_NOT_EMPTY = b'\x2B'
    IS_EMPTY = b'\x2C'
    IS_FALLING = b'\x2D'
    IS_CRYSTAL = b'\x2E'
    IS_ALIVE_CRYSTAL = b'\x2F'

    IS_FALLING_GRAVEL = b'\x30'
    IS_FALLING_SAND = b'\x31'
    IS_BREAKABLE = b'\x32'
    IS_UNBREAKABLE = b'\x33'
    IS_KRASNOSKAL = b'\x34'
    IS_CHERNOSKAL = b'\x35'
    IS_SLIME = b'\x36'
    IS_ERROR1 = b'\x37'
    IS_SAND_YB = b'\x38'
    IS_QUADRO = b'\x39'
    IS_ROAD = b'\x3A'
    IS_RED_BLOCK = b'\x3B'
    IS_YELLOW_BLOCK = b'\x3C'
    IS_HP_LESS_90 = b'\x3D'
    IS_HP_LESS_50 = b'\x3E'
    IS_KISLOTKA = b'\x3F'

    IS_COMMON_GRAVEL = b'\x40'
    IS_LAVA = b'\x41'
    IS_ALIVE_CYAN = b'\x42'
    IS_ALIVE_WHITE = b'\x43'
    IS_ALIVE_RED = b'\x44'
    IS_ALIVE_VIOLET = b'\x45'
    IS_ALIVE_BLACK = b'\x46'
    IS_ALIVE_BLUE = b'\x47'
    IS_ALIVE_RAINBOW = b'\x48'
    IS_ERROR2 = b'\x49'
    IS_BOX = b'\x4A'
    IS_ERROR3 = b'\x4B'
    IS_OPORA = b'\x4C'
    IS_GREEN_BLOCK = b'\x4D'
    IS_FULL = b'\x4E'
    IS_FULL_GEO = b'\x4F'

    IS_ERROR4 = b'\x50'
    AFTER_RESPAWN = b'\x51'
    AFTER_DAMAGE = b'\x52'
    AFTER_ROBOTS = b'\x53'
    IS_ERROR5 = b'\x54'
    IS_ERROR6 = b'\x55'
    OFFSET_LEFT_HAND = b'\x56'
    OFFSET_RIGHT_HAND = b'\x57'
    OFFSET_BEHIND = b'\x58'
    BOX_ALL = b'\x59'
    BOX_HALF = b'\x5A'
    BOX_WHITE = b'\x5B'
    BOX_GREEN = b'\x5C'
    BOX_RED = b'\x5D'
    BOX_BLUE = b'\x5E'
    BOX_CYAN = b'\x5F'

    BOX_VIOLET = b'\x60'
    SET = b'\x61'
    GET = b'\x62'
    SET_VALUE = b'\x63'
    ADD_VALUE = b'\x64'
    MULTIPLY_VALUE = b'\x65'
    DIVIDE_VALUE = b'\x66'
    SUBTRACT_VALUE = b'\x67'
    ADD = b'\x68'
    MULTIPLY = b'\x69'
    DIVIDE = b'\x6A'
    SUBTRACT = b'\x6B'
    ADD_VAR = b'\x6C'
    MULTIPLY_VAR = b'\x6D'
    DIVIDE_VAR = b'\x6E'
    SUBTRACT_VAR = b'\x6F'

    IS_GREATER = b'\x70'
    IS_LESS = b'\x71'
    IS_GREATER_OR_EQUAL = b'\x72'
    IS_LESS_OR_EQUAL = b'\x73'
    IS_EQUAL = b'\x74'
    IS_NOT_EQUAL = b'\x75'
    IS_ERROR7 = b'\x76'
    VAR_GREATER = b'\x77'
    VAR_LESS = b'\x78'
    VAR_GREATER_OR_EQUAL = b'\x79'
    VAR_LESS_OR_EQUAL = b'\x7A'
    VAR_EQUAL = b'\x7B'
    VAR_NOT_EQUAL = b'\x7C'
    ROUND = b'\x7D'
    ROUND_CEIL = b'\x7E'
    ROUND_FLOOR = b'\x7F'

    I_DONT_KNOW1 = b'\x80'
    I_DONT_KNOW2 = b'\x81'
    I_DONT_KNOW3 = b'\x82'
    OFFSET_TOP = b'\x83'
    OFFSET_LEFT = b'\x84'
    OFFSET_BOTTOM = b'\x85'
    OFFSET_RIGHT = b'\x86'
    CHECK_FORWARD = b'\x87'
    OFFSET_FORWARD = b'\x88'
    CALL_FUNC_STATE = b'\x89'
    RETURN_STATE = b'\x8A'
    YES_NO = b'\x8B'
    NO_YES = b'\x8C'
    STD_DIG = b'\x8D'
    STD_BUILD = b'\x8E'
    STD_HEAL = b'\x8F'

    FLIP = b'\x90'
    STD_DIG_AROUND = b'\x91'
    IS_IN_GUN = b'\x92'
    AMMO = b'\x93'
    IS_HP_LESS_100 = b'\x94'
    IS_HP_LESS_50_2 = b'\x95'
    YES_NO_NEWLINE = b'\x96'
    NO_YES_NEWLINE = b'\x97'
    YES_NO_START = b'\x98'
    NO_YES_START = b'\x99'
    YES_NO_STOP = b'\x9A'
    NO_YES_STOP = b'\x9B'
    CHECK_LEFT_HAND = b'\x9C'
    CHECK_RIGHT_HAND = b'\x9D'
    AUTO_DIG_ON = b'\x9E'
    AUTO_DIG_OFF = b'\x9F'

    AGR_ON = b'\xA0'
    AGR_OFF = b'\xA1'
    USE_BOOM = b'\xA2'
    USE_RAZRYAD = b'\xA3'
    USE_PROTON = b'\xA4'
    BUILD_WB = b'\xA5'
    RESPAWN_TO = b'\xA6'
    USE_GEOPACK = b'\xA7'
    USE_ZZ = b'\xA8'
    USE_C190 = b'\xA9'
    USE_POLIMER = b'\xAA'
    UP = b'\xAB'
    CRAFT = b'\xAC'
    USE_NANOBOT = b'\xAD'
    USE_REMBOT = b'\xAE'
    DIR_INV_TOP = b'\xAF'

    DIR_INV_LEFT = b'\xB0'
    DIR_INV_BOTTOM = b'\xB1'
    DIR_INV_RIGHT = b'\xB2'
    MODE_MANUAL = b'\xB3'
    MODE_AUTO = b'\xB4'
    I_DONT_KNOW4 = b'\xB5'
    I_DONT_KNOW5 = b'\xB6'
    
    def __str__(self):
        return self.name.lower()


# Использование
extract_and_rename_sprites(
    sprite_sheet_path="prog_icons.jpg",
    rows=12,
    cols=16,
    output_dir="sprites",
    command_enum=Command
)