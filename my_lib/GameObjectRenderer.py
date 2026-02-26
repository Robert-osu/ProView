
from abc import ABC, abstractmethod
import uuid

class GameObjectInterface(ABC):
    @abstractmethod
    def _execute(self):
        pass

    @abstractmethod
    def _update(self):
        pass

    @abstractmethod
    def _draw(self):
        pass

class GameObject(GameObjectInterface):
    def __init__(self, z_order=0):
        self.id = uuid.uuid4() # Уникальный идентификатор
        self.z_order = z_order
        self.manager = None # Будет установлен при добавлении в менеджер

    def _execute(self):
        pass

    def _update(self):
        pass

    def _draw(self):
        pass

    def set_manager(self, manager):
        self.manager = manager

class GameObjectManager(GameObjectInterface):
    """
    Менеджер отрисовки игровых объектов - управляет коллекцией игровых объектов, 
    сортирует их по приоритету и выполняет основной игровой цикл (логика → обновление → отрисовка).
    Composite
    """
    def __init__(self):
        self.elements = {}
        self.sorted_list = []

    def add(self, element: GameObjectInterface, z_order):
        self.elements[element.id] = (z_order, element)
        self._sort()

    def delete(self, id):
        if id in self.elements.keys():
            del self.elements[id]
            self._sort()

    def run(self):
        self._execute()
        self._update()
        self._draw()

    def _sort(self):
        self.sorted_list = [element for _, element in sorted(self.elements.values(), key=lambda x: x[0])]

    def _execute(self):
        for object in self.sorted_list:
            object._execute()

    def _update(self):
        for object in self.sorted_list:
            object._update()

    def _draw(self):
        for object in self.sorted_list:
            object._draw()

