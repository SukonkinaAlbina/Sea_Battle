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
        'FRAME_COLOR': (255, 255, 255),
        'LEFT_POLE_COLOR': (175, 238, 238),
        'RIGHT_POLE_COLOR': (112, 128, 144),
        'HEADER_COLOR': (0, 206, 209),
        'HEADER_MARGIN': 70,
        'LEFT_MARGIN': 20,
        'BOTTOM_MARGIN': 70,
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
    _size = [2 * (pole_settings['LEFT_MARGIN'] + pole_settings['SIZE_BLOCK'] * pole_settings['COUNT_BLOCKS'] +
                  pole_settings['MARGIN'] * pole_settings['COUNT_BLOCKS']) + SPACE_BETWEEN,
             pole_settings['SIZE_BLOCK'] * pole_settings['COUNT_BLOCKS'] + pole_settings['MARGIN'] * pole_settings[
                 'COUNT_BLOCKS'] + pole_settings['HEADER_MARGIN'] + pole_settings['BOTTOM_MARGIN']]
    _ships = []
    screen = pygame.display.set_mode(_size)
    pygame.display.set_caption('Морской бой')
    timer = pygame.time.Clock()
    courier = pygame.font.SysFont('courier', 20)
    font = pygame.font.SysFont('notosans', int(pole_settings['SIZE_BLOCK'] // 1.5))

    def __init__(self):
        self._ships = [Ship(4, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)),
                       Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2))]
        self._cells = np.zeros((self.pole_settings['COUNT_BLOCKS'], self.pole_settings['COUNT_BLOCKS']))
        self._available = set([(x, y) for x in range(self.pole_settings['COUNT_BLOCKS']) for y in
                               range(self.pole_settings['COUNT_BLOCKS'])])
        self.pl_rect_x = self.pole_settings['LEFT_MARGIN']
        self.com_rect_x = self.pl_rect_x + self.pole_settings['SIZE_BLOCK'] * self.pole_settings['COUNT_BLOCKS'] + \
                          self.pole_settings['MARGIN'] * (self.pole_settings['COUNT_BLOCKS'] + 2) + self.SPACE_BETWEEN
        self.pole_width = (self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']) * self.pole_settings[
            'COUNT_BLOCKS']

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

    def draw_hit(self, block):
        x = self.com_rect_x + block[0] * (self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN'])
        y = self.pole_settings['HEADER_MARGIN'] + block[1] * (
                    self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN'])
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x + self.pole_settings['SIZE_BLOCK'],
                                                          y + self.pole_settings['SIZE_BLOCK']),
                         self.pole_settings['SIZE_BLOCK'] // 6)
        pygame.draw.line(self.screen, (0, 0, 0), (x, y + self.pole_settings['SIZE_BLOCK']),
                         (x + self.pole_settings['SIZE_BLOCK'], y),
                         self.pole_settings['SIZE_BLOCK'] // 6)
        #print((x + self.pole_settings['SIZE_BLOCK'], y + self.pole_settings['SIZE_BLOCK']))
        # pygame.display.flip()

    def draw_fail(self, block):
        x = self.com_rect_x + block[0] * (self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']) + self.pole_settings['SIZE_BLOCK']//2
        y = self.pole_settings['HEADER_MARGIN'] + block[1] * (
                self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']) + self.pole_settings['SIZE_BLOCK']//2
        pygame.draw.circle(self.screen, (0,0,0), (x, y), self.pole_settings['SIZE_BLOCK'] // 6)

    def draw_grid(self):
        self.screen.fill(self.pole_settings['FRAME_COLOR'])
        for x in [self.pl_rect_x, self.com_rect_x]:
            pygame.draw.rect(self.screen, self.pole_settings['HEADER_COLOR'],
                             [x, 0, self.pole_width, self.pole_settings['HEADER_MARGIN']])
        btn_1 = Button(self.pole_settings['LEFT_MARGIN'], self.pole_settings['HEADER_MARGIN'] +
                       (self._size[0] - self.SPACE_BETWEEN - 2 * self.pole_settings['LEFT_MARGIN']) / 2,
                       5 * (self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']), 40, 'Новое поле')
        btn_1.draw_button(self, self.courier, (0, 130, 234), (255, 255, 255))
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for row in range(self.pole_settings['COUNT_BLOCKS']):
            for column in range(self.pole_settings['COUNT_BLOCKS']):
                self.draw_block(self.pole_settings['LEFT_POLE_COLOR'], row, column)
                self.draw_block(self.pole_settings['RIGHT_POLE_COLOR'], row, column, 'computer')
                if row < 10:
                    num_ver = self.font.render(str(row + 1), True, (0, 0, 0))
                    letters_hor = self.font.render(letters[row], True, (0, 0, 0))
                    num_ver_height = num_ver.get_height()
                    letters_hor_width = letters_hor.get_width()
                    for x in [self.pl_rect_x, self.com_rect_x]:
                        self.screen.blit(num_ver, (x - (self.pole_settings['SIZE_BLOCK'] // 2),
                                                   self.pole_settings['HEADER_MARGIN'] + row * (
                                                           self.pole_settings['SIZE_BLOCK'] + self.pole_settings[
                                                       'MARGIN']) +
                                                   (self.pole_settings['SIZE_BLOCK'] // 2 - num_ver_height // 2)))
                        self.screen.blit(letters_hor,
                                         (x + row * (self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']) +
                                          (self.pole_settings['SIZE_BLOCK'] // 2 + self.pole_settings[
                                              'MARGIN'] // 2 - letters_hor_width // 2),
                                          self.pole_settings['HEADER_MARGIN'] - self.pole_settings['SIZE_BLOCK'] // 2))
        return btn_1

    def draw_ships(self, name='player'):
        for ship in self._ships:
            for coord_1, coord_2 in zip(ship.ship_x, ship.ship_y):
                self.draw_block(self.pole_settings['SHIP_COLORS'][ship.length], coord_2, coord_1, name)

    def show(self):
        BLOCK = (0, 0)
        computer_turn = False
        btn_1 = self.draw_grid()
        pole_2 = GamePole()
        comp_ships = pole_2.arrange_the_ships()
        self.draw_ships()
        #pole_2.draw_ships('computer')
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('exit')
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and btn_1.rect_button.collidepoint(pygame.mouse.get_pos()):
                    new_pole = GamePole()
                    new_pole.arrange_the_ships()
                    new_pole.show()
                elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if self.com_rect_x <= x <= self.com_rect_x + self.pole_width \
                            and self.pole_settings['HEADER_MARGIN'] <= \
                            y <= self.pole_settings['HEADER_MARGIN'] + self.pole_width:
                        block = (
                        (x - self.com_rect_x) // (self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']),
                        (y - self.pole_settings['HEADER_MARGIN']) // (
                                    self.pole_settings['SIZE_BLOCK'] + self.pole_settings['MARGIN']))
                        if comp_ships[block[1], block[0]] == 1:
                            self.draw_hit(block)
                        else:
                            self.draw_fail(block)
                pygame.display.update()

    def draw_block(self, color, row, column, name='player'):
        if name != 'player':
            x = self.com_rect_x
        else:
            x = self.pl_rect_x
        pygame.draw.rect(self.screen, color,
                         [x + column * self.pole_settings['SIZE_BLOCK'] +
                          self.pole_settings['MARGIN'] * (column + 1),
                          self.pole_settings['HEADER_MARGIN'] + row * self.pole_settings['SIZE_BLOCK']
                          + self.pole_settings['MARGIN'] * (row + 1), self.pole_settings['SIZE_BLOCK'],
                          self.pole_settings['SIZE_BLOCK']])


class Button:
    def __init__(self, x, y, width, height, text):
        self.size = (width, height)
        self.text = text  # Текст кнопки
        self.x = x  # Позиция х кнопки
        self.y = y  # Позиция у кнопки
        self.rect_button = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def draw_button(self, pole, font, btn_color, text_color):
        pygame.draw.rect(pole.screen, btn_color, self.rect_button)
        text_to_blit = font.render(self.text, True, text_color)
        pole.screen.blit(text_to_blit, (self.rect_button.centerx - 2 * pole.pole_settings['SIZE_BLOCK'],
                                        self.rect_button.centery - 14))


pole_player = GamePole()
p_1 = pole_player.arrange_the_ships()
pole_computer = GamePole()
p_2 = pole_computer.arrange_the_ships()
pole_player.show()
