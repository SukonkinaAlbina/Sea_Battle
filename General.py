import pygame
from random import randint, choice, sample
import sys
import numpy as np

pygame.init()


class Ship:
    def __init__(self, length, tp=1, x=None, y=None):
        self.length = length
        self.tp = tp
        self.x = x
        self.y = y
        self.ship_x, self.ship_y = [0] * length, [0] * length
        self.cells = [1] * length

    def set_start_coords(self, x, y):
        self.x = x
        self.y = y
        self.set_coords()

    def set_coords(self):
        for i in range(self.length):
            if self.tp == 1:
                self.ship_x[i] = self.x + i
                self.ship_y[i] = self.y
            else:
                self.ship_x[i] = self.x
                self.ship_y[i] = self.y + i

    def generate_coords(self, available):
        y, x = choice(list(available))
        self.set_start_coords(x, y)
        while any([x < 0 or x > 9 for x in self.ship_x]) or \
                any([x < 0 or x > 9 for x in self.ship_y]):
            self.generate_coords(available)


class GamePole:
    pole_settings = {
        'SIZE_BLOCK': 30,
        'FRAME_COLOR': (0, 0, 0),
        'LEFT_POLE_COLOR': (175, 238, 238),
        'RIGHT_POLE_COLOR': (112, 128, 144),
        'HEADER_COLOR': (0, 206, 209),
        'HEADER_MARGIN': 20,
        'COUNT_BLOCKS': 10,
        'MARGIN': 1,
        'SHIP_COLORS': {
            4: (0, 102, 0),
            3: (154, 205, 50),
            2: (255, 69, 0),
            1: (75, 0, 130)
        }
    }
    SPACE_BETWEEN = 2 * pole_settings['SIZE_BLOCK']
    _size = [2 * (pole_settings['SIZE_BLOCK'] * pole_settings['COUNT_BLOCKS'] + pole_settings['MARGIN'] * pole_settings[
        'COUNT_BLOCKS']) + SPACE_BETWEEN,
             pole_settings['SIZE_BLOCK'] * pole_settings['COUNT_BLOCKS'] + pole_settings['MARGIN'] * pole_settings[
                 'COUNT_BLOCKS'] + pole_settings['HEADER_MARGIN']]
    _ships = []
    screen = pygame.display.set_mode(_size)
    pygame.display.set_caption('Морской бой')
    timer = pygame.time.Clock()
    courier = pygame.font.SysFont('courier', 36)

    def __init__(self):
        self._ships = [Ship(4, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)),
                       Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2))]
        self._cells = np.zeros((self.pole_settings['COUNT_BLOCKS'], self.pole_settings['COUNT_BLOCKS']))
        self._available = set([(x, y) for x in range(self.pole_settings['COUNT_BLOCKS']) for y in
                               range(self.pole_settings['COUNT_BLOCKS'])])

    def generate_coords(self, ship, available):
        ship.generate_coords(available)
        if ship.tp == 1:
            while any(self._cells[ship.y, ship.x:ship.x + ship.length]):
                self.generate_coords(ship, available)
        else:
            while any(self._cells[ship.y:ship.y + ship.length, ship.x]):
                self.generate_coords(ship, available)

    def arrange_the_ships(self):
        available = self._available
        for ship in self._ships:
            self.generate_coords(ship, available)
            if ship.tp == 1:
                self._cells[ship.y, ship.x:ship.x + ship.length] = np.where(self._cells[ship.y,
                                                                            ship.x:ship.x + ship.length] == 0, 1, 0)
            else:
                self._cells[ship.y:ship.y + ship.length, ship.x] = np.where(self._cells[ship.y:ship.y + ship.length,
                                                                            ship.x] == 0, 1, 0)
            available = self.update_available_block(ship)
        return self._cells

    def update_available_block(self, ship):
        for x, y in zip(ship.ship_x, ship.ship_y):
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 <= x + k < 10 and 0 <= y + m < 10:
                        if self._cells[y + m][x + k] != 1 and self._cells[y + m][x + k] != 0.2:
                            self._cells[y + m][x + k] = 0.2
                        self._available.discard((y + m, x + k))
        return self._available

    def show(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('exit')
                    pygame.quit()
                    sys.exit()
            self.screen.fill(self.pole_settings['FRAME_COLOR'])
            pygame.draw.rect(self.screen, self.pole_settings['HEADER_COLOR'],
                             [0, 0, (self._size[0] - self.SPACE_BETWEEN) / 2, self.pole_settings['HEADER_MARGIN']])
            pygame.draw.rect(self.screen, self.pole_settings['HEADER_COLOR'],
                             [self.pole_settings['SIZE_BLOCK'] * self.pole_settings['COUNT_BLOCKS'] +
                              self.pole_settings['MARGIN'] * (self.pole_settings['COUNT_BLOCKS'] + 2) +
                              self.SPACE_BETWEEN, 0, (self._size[0] - self.SPACE_BETWEEN) / 2,
                              self.pole_settings['HEADER_MARGIN']])
            for row in range(self.pole_settings['COUNT_BLOCKS']):
                for column in range(self.pole_settings['COUNT_BLOCKS']):
                    self.draw_block(self.pole_settings['LEFT_POLE_COLOR'], row, column)
                    self.draw_block(self.pole_settings['RIGHT_POLE_COLOR'], row,
                                    column + self.pole_settings['COUNT_BLOCKS'] + 2)
            for ship in self._ships:
                for coord_1, coord_2 in zip(ship.ship_x, ship.ship_y):
                    self.draw_block(self.pole_settings['SHIP_COLORS'][ship.length], coord_1, coord_2)
            pygame.display.flip()

    def draw_block(self, color, row, column):
        pygame.draw.rect(self.screen, color,
                         [column * self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN'] * (column + 1),
                          self.pole_settings['HEADER_MARGIN'] + row * self.pole_settings['SIZE_BLOCK']
                          + self.pole_settings['MARGIN'] * (row + 1), self.pole_settings['SIZE_BLOCK'],
                          self.pole_settings['SIZE_BLOCK']])



