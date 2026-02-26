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
            self.changed = False  # изменений не было


if __name__ == "__main__":
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