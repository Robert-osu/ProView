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

### группировки по вводу значений

# Определяем диапазоны для каждой группы
NO_ARGS_RANGES = [(0x00, 0x17), (0x1B, 0x27), (0x29, 0x60), (0x76, 0x76), (0x83, 0x88), (0x8A, 0x8A), (0x8D, 0xA5), (0xA7, 0xB4)]
ONE_ARG_RANGES = [(0x18, 0x1A), (0x28, 0x28), (0x61, 0x62), (0x68, 0x6B), (0x70, 0x75), (0x7D, 0x7F), (0x89, 0x89), (0x8B, 0x8C), (0xA6, 0xA6)]
TWO_ARGS_RANGES = [(0x63, 0x67), (0x6C, 0x6F), (0x77, 0x7C), (0x80, 0x82)]

def get_commands_in_ranges(ranges):
    """Получить команды из нескольких диапазонов"""
    result = set()
    for cmd in Command:
        cmd_int = int.from_bytes(cmd.value, 'big')
        for start, end in ranges:
            if start <= cmd_int <= end:
                result.add(cmd)
                break
    return result

# Создаем группы
Command.NO_ARGS = get_commands_in_ranges(NO_ARGS_RANGES)
Command.ONE_ARGS = get_commands_in_ranges(ONE_ARG_RANGES)
Command.TWO_ARGS = get_commands_in_ranges(TWO_ARGS_RANGES)


### группировки общей тематики
Command.ACTION = {Command.MOVE_BOTTOM, Command.MOVE_LEFT, 
                  Command.MOVE_RIGHT, Command.MOVE_TOP, 
                  Command.REPEAT, Command.MOVE_FORWARD,
                  Command.DIR_BOTTOM, Command.DIR_TOP, Command.DIR_LEFT, 
                  Command.DIR_RIGHT, Command.DIR_INV_BOTTOM, Command.DIR_INV_LEFT,
                  Command.DIR_INV_RIGHT, Command.DIR_INV_TOP, Command.DIR_RANDOM,
                  Command.ROTATE_LEFT, Command.ROTATE_RIGHT,
                  Command.BUILD_BLOCK, Command.BUILD_QUADRO, Command.BUILD_ROAD,
                  Command.BUILD_WB,
                  Command.GEO, Command.HEAL, 
                  Command.STD_BUILD, Command.STD_DIG, Command.STD_DIG_AROUND, 
                  Command.STD_HEAL, 

                  Command.BOX_ALL, Command.BOX_BLUE, Command.BOX_WHITE,
                  Command.BOX_CYAN, Command.BOX_GREEN, Command.BOX_HALF,
                  Command.BOX_RED, Command.BOX_VIOLET, 

                  Command.USE_BOOM, Command.USE_C190, Command.USE_GEOPACK,
                  Command.USE_NANOBOT, Command.USE_POLIMER, Command.USE_PROTON,
                  Command.USE_RAZRYAD, Command.USE_REMBOT, Command.USE_ZZ}

Command.Q = (Command.RETURN, Command.RETURN_ARGUMENT, Command.RETURN_STATE)
Command.W = (Command.MOVE_TOP, Command.DIR_TOP, Command.DIR_INV_TOP)
Command.A = (Command.MOVE_LEFT, Command.DIR_LEFT, Command.DIR_INV_LEFT)
Command.S = (Command.MOVE_BOTTOM, Command.DIR_BOTTOM, Command.DIR_INV_BOTTOM)
Command.D = (Command.MOVE_RIGHT, Command.DIR_RIGHT, Command.DIR_INV_RIGHT)
Command.SHIFT_W = (Command.CHECK_TOP, Command.OFFSET_TOP)
Command.SHIFT_A = (Command.CHECK_LEFT, Command.OFFSET_LEFT)
Command.SHIFT_S = (Command.CHECK_BOTTOM, Command.OFFSET_BOTTOM)
Command.SHIFT_D = (Command.CHECK_RIGHT, Command.OFFSET_RIGHT)
# для определения диагональных
Command.CHECK_ORTO = (Command.CHECK_TOP, Command.CHECK_LEFT, Command.CHECK_BOTTOM, Command.CHECK_RIGHT)
# Словарь для маппинга направлений в диагональные
Command.CHECK_DIAGONAL = {
    # (направление1, направление2): диагональное направление
    (Command.CHECK_TOP, Command.CHECK_LEFT): Command.CHECK_TOP_LEFT,
    (Command.CHECK_TOP, Command.CHECK_RIGHT): Command.CHECK_TOP_RIGHT,
    (Command.CHECK_BOTTOM, Command.CHECK_LEFT): Command.CHECK_BOTTOM_LEFT,
    (Command.CHECK_BOTTOM, Command.CHECK_RIGHT): Command.CHECK_BOTTOM_RIGHT,
    
    # Также учтем обратный порядок
    (Command.CHECK_LEFT, Command.CHECK_TOP): Command.CHECK_TOP_LEFT,
    (Command.CHECK_RIGHT, Command.CHECK_TOP): Command.CHECK_TOP_RIGHT,
    (Command.CHECK_LEFT, Command.CHECK_BOTTOM): Command.CHECK_BOTTOM_LEFT,
    (Command.CHECK_RIGHT, Command.CHECK_BOTTOM): Command.CHECK_BOTTOM_RIGHT,
}
Command.E = {Command.START, Command.STOP, Command.RESPAWN_TO}
Command.R = {Command.ROTATE_LEFT, Command.ROTATE_RIGHT, Command.DIR_RANDOM}
Command.T = {Command.STD_DIG, Command.STD_BUILD, Command.STD_HEAL, Command.STD_DIG_AROUND}
Command.Y = {Command.FLIP}
Command.I = {Command.YES_NO, Command.NO_YES}
Command.O = {Command.OR, Command.AND}
Command.F = {Command.MOVE_FORWARD}
Command.SHIFT_F = {Command.CHECK_FORWARD, Command.OFFSET_FORWARD, Command.CHECK_LEFT_HAND, Command.CHECK_RIGHT_HAND}
Command.G = {Command.GO_TO, Command.CALL_FUNC, Command.CALL_FUNC_CONDITION, Command.CALL_FUNC_STATE}
Command.H = {Command.IS_HP_LESS_100, Command.IS_HP_LESS_50}
Command.J = {Command.IS_IN_GUN, Command.AMMO}
Command.L = {Command.LABEL}
Command.Z = {Command.DIG, Command.BUILD_BLOCK, Command.GEO, Command.BUILD_ROAD, Command.HEAL, Command.BUILD_QUADRO}
Command.SHIFT_Z = {Command.BUILD_WB, Command.USE_BOOM, Command.USE_PROTON, Command.USE_RAZRYAD}
Command.X = {Command.USE_GEOPACK, Command.USE_ZZ, Command.USE_POLIMER, Command.USE_C190}
Command.SHIFT_X = {Command.CRAFT, Command.UP, Command.USE_NANOBOT, Command.USE_REMBOT}
Command.C = {Command.IS_NOT_EMPTY, Command.IS_EMPTY, Command.IS_FALLING, Command.IS_CRYSTAL, Command.IS_ALIVE_CRYSTAL, 
             Command.IS_FALLING_GRAVEL, Command.IS_FALLING_SAND, Command.IS_BREAKABLE, Command.IS_UNBREAKABLE, Command.IS_SLIME}
Command.SHIFT_C = {Command.IS_CHERNOSKAL, Command.IS_KRASNOSKAL, Command.IS_GREEN_BLOCK, Command.IS_YELLOW_BLOCK, Command.IS_RED_BLOCK,
                   Command.IS_OPORA, Command.IS_QUADRO, Command.IS_ROAD, Command.IS_BOX}
Command.V = {Command.VAR_EQUAL, Command.VAR_LESS, Command.VAR_GREATER}
Command.B = {Command.ALARM, Command.I_DONT_KNOW4, Command.I_DONT_KNOW5}
Command.SHIFT_B = {Command.MODE_MANUAL, Command.MODE_AUTO}
Command.M = {Command.AUTO_DIG_ON, Command.AUTO_DIG_OFF, Command.AGR_ON, Command.AGR_OFF}
Command.BACKSPACE = {Command.NEWLINE, Command.EMPTY}

Command.CONDITION = {}

if __name__ == "__main__":

    print(Command.CHECK_ORTO.index(Command.CHECK_LEFT_HAND))

    # Проверка
    print(f"TWO_ARGS: {sorted([c.name for c in Command.TWO_ARGS])}")