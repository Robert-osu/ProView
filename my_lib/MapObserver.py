from abc import ABC, abstractmethod
from typing import Protocol, Dict, Tuple, Optional
import numpy as np

class Observer(ABC):
    @abstractmethod
    def on_object_created(self, obj, coord):
        """Вызывается при создании объекта"""
        pass

    @abstractmethod
    def on_object_moved(self, obj, old_coord, new_coord):
        """Вызывается при перемещении объекта"""
        pass

    @abstractmethod
    def on_object_removed(self, obj, coord):
        """Вызывается при удалении объекта"""
        pass

class GameObject:
    def __init__(self, game_object_id: int, initial_coord: tuple):
        self.id = game_object_id
        self.coord = initial_coord
        self._observers = []
    
    def add_map_observer(self, observer: Observer):
        self._observers.append(observer)
    
    def move_to(self, new_coord: tuple):
        old_coord = self.coord
        self.coord = new_coord
        self._notify_moved(old_coord, new_coord)
    
    def remove(self):
        self._notify_removed()
    
    def _notify_created(self):
        for observer in self._observers:
            observer.on_object_created(self, self.coord)
    
    def _notify_moved(self, old_coord: tuple, new_coord: tuple):
        for observer in self._observers:
            observer.on_object_moved(self, old_coord, new_coord)
    
    def _notify_removed(self):
        for observer in self._observers:
            observer.on_object_removed(self, self.coord)

class GameMap(Observer):
    def __init__(self, size: tuple):
        # Словарь для хранения объектов по координатам
        self._objects_by_coord: Dict[Tuple, list] = {}
        # Словарь для быстрого поиска объекта по ID
        self._objects_by_id: Dict[int, GameObject] = {}
    
    def on_object_created(self, obj: GameObject, coord: Tuple):
        """Вызывается при создании объекта"""
        print(f"Объект {obj.id} создан на координатах {coord}")
        
        # Добавляем объект в словарь по координатам
        if coord not in self._objects_by_coord:
            self._objects_by_coord[coord] = []
        self._objects_by_coord[coord].append(obj)
        
        # Добавляем объект в словарь по ID
        self._objects_by_id[obj.id] = obj
    
    def on_object_moved(self, obj: GameObject, old_coord: Tuple, new_coord: Tuple):
        """Вызывается при перемещении объекта"""
        print(f"Объект {obj.id} перемещен с {old_coord} на {new_coord}")
        
        # Удаляем объект из старой координаты
        if old_coord in self._objects_by_coord and obj in self._objects_by_coord[old_coord]:
            self._objects_by_coord[old_coord].remove(obj)
            # Если список пуст, удаляем координату
            if not self._objects_by_coord[old_coord]:
                del self._objects_by_coord[old_coord]
        
        # Добавляем объект в новую координату
        if new_coord not in self._objects_by_coord:
            self._objects_by_coord[new_coord] = []
        self._objects_by_coord[new_coord].append(obj)
    
    def on_object_removed(self, obj: GameObject, coord: Tuple):
        """Вызывается при удалении объекта"""
        print(f"Объект {obj.id} удален с координат {coord}")
        
        # Удаляем объект из словаря по координатам
        if coord in self._objects_by_coord and obj in self._objects_by_coord[coord]:
            self._objects_by_coord[coord].remove(obj)
            # Если список пуст, удаляем координату
            if not self._objects_by_coord[coord]:
                del self._objects_by_coord[coord]
        
        # Удаляем объект из словаря по ID
        if obj.id in self._objects_by_id:
            del self._objects_by_id[obj.id]
    
    def get_objects_at_coord(self, coord: Tuple) -> list:
        """Возвращает все объекты на указанных координатах"""
        return self._objects_by_coord.get(coord, [])
    
    def get_object_by_id(self, obj_id: str) -> Optional[GameObject]:
        """Возвращает объект по его ID"""
        return self._objects_by_id.get(obj_id)
    
    def get_all_coords_with_objects(self) -> list:
        """Возвращает все координаты, на которых есть объекты"""
        return list(self._objects_by_coord.keys())
    
    def get_all_objects(self) -> list:
        """Возвращает все объекты на карте"""
        return list(self._objects_by_id.values())
    
    def print_map_state(self):
        """Выводит текущее состояние карты"""
        print("\n=== ТЕКУЩЕЕ СОСТОЯНИЕ КАРТЫ ===")
        for coord, objects in self._objects_by_coord.items():
            obj_ids = [obj.id for obj in objects]
            print(f"Координаты {coord}: {obj_ids}")
        print("===============================\n")