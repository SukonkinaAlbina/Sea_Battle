import pygame
from random import randint, choice, sample
import sys
import numpy as np
from Settings import pole_settings

pygame.init()


class Ship:
    def __init__(self, length, tp=1, x=None, y=None):
        self.length = length
        self.tp = tp
        self.x = x
        self.y = y
        self.ship_x, self.ship_y = [0] * length, [0] * length
        self.cells = [length] * length

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
    SPACE_BETWEEN = 2 * pole_settings['SIZE_BLOCK']
    POLE_SIZE = (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) * pole_settings['COUNT_BLOCKS']
    _size = [2 * (pole_settings['LEFT_MARGIN'] + POLE_SIZE) + SPACE_BETWEEN,
             POLE_SIZE + pole_settings['HEADER_MARGIN'] + pole_settings['BOTTOM_MARGIN']]
    _ships = []
    screen = pygame.display.set_mode(_size)
    pygame.display.set_caption('Морской бой')
    timer = pygame.time.Clock()

    def __init__(self):
        self._ships = [Ship(4, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)),
                       Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)),
                       Ship(1, tp=randint(1, 2))]
        self._cells = np.zeros((pole_settings['COUNT_BLOCKS'], pole_settings['COUNT_BLOCKS']))
        self._available = set([(x, y) for x in range(pole_settings['COUNT_BLOCKS']) for y in
                               range(pole_settings['COUNT_BLOCKS'])])
        self.pl_rect_x = pole_settings['LEFT_MARGIN']
        self.com_rect_x = self.pl_rect_x + self.POLE_SIZE + 2 * pole_settings['MARGIN'] + self.SPACE_BETWEEN

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
                                                                            ship.x:ship.x + ship.length] == 0,
                                                                            ship.length, 0)
            else:
                self._cells[ship.y:ship.y + ship.length, ship.x] = np.where(self._cells[ship.y:ship.y + ship.length,
                                                                            ship.x] == 0, ship.length, 0)
            available = self.update_available_block(ship)
        return self._cells

    def update_available_block(self, ship):
        for x, y in zip(ship.ship_x, ship.ship_y):
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 <= x + k < 10 and 0 <= y + m < 10:
                        if self._cells[y + m][x + k] not in [1, 2, 3, 4] and self._cells[y + m][x + k] != 0.2:
                            self._cells[y + m][x + k] = 0.2
                        self._available.discard((y + m, x + k))
        return self._available

    def draw_block(self, color, row, column, player='player'):
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

    def draw_hit(self, block, opponent='player'):
        if opponent != 'player':
            x_0 = self.com_rect_x
        else:
            x_0 = self.pl_rect_x
        x = x_0 + block[0] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN'])
        y = pole_settings['HEADER_MARGIN'] + \
            block[1] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN'])
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x + pole_settings['SIZE_BLOCK'],
                                                          y + pole_settings['SIZE_BLOCK']),
                         pole_settings['SIZE_BLOCK'] // 6)
        pygame.draw.line(self.screen, (0, 0, 0), (x, y + pole_settings['SIZE_BLOCK']),
                         (x + pole_settings['SIZE_BLOCK'], y),
                         pole_settings['SIZE_BLOCK'] // 6)
        # print((x + self.pole_settings['SIZE_BLOCK'], y + self.pole_settings['SIZE_BLOCK']))
        # pygame.display.flip()

    def draw_fail(self, block, opponent='player'):
        if opponent != 'player':
            x_0 = self.com_rect_x
        else:
            x_0 = self.pl_rect_x
        x = x_0 + block[0] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) + \
            pole_settings['SIZE_BLOCK'] // 2
        y = pole_settings['HEADER_MARGIN'] + \
            block[1] * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']) + pole_settings['SIZE_BLOCK'] // 2
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), pole_settings['SIZE_BLOCK'] // 6)

    def draw_grid(self):
        self.screen.fill(pole_settings['FRAME_COLOR'])
        for x in [self.pl_rect_x, self.com_rect_x]:
            pygame.draw.rect(self.screen, pole_settings['HEADER_COLOR'],
                             [x, 0, self.POLE_SIZE, pole_settings['HEADER_MARGIN']])
        btn_1 = Button(pole_settings['LEFT_MARGIN'], pole_settings['HEADER_MARGIN'] +
                       (self._size[0] - self.SPACE_BETWEEN - 2 * pole_settings['LEFT_MARGIN']) / 2,
                       5 * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']), 40, 'Новое поле')
        btn_1.draw_button(self, pole_settings['FONT_1'], (0, 130, 234), (255, 255, 255))
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
        return btn_1

    def draw_ships(self, name='player'):
        for ship in self._ships:
            for coord_1, coord_2 in zip(ship.ship_x, ship.ship_y):
                self.draw_block(pole_settings['SHIP_COLORS'][ship.length], coord_2, coord_1, name)

    def check_hit(self, x, y, opponent_hit_ships, opponent='player'):
        if opponent_hit_ships[y, x] in [1, 2, 3, 4]:
            opponent_hit_ships[y, x] = opponent_hit_ships[y, x] / 4
            self.draw_hit([x, y], opponent)
            return True
        elif opponent_hit_ships[y, x] != 0.3 and opponent_hit_ships[y, x] not in [0.25, 0.5, 0.75, 1]:
            opponent_hit_ships[y, x] = 0.3
            self.draw_fail([x, y], opponent)
            return False
        else:
            return True

    def fill_the_cells_around(self, x, y, opponent_avail_hit_ships, opponent_hit_ships, opponent='player'):
        for k in range(-1, 2):
            for m in range(-1, 2):
                if 0 <= x + k < 10 and 0 <= y + m < 10:
                    if k != 0 or m != 0:
                        opponent_hit_ships[y + m, x + k] = 0.3
                        opponent_avail_hit_ships.discard((x + k, y + m))
                        self.draw_fail((x + k, y + m), opponent)

    def computer_hit(self, computer_avail_hit_ships, computer_hit_ships):
        pygame.time.delay(500)
        x, y = choice(list(computer_avail_hit_ships))
        computer_avail_hit_ships.discard((x, y))
        # print(available)
        return x, y, self.check_hit(x, y, computer_hit_ships, 'player')

    @staticmethod
    def get_avail_cells(x, y, available_for_hit, hit_ships):
        for k in range(-1, 2):
            for m in range(-1, 2):
                if 0 <= x + k < 10 and 0 <= y + m < 10 and abs(k + m) == 1:
                    if hit_ships[y + m, x + k] not in [0.25, 0.5, 0.75, 1] and \
                            hit_ships[y + m, x + k] != 0.3:
                        available_for_hit.add((x + k, y + m))
        return available_for_hit

    def update_around(self, cells_around, last_com_hit, comp_hit_ships, avail_hit_ships, opponent='player'):
        summa = comp_hit_ships[last_com_hit[0][1], last_com_hit[0][0]]
        for el in last_com_hit[1:]:
            summa += comp_hit_ships[el[1], el[0]]
        if summa == 0.25:
            self.draw_block((0, 0, 0), last_com_hit[0][1], last_com_hit[0][0])
            self.fill_the_cells_around(last_com_hit[0][0], last_com_hit[0][1], avail_hit_ships, comp_hit_ships)
            cells_around = set()
        elif len(last_com_hit) > 1:
            x, y = last_com_hit[-1]
            if (x == last_com_hit[-2][0] - 1 or x == last_com_hit[-2][0] + 1) \
                    and y == last_com_hit[-2][1]:
                for k in [-1, 1]:
                    if 0 <= y + k < 10:
                        comp_hit_ships[y + k, x] = 0.3
                        self.draw_fail([x, y + k], opponent)
                        cells_around.discard((x, y + k))
                        avail_hit_ships.discard((x, y + k))
            if (y == last_com_hit[-2][1] - 1 or y == last_com_hit[-2][1] + 1) and x == last_com_hit[-2][0]:
                for k in [-1, 1]:
                    if 0 <= x + k < 10:
                        comp_hit_ships[y, x + k] = 0.3
                        self.draw_fail([x + k, y], opponent)
                        cells_around.discard((x + k, y))
                        avail_hit_ships.discard((x + k, y))
            if summa not in [1, 2.25, 4]:
                cells_around.update(cells_around)
            else:
                for el in last_com_hit:
                    self.draw_block((0, 0, 0), el[1], el[0], opponent)
                    self.fill_the_cells_around(el[0], el[1], avail_hit_ships, comp_hit_ships, opponent)
                cells_around = set()
        return cells_around

    def show(self):
        BLOCK = (0, 0)
        summa = 0
        computer_turn = False
        btn_1 = self.draw_grid()
        player_ships = self.arrange_the_ships()
        computer_hit_ships = player_ships
        computer_avail_hit_ships = set([(x, y) for x in range(pole_settings['COUNT_BLOCKS']) for y in
                                        range(pole_settings['COUNT_BLOCKS'])])
        available = computer_avail_hit_ships
        player_shots = {}
        player_avail_hit_ships = computer_avail_hit_ships
        last_comp_shot, last_pl_shot = [], []
        cells_around = set()
        pole_2 = GamePole()
        comp_ships = pole_2.arrange_the_ships()
        self.draw_ships()
        pole_2.draw_ships('computer')
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
                    if self.com_rect_x <= x <= self.com_rect_x + self.POLE_SIZE \
                            and pole_settings['HEADER_MARGIN'] <= \
                            y <= pole_settings['HEADER_MARGIN'] + self.POLE_SIZE:
                        block = (
                            (x - self.com_rect_x) // (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']),
                            (y - pole_settings['HEADER_MARGIN']) // (
                                    pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']))
                        if block not in last_pl_shot:
                            computer_turn = not self.check_hit(*block, comp_ships, 'computer')
                            if not computer_turn:
                                for sh in pole_2._ships:
                                    if block in zip(sh.ship_x, sh.ship_y):
                                        player_shots.setdefault((pole_2._ships.index(sh), sh.length), [])
                                        player_shots[(pole_2._ships.index(sh), sh.length)].append(block)
                                for key, val in player_shots.items():
                                    if key[1] == len(val):
                                        for el in val:
                                            self.draw_block((0, 0, 0), *el[::-1], 'computer')
                                            self.fill_the_cells_around(*el, player_avail_hit_ships, comp_ships, 'computer')
                                            print(len(player_avail_hit_ships))
            if summa == 20:
                self.show_message('Игрок выиграл!', (0, 0, self._size[0], self._size[1]))

                # computer_turn = True
            if computer_turn:
                x, y, computer_turn = self.computer_hit(available, computer_hit_ships)
                if computer_turn:
                    last_comp_shot.append((x, y))
                    cells_around = set(self.get_avail_cells(x, y, cells_around, computer_hit_ships))
                    cells_around = self.update_around(cells_around, last_comp_shot, computer_hit_ships,
                                                      computer_avail_hit_ships)
                    if cells_around:
                        available = cells_around
                    else:
                        available = computer_avail_hit_ships
                        last_comp_shot = []
            pygame.display.update()

    def show_message(self, text, rect, which_font=pole_settings['FONT_2'], color=(255, 0, 0)):
        text_width, text_height = which_font.size(text)
        rect = pygame.Rect(0, 0, self._size[0], self._size[1])
        x_start = rect.centerx - text_width / 2
        y_start = rect.centery - text_height / 2
        text_to_blit = which_font.render(text, True, color)
        self.screen.fill((255, 255, 255), rect)
        self.screen.blit(text_to_blit, (x_start, y_start))


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
        pole.screen.blit(text_to_blit, (self.rect_button.centerx - 2 * pole_settings['SIZE_BLOCK'],
                                        self.rect_button.centery - 14))


# Play


pole_player = GamePole()
# p_1 = pole_player.arrange_the_ships()
# pole_computer = GamePole()
# p_2 = pole_computer.arrange_the_ships()
pole_player.show()
