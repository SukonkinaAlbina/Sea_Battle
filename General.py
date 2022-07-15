import pygame
import sys
from Settings import Button, pole_settings
import pygame_menu
from GamePole import GamePole

pygame.init()


class Play(GamePole):
    def show(self):
        menu.disable()
        player_name = text_input.get_value()
        summa_pl, summa_com = 0, 0
        game_over = False
        computer_turn = False
        self.draw_grid()
        btn_1 = Button(pole_settings['LEFT_MARGIN'], pole_settings['HEADER_MARGIN'] +
                       (self.size[0] - self.SPACE_BETWEEN - 2 * pole_settings['LEFT_MARGIN']) / 2,
                       5 * (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']), 40, 'Новое поле')
        btn_1.draw_button(self, btn_color=(0, 130, 234))
        btn_start = Button(btn_1.x + btn_1.size[0], btn_1.y, *btn_1.size, 'Начать игру')
        btn_start.draw_button(self, btn_color=(0, 0, 234))
        player_ships = self.arrange_the_ships()
        computer_hit_ships = player_ships
        computer_avail_hit_ships = set([(x, y) for x in range(pole_settings['COUNT_BLOCKS']) for y in
                                        range(pole_settings['COUNT_BLOCKS'])])
        available = computer_avail_hit_ships
        player_shots = {}
        player_avail_hit_ships = computer_avail_hit_ships.copy()
        last_comp_shot = []
        cells_around = set()
        pole_2 = Play()
        comp_ships = pole_2.arrange_the_ships()
        self.draw_ships()
        for name, x in zip([player_name, 'Computer'], [self.pl_rect_x, self.com_rect_x]):
            text = pole_settings['FONT_1'].render(name, 0, (180, 0, 49))
            self.screen.blit(text, (x, 0))
        #pole_2.draw_ships('computer')
        pygame.display.update()
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('exit')
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and btn_1.rect_button.collidepoint(pygame.mouse.get_pos()) \
                        and btn_1.active:
                    new_pole = Play()
                    new_pole.show()
                elif event.type == pygame.MOUSEBUTTONDOWN and btn_start.rect_button.collidepoint(pygame.mouse.get_pos()) \
                        and btn_start.active:
                    btn_1.active, btn_start.active = False, False
                    btn_1.draw_button(self)
                    btn_start.draw_button(self)
                elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN and not btn_start.active:
                    x, y = event.pos
                    if self.com_rect_x <= x <= self.com_rect_x + self.POLE_SIZE \
                            and pole_settings['HEADER_MARGIN'] <= \
                            y <= pole_settings['HEADER_MARGIN'] + self.POLE_SIZE:
                        block = (
                            (x - self.com_rect_x) // (pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']),
                            (y - pole_settings['HEADER_MARGIN']) // (
                                    pole_settings['SIZE_BLOCK'] + pole_settings['MARGIN']))
                        if comp_ships[block[1], block[0]] == 0.3 or comp_ships[block[1], block[0]] in [0.2, 0.4, 0.6,
                                                                                                       0.8]:
                            computer_turn = False
                        else:
                            computer_turn = not self.check_hit(*block, comp_ships, 'computer')
                            if not computer_turn:
                                for sh in pole_2._ships:
                                    if block in zip(sh.ship_x, sh.ship_y):
                                        player_shots.setdefault((pole_2._ships.index(sh), sh.length), [])
                                        player_shots[(pole_2._ships.index(sh), sh.length)].append(block)
                                for key, val in player_shots.items():
                                    if key[1] == len(val):
                                        summa_pl += len(val)
                                        for el in val:
                                            self.draw_block((0, 0, 0), *el[::-1], 'computer')
                                            self.fill_the_cells_around(*el, player_avail_hit_ships, comp_ships,
                                                                       'computer')
                                        player_shots[key] = []
                    if summa_pl == 20:
                        game_over = True
            if computer_turn:
                x, y, computer_turn = self.computer_hit(available, computer_hit_ships)
                if computer_turn:
                    last_comp_shot.append((x, y))
                    cells_around = set(self.get_avail_cells(x, y, cells_around, computer_hit_ships))
                    cells_around, summa_com = self.update_around(cells_around, last_comp_shot,
                                                                 computer_hit_ships,
                                                                 computer_avail_hit_ships, summa_com)
                    if cells_around:
                        available = cells_around
                    else:
                        available = computer_avail_hit_ships
                        last_comp_shot = []
                    if summa_com == 20:
                        game_over = True
            pygame.display.update()
        if summa_pl == 20:
            text = 'Вы выиграли!'
        if summa_com == 20:
            text = 'Вы проиграли!'
        player = Play()
        menu_new = pygame_menu.Menu(text, player.size[0], player.size[1],
                                    theme=pygame_menu.themes.THEME_GREEN)
        menu_new.add.button('Restart', player.show)
        menu_new.add.button('Quit', pygame_menu.events.EXIT)
        if menu_new.is_enabled():
            menu_new.mainloop(player.screen)
        pygame.display.update()


# Play
pole_player = Play()
menu = pygame_menu.Menu('Welcome', pole_player.size[0], pole_player.size[1], theme=pygame_menu.themes.THEME_BLUE)
text_input = menu.add.text_input('Name :', default='Player-1')
menu.add.button('Play', pole_player.show)
menu.add.button('Quit', pygame_menu.events.EXIT)
if menu.is_enabled():
    menu.mainloop(pole_player.screen)
