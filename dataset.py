from enum import Enum

class Dictionary(Enum):
    NAME = "Программатор"
    DEFINITION = "Система автоматизации на базе скриптов."
    DESCRIPTION = "Позволяет последовательно собирать картинки-операторы в готовую программу для автоматизации вашего робота."

    # помощь по операторам
    EMPTY = "пустой оператор"
    NEWLINE = "учитывать следующую строку"
    START = "точка старта"
    STOP = "прервать программу"
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