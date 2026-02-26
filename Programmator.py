"""
Модуль для работы с закодированными данными программы.
Предоставляет функциональность декодирования, модификации и кодирования данных.
"""

import base64
import lzma
from typing import List, Union

from Command import Command
from ProgrammatorViewer import ProgrammatorViewer


class ValueTuple():
    first: str
    second: str
    
    def __new__(cls, first='0', second='0') -> tuple:
        """Возвращает tuple сразу при создании"""
        first = str(first)
        second = str(second)

        first = first[:3]
        second = second[:3]
        return (first, second)


class Programmator:
    """
    Класс для работы с закодированными данными программы.
    
    Формат данных:
    - Первые 4 байта: размер данных (little-endian)
    - Далее: команды (size_data байт)
    - Остальное: значения, разделенные ':' и '@'
    """
    
    SIZE_BYTES = 4

    def __init__(self, size = 16 * 12 * 16):
        self._commands = [Command.EMPTY] * size
        self._values = [['0'] for _ in range(size)]
        self.size = size

        self.addCommand(size - 1, Command.MULTIPLY_VALUE)
        self._modifyData()

        args_1 = list(Command.ONE_ARGS)
        args_2 = list(Command.TWO_ARGS)
        args_0 = list(Command.NO_ARGS)
        list_cmd = list(Command)

        # self.addCommand(1, list_cmd[2])
        # self.addValue(1, ValueTuple('10', 'a'))

        # self.addCommand(2, Command.SET_VALUE)
        # self.addValue(2, ValueTuple('A', '1'))

        # self.addCommand(3, list_cmd[99])
        # self.addValue(3, ValueTuple('B', '21'))

        # self.addCommand(4, list_cmd[98])
        # self.addValue(4, ValueTuple('B'))

        # self.addCommand(5, list_cmd[97])
        # self.addValue(5, ValueTuple('A'))

        # self.addCommand(6, list_cmd[120])
        # self.addValue(6, ValueTuple('C', '5'))

        # # self.addCommand(7, list_cmd[113])
        # # self.addValue(7, ValueTuple('C', '5'))

        # self.addCommand(8, list_cmd[139])
        # self.addValue(8, ValueTuple('C', '5'))

        # self.addCommand(9, list_cmd[23])
        # self.addValue(9, ValueTuple('C', '5'))
        #self._values[120] = ['1', '1']
        



    def copy(self, code: str):
        """
        Копирвоание программы.
        
        Args:
            code: base64 строка с LZMA сжатыми данными
        """
        data = self._decode(code)
        mod_data = bytearray(data)
        
        """Парсит данные на составные части."""
        bsize = Programmator.SIZE_BYTES
        
        self.size = int.from_bytes(mod_data[:bsize], 'little')

        list_commands = list(Command)
        self._commands = []
        for byte in mod_data[bsize:(self.size + bsize)]:
            self._commands.append(list_commands[int(byte)])


        self._values = self._parseValues(mod_data[self.size + bsize:])

    def addCommand(self, index, cmd: Command):
        if index >= 0 and index < self.size:
            self._commands[index] = cmd
            if cmd in Command.TWO_ARGS:
                # Добавляем только если нужно дополнить до 2 элементов
                current = self._values[index]
                needed = 2 - len(current)
                if needed > 0:
                    current.extend(['0'] * needed)  # получится ['3', '0'] или ['4', '5']
                    self._values[index] = current

    def addValue(self, index, value_tuple: ValueTuple):
        if index > 0 and index < self.size:
            if self._commands[index] in Command.NO_ARGS:
                return
            elif self._commands[index] in Command.ONE_ARGS:
                self._values[index][0] = value_tuple[0]
            elif self._commands[index] in Command.TWO_ARGS:
                #print(value_tuple)
                self._values[index][0], self._values[index][1] = value_tuple
                #print(self._values[index])

    def getCommands(self):
        return self._commands
        
    def getEncode(self) -> str:
        """
        Получить закодированную строку после модификаций.
        
        Returns:
            base64 строка с LZMA сжатыми данными
        """
        return self._encode()
    
    def _decode(self, code: str) -> bytes:
        """
        Декодирует base64 строку и распаковывает LZMA.
        
        Args:
            code: base64 строка для декодирования
            
        Returns:
            Распакованные данные
        """
        decoded_bytes = base64.b64decode(code)
        decompressed_data = lzma.decompress(decoded_bytes)
        print("Decompressed data:", decompressed_data)
        return decompressed_data
    
    def _modifyData(self) -> None:
        """
        Модифицирует данные (примеры изменений).
        Можно переопределить в наследнике для конкретных изменений.
        """
        # Пример изменения первого байта команд
        commands_list = list(Command)
        for i in range(0, 16 + 16 * 16):
            if i < len(commands_list):
                self.addCommand(i, commands_list[i])

    def _encode(self) -> str:
        """
        Кодирует данные обратно в base64 с LZMA сжатием.
        
        Returns:
            base64 строка
        """
        if self._getSizeData() == 0:
            return 0
        compressed_again = lzma.compress(
            bytes(self._compareBytes()),
            format=lzma.FORMAT_ALONE,
            check=-1,
            preset=0
        )
        
        encoded_again = base64.b64encode(compressed_again).decode('utf-8')
        print("New base64 string:", encoded_again)
        return encoded_again
    
    def _parseValues(self, byte_data: bytes) -> List[List[str]]:
        """
        Парсит значения из байтового представления.
        
        Args:
            byte_data: байтовые данные для парсинга
            
        Returns:
            Список списков строковых значений
        """
        data_str = byte_data.decode('utf-8')
        parts = data_str.split(':')
        
        result = []
        for part in parts:
            if '@' in part:
                values = part.split('@')
                result.append(values)
            else:
                result.append([part])
        
        return result
    
    def _serializeValues(self) -> bytearray:
        """
        Сериализует значения обратно в байтовое представление.
        
        Returns:
            Байтовое представление значений
        """
        parts = []
        for item in self._values:
            if len(item) > 1:
                part = '@'.join(item)
            else:
                part = item[0]
            parts.append(part)
        
        result_str = ':'.join(parts)
        return bytearray(result_str, 'utf-8')
    
    def _getSizeData(self) -> bytes:
        """
        Изменяет размер данных в соответствии с текущими командами.
        
        Returns:
            Байтовое представление размера (4 байта, little-endian)
        """
        return len(self._commands).to_bytes(Programmator.SIZE_BYTES, 'little')
    
    def _compareBytes(self) -> bytearray:
        """
        Собирает все части данных в единый массив байт.
        
        Returns:
            Полный массив байт данных
        """
        size_bytes = self._getSizeData()
        values_bytes = self._serializeValues()
        commands_bytes = bytearray(cmd.value[0] for cmd in self._commands)

        
        result = bytearray(b''.join([size_bytes, commands_bytes, values_bytes]))
        print(result)
        return result
    


def main() -> None:
    """Основная функция для демонстрации работы класса."""
    # Ваша зашифрованная строка в base64
    encoded_string = "XQAAgACzAAAAAAAAAAAZADAMYCDURSxK8GR5e/2nd+V9B2fs+9LemstWZRQBmMQiE4IOuXqySGdcZtrDkPe00KEs+KiBkaH1Dx0a4GlBU6a90Uy5qp5AHk4BJ9dul//0RfUyVcEDj28w/394ryD97MbhFAMFuVwQPzKLgA=="
    #encoded_str2 = "XQAAgACFAAAAAAAAAAARgDAMRhMdUereBiFWGkQyKQPZJs2tNUW3voIoB50brWMaGrpr5pUS/JTgZoWZccIHKQX5PJLXzw6hbx7gzQZLXhJafLQmEENkd4cQN/x+H//nchAA"

    program = Programmator()
    #program.copy(encoded_str2)
    #program._values[8] = ['A', '1']
    #print(program._values[0], program._values[8])
    encoded_again = program.getEncode()


if __name__ == "__main__":
    main()