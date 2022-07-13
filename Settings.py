import pygame
pygame.init()
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
    },
    'FONT_1' : pygame.font.SysFont('courier', 20),
    'FONT_2' : pygame.font.SysFont('notosans', 20)
}