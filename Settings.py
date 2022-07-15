import pygame

pygame.init()
pole_settings = {
    'SIZE_BLOCK': 60,
    'FRAME_COLOR': (255, 255, 255),
    'LEFT_POLE_COLOR': (175, 238, 238),
    'RIGHT_POLE_COLOR': (112, 128, 144),
    'HEADER_COLOR': (0, 206, 209),
    'HEADER_MARGIN': 70,
    'BOTTOM_MARGIN': 70,
    'COUNT_BLOCKS': 10,
    'MARGIN': 1,
    'SHIP_COLORS': {
        4: (0, 102, 0),
        3: (154, 205, 50),
        2: (255, 69, 0),
        1: (75, 0, 130)
    },
    'FONT_1': pygame.font.SysFont('arial', 30),
    'FONT_2': pygame.font.SysFont('notosans', 20),
    'FONT_3': pygame.font.SysFont('courier', 20)
}
pole_settings['LEFT_MARGIN'] = int(pole_settings['SIZE_BLOCK'] // 1.5)


class Button:
    def __init__(self, x, y, width, height, text):
        self.size = (width, height)
        self.text = text  # Текст кнопки
        self.x = x  # Позиция х кнопки
        self.y = y  # Позиция у кнопки
        self.rect_button = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
        self.active = True

    def draw_button(self, pole, font=pole_settings['FONT_3'], btn_color=pole_settings['FRAME_COLOR'],
                    text_color=(255, 255, 255)):
        pygame.draw.rect(pole.screen, btn_color, self.rect_button)
        text_to_blit = font.render(self.text, True, text_color)
        pole.screen.blit(text_to_blit, (self.rect_button.centerx - 2 * pole_settings['SIZE_BLOCK'],
                                        self.rect_button.centery - 14))
