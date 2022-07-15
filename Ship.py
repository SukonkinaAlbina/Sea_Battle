from random import choice


class Ship:
    def __init__(self, length, tp=1, x=None, y=None):
        self.length = length  # длина корабля
        self.tp = tp  # ориентация корабля (1 - горизонтальная, 2 - вертикальная)
        self.x = x  # координаты первой палубы корабля
        self.y = y
        self.ship_x, self.ship_y = [0] * length, [0] * length  # координаты всего корабля
        self.cells = [length] * length  # ячейки для корабля

    def set_start_coords(self, x, y):  # задаёт начальные координаты
        self.x = x
        self.y = y
        self.set_coords()

    def set_coords(self):  # задаёт координаты всего корабля
        for i in range(self.length):
            if self.tp == 1:
                self.ship_x[i] = self.x + i
                self.ship_y[i] = self.y
            else:
                self.ship_x[i] = self.x
                self.ship_y[i] = self.y + i

    def generate_coords(self,
                        available):  # случайно генерирует начальные координаты корабля из оставшихся свободных клеток
        y, x = choice(list(available))
        self.set_start_coords(x, y)
        while any([x < 0 or x > 9 for x in self.ship_x]) or \
                any([x < 0 or x > 9 for x in self.ship_y]):
            self.generate_coords(available)
