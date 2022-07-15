from Settings import pole_settings
from random import randint, choice
import pygame
from Ship import Ship
import numpy as np


class GamePole:
    SPACE_BETWEEN = 2 * pole_settings['SIZE_BLOCK']  # расстояние между полями
    POLE_SIZE = (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) * pole_settings[
        'COUNT_BLOCKS']  # размер одного поля
    size = [2 * (pole_settings['LEFT_MARGIN'] + POLE_SIZE) + SPACE_BETWEEN,
            POLE_SIZE + pole_settings['HEADER_MARGIN'] + pole_settings['BOTTOM_MARGIN']]  # размер всего игрового поля
    _ships = []  # список кораблей
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Морской бой')
    timer = pygame.time.Clock()

    def __init__(self):
        #  список кораблей
        self._ships = [Ship(4, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)),
                       Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2))]
        self._cells = np.zeros((pole_settings['COUNT_BLOCKS'], pole_settings['COUNT_BLOCKS']))
        self._available = set([(x, y) for x in range(pole_settings['COUNT_BLOCKS']) for y in
                               range(pole_settings['COUNT_BLOCKS'])])
        self.pl_rect_x = pole_settings['LEFT_MARGIN']
        self.com_rect_x = self.pl_rect_x + self.POLE_SIZE + 2 * pole_settings['MARGIN'] + self.SPACE_BETWEEN

    def generate_coords(self, ship,
                        available):  # случайно генерирует начальные координаты корабля из оставшихся свободных клеток
        ship.generate_coords(available)
        if ship.tp == 1:
            while any(self._cells[ship.y, ship.x:ship.x + ship.length]):
                self.generate_coords(ship, available)
        else:
            while any(self._cells[ship.y:ship.y + ship.length, ship.x]):
                self.generate_coords(ship, available)

    def arrange_the_ships(self):  # расставляет корабли на поле
        available = self._available
        for ship in self._ships:
            self.generate_coords(ship, available)
            if ship.tp == 1:
                self._cells[ship.y, ship.x:ship.x + ship.length] = np.where(self._cells[ship.y,
                                                                            ship.x:ship.x + ship.length] == 0,
                                                                            ship.length, 0)
            else:
                self._cells[ship.y:ship.y + ship.length, ship.x] = np.where(self._cells[ship.y:ship.y + ship.length,
                                                                            ship.x] == 0, ship.length, 0)
            available = self.update_available_block(ship)
        return self._cells

    def update_available_block(self, ship):  # обновляет список свободных клеток
        for x, y in zip(ship.ship_x, ship.ship_y):
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 <= x + k < 10 and 0 <= y + m < 10:
                        if self._cells[y + m][x + k] not in [1, 2, 3, 4] and self._cells[y + m][x + k] != 0.1:
                            self._cells[y + m][x + k] = 0.1
                        self._available.discard((y + m, x + k))
        return self._available

    def draw_block(self, color, row, column, player='player'):  # рисует блок
        if player != 'player':
            x = self.com_rect_x
        else:
            x = self.pl_rect_x
        pygame.draw.rect(self.screen, color,
                         [x + column * pole_settings['SIZE_BLOCK'] +
                          pole_settings['MARGIN'] * (column + 1),
                          pole_settings['HEADER_MARGIN'] + row * pole_settings['SIZE_BLOCK']
                          + pole_settings['MARGIN'] * (row + 1), pole_settings['SIZE_BLOCK'],
                          pole_settings['SIZE_BLOCK']])

    def draw_hit(self, block, opponent='player'):  # рисует крест, если корабль был поражён
        if opponent != 'player':
            x_0 = self.com_rect_x
        else:
            x_0 = self.pl_rect_x
        x = x_0 + block[0] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) + 2 * pole_settings['MARGIN']
        y = pole_settings['HEADER_MARGIN'] + \
            block[1] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) + 2 * pole_settings['MARGIN']
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x + pole_settings['SIZE_BLOCK'] - 3 * pole_settings['MARGIN'],
                                                          y + pole_settings['SIZE_BLOCK'] - 3 * pole_settings[
                                                              'MARGIN']),
                         pole_settings['SIZE_BLOCK'] // 6)
        pygame.draw.line(self.screen, (0, 0, 0), (x, y + pole_settings['SIZE_BLOCK'] - 3 * pole_settings['MARGIN']),
                         (x + pole_settings['SIZE_BLOCK'] - 3 * pole_settings['MARGIN'], y),
                         pole_settings['SIZE_BLOCK'] // 6)

    def draw_fail(self, block, opponent='player'):  # рисует точку, если удар был нанесён мимо цели
        if opponent != 'player':
            x_0 = self.com_rect_x
        else:
            x_0 = self.pl_rect_x
        x = x_0 + block[0] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) + \
            pole_settings['SIZE_BLOCK'] // 2
        y = pole_settings['HEADER_MARGIN'] + \
            block[1] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) + pole_settings['SIZE_BLOCK'] // 2
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), pole_settings['SIZE_BLOCK'] // 6)

    def draw_grid(self):  # рисует сетку для игры
        self.screen.fill(pole_settings['FRAME_COLOR'])
        for x in [self.pl_rect_x, self.com_rect_x]:
            pygame.draw.rect(self.screen, pole_settings['HEADER_COLOR'],
                             [x, 0, self.POLE_SIZE, pole_settings['HEADER_MARGIN']])

        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for row in range(pole_settings['COUNT_BLOCKS']):
            for column in range(pole_settings['COUNT_BLOCKS']):
                self.draw_block(pole_settings['LEFT_POLE_COLOR'], row, column)
                self.draw_block(pole_settings['RIGHT_POLE_COLOR'], row, column, 'computer')
                if row < 10:
                    num_ver = pole_settings['FONT_2'].render(str(row + 1), True, (0, 0, 0))
                    letters_hor = pole_settings['FONT_2'].render(letters[row], True, (0, 0, 0))
                    num_ver_height = num_ver.get_height()
                    letters_hor_width = letters_hor.get_width()
                    for x in [self.pl_rect_x, self.com_rect_x]:
                        self.screen.blit(num_ver, (x - (pole_settings['SIZE_BLOCK'] // 2),
                                                   pole_settings['HEADER_MARGIN'] +
                                                   row * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) +
                                                   (pole_settings['SIZE_BLOCK'] // 2 - num_ver_height // 2)))
                        self.screen.blit(letters_hor,
                                         (x + row * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) +
                                          (pole_settings['SIZE_BLOCK'] // 2 + pole_settings['MARGIN'] // 2
                                           - letters_hor_width // 2),
                                          pole_settings['HEADER_MARGIN'] - pole_settings['SIZE_BLOCK'] // 2))

    def draw_ships(self, name='player'):  # рисует корабли на поле
        for ship in self._ships:
            for coord_1, coord_2 in zip(ship.ship_x, ship.ship_y):
                self.draw_block(pole_settings['SHIP_COLORS'][ship.length], coord_2, coord_1, name)

    def check_hit(self, x, y, opponent_hit_ships, opponent='player'):  # проверяет, попал ли снаряд в цель
        if opponent_hit_ships[y, x] in [1, 2, 3, 4]:
            opponent_hit_ships[y, x] = opponent_hit_ships[y, x] / 5
            self.draw_hit([x, y], opponent)
            return True
        elif opponent_hit_ships[y, x] != 0.3 and opponent_hit_ships[y, x] not in [0.2, 0.4, 0.6, 0.8]:
            opponent_hit_ships[y, x] = 0.3
            self.draw_fail([x, y], opponent)
            return False

    def fill_the_cells_around(self, x, y, opponent_avail_hit_ships, opponent_hit_ships,
                              opponent='player'):  # заполняет все клетки, окружающие корабль
        for k in range(-1, 2):
            for m in range(-1, 2):
                if 0 <= x + k < 10 and 0 <= y + m < 10:
                    if k != 0 or m != 0:
                        opponent_hit_ships[y + m, x + k] = 0.3
                        opponent_avail_hit_ships.discard((x + k, y + m))
                        self.draw_fail((x + k, y + m), opponent)

    def computer_hit(self, computer_avail_hit_ships, computer_hit_ships):  # описывает ход компьютера
        pygame.time.delay(1000)
        x, y = choice(list(computer_avail_hit_ships))
        computer_avail_hit_ships.discard((x, y))
        return x, y, self.check_hit(x, y, computer_hit_ships, 'player')

    @staticmethod
    def get_avail_cells(x, y, available_for_hit, hit_ships):  # возвращает все клетки, подходящие для удара
        for k in range(-1, 2):
            for m in range(-1, 2):
                if 0 <= x + k < 10 and 0 <= y + m < 10 and abs(k + m) == 1:
                    if hit_ships[y + m, x + k] not in [0.2, 0.4, 0.6, 0.8] and \
                            hit_ships[y + m, x + k] != 0.3:
                        available_for_hit.add((x + k, y + m))
        return available_for_hit

    def update_around(self, cells_around, last_com_hit, comp_hit_ships, avail_hit_ships, com_sum,
                      opponent='player'):  # обновляет список клеток вокруг текущей
        summa = comp_hit_ships[last_com_hit[0][1], last_com_hit[0][0]]
        avail_hit_ships.discard((last_com_hit[-1][0], last_com_hit[-1][1]))
        cells_around.discard((last_com_hit[-1][0], last_com_hit[-1][1]))
        for el in last_com_hit[1:]:
            summa += comp_hit_ships[el[1], el[0]]
        if summa == 0.2:
            self.draw_block((0, 0, 0), last_com_hit[0][1], last_com_hit[0][0])
            self.fill_the_cells_around(last_com_hit[0][0], last_com_hit[0][1], avail_hit_ships, comp_hit_ships)
            com_sum += 1
            cells_around = set()
        elif len(last_com_hit) > 1:
            x, y = last_com_hit[-1]
            if (x == last_com_hit[-2][0] - 1 or x == last_com_hit[-2][0] + 1) \
                    and y == last_com_hit[-2][1]:
                for k in [-1, 1]:
                    if 0 <= y + k < 10:
                        for el in [x, last_com_hit[-2][0]]:
                            comp_hit_ships[y + k, el] = 0.3
                            self.draw_fail([el, y + k], opponent)
                            cells_around.discard((el, y + k))
                            avail_hit_ships.discard((el, y + k))
            if (y == last_com_hit[-2][1] - 1 or y == last_com_hit[-2][1] + 1) and x == last_com_hit[-2][0]:
                for k in [-1, 1]:
                    if 0 <= x + k < 10:
                        for el in [y, last_com_hit[-2][1]]:
                            comp_hit_ships[el, x + k] = 0.3
                            self.draw_fail([x + k, el], opponent)
                            cells_around.discard((x + k, el))
                            avail_hit_ships.discard((x + k, el))
            if round(summa, 1) not in [0.8, 1.8, 3.2]:
                cells_around.update(cells_around)
            else:
                for el in last_com_hit:
                    self.draw_block((0, 0, 0), el[1], el[0], opponent)
                    self.fill_the_cells_around(el[0], el[1], avail_hit_ships, comp_hit_ships, opponent)
                com_sum += len(last_com_hit)
                cells_around = set()
        return cells_around, com_sum

    def show_message(self, text, rect=pygame.Rect(0, 0, 70, 70),
                     which_font=pole_settings['FONT_2'], color=(255, 0, 0)):  # выводит сообщение на экран
        text_width, text_height = which_font.size(text)
        x_start = rect.centerx - text_width / 2
        y_start = rect.centery - text_height / 2
        text_to_blit = which_font.render(text, True, color)
        self.screen.fill((255, 255, 255), rect)
        self.screen.blit(text_to_blit, (x_start, y_start))
