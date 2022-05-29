import pygame as pg 
import random 
from copy import deepcopy


pg.init()


# CONSTANTS
WIDTH = 800
HEIGHT = 800
BOARD_WIDTH = 600
BOARD_HEIGHT = 600
FPS = 30 
TILE_COLORS = {
    2: (20, 144, 234),
    4: (193, 247, 34),
    8: (105, 27, 161),
    16: (125, 2, 106),
    32: (29, 13, 90),
    64: (170, 49, 171),
    128: (0, 105, 41),
    256: (134, 22, 229),
    512: (4, 2, 169),
    1024: (124, 198, 80),
    2048: (25, 124, 196)
}


def draw_tiles(screen, matrix):
    start_x = WIDTH//2 - BOARD_WIDTH//2
    start_y = HEIGHT//2 - BOARD_HEIGHT//2
    number_font = pg.font.SysFont('Comic Sans MS', 50)

    for row in range(4):
        for col in range(4):
            tile = matrix[row][col]
            if tile:
                x = start_x + col * 150 
                y = start_y + row * 150
                pg.draw.rect(screen, TILE_COLORS[tile], (x, y, 150, 150))
                number_surface = number_font.render(str(tile), False, (255, 255, 255))
                screen.blit(number_surface, (x + 75 - number_surface.get_width()//2, y + 75 - number_surface.get_height()//2))
                    


def draw_board(screen, matrix):
    pg.draw.rect(screen, (187, 173, 160), (WIDTH // 2 - 310, HEIGHT//2 - 310, 620, 620))
    pg.draw.rect(screen, (205, 193, 180), (WIDTH//2 - BOARD_WIDTH//2, HEIGHT//2 - BOARD_HEIGHT//2, BOARD_WIDTH, BOARD_HEIGHT))

    draw_tiles(screen, matrix)

    line_pos = WIDTH//2 - BOARD_WIDTH//2
    for _ in range(5):
        pg.draw.line(screen, (187, 173, 160), (WIDTH//2 - BOARD_WIDTH//2, line_pos), (WIDTH//2 - BOARD_WIDTH//2 + BOARD_WIDTH, line_pos), 15)
        pg.draw.line(screen, (187, 173, 160), (line_pos, WIDTH//2 - BOARD_WIDTH//2), (line_pos, WIDTH//2 - BOARD_WIDTH//2 + BOARD_WIDTH,), 15)
        line_pos += 150


def show_score(screen):
    global score 
    score_font = pg.font.SysFont('Comic Sans MS', 32)
    score_surface = score_font.render(f'Score: {score}', False, (255, 255, 255))
    screen.blit(score_surface, (90, 25))


def game_over_screen(screen):
    global win 

    if win:
        text = 'You won'
    else:
        text = 'You lost'

    text_font = pg.font.SysFont('Comic Sans MS', 70)
    text_surface = text_font.render(text, False, (255, 255, 255))
    screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, 300 - text_surface.get_height()//2))

    pg.draw.rect(screen, (192, 192, 192), (WIDTH //2 - 100, HEIGHT // 2 - 35, 200, 70))
    play_again_font = pg.font.SysFont('Comic Sans MS', 30)
    play_again_surface = play_again_font.render('Play Again?', False, (255, 255, 255))
    screen.blit(play_again_surface, (WIDTH //2 - play_again_surface.get_width()//2, HEIGHT // 2 - play_again_surface.get_height()//2))


def draw(screen, matrix):
    global game_over

    screen.fill('gray')
    draw_board(screen, matrix)
    show_score(screen)

    if game_over:
        game_over_screen(screen)

    pg.display.update()


# logic functions
def random_number():
    # 10% chance for getting 4 on initial board
    if random.random() < 0.1:
        number = 4
    # otherwise 2
    else:
        number = 2
    return number


def random_tiles(matrix, initializing=False):
    number = random_number()
    for i in range(1 + initializing):
        row = random.randrange(0, 4)
        col = random.randrange(0, 4)
        while matrix[row][col]:
            row = random.randrange(0, 4)
            col = random.randrange(0, 4)
        matrix[row][col] = number
    return matrix


def initialize_matrix():
    return random_tiles([[0 for _ in range(4)] for _ in range(4)], True)


def is_full(matrix):
    for row in matrix:
        if not all(row):
            return False
    return True


def did_change(old_matrix, new_matrix):
    return old_matrix != new_matrix


def can_swipe(matrix):
    if not is_full(matrix):
        return True
    for row in range(4):
        for col in range(4):
            number = matrix[row][col]
            if col < 3:
                next_number = matrix[row][col + 1]
                if number == next_number:
                    return True
            if row < 3:
                next_number = matrix[row + 1][col]
                if number == next_number:
                    return True
    return False


def won(matrix):
    if any(2048 in row for row in matrix):
        return True
    return False


# help functions for traverse function
def prepare_for(matrix, direction):
    matrix_len = len(matrix)

    if direction == 'right':
        step_col = stop_col = -1
        stop_row = matrix_len
        start_col = matrix_len - 2
        start_row = 0
        step_row = 1
    elif direction == 'left':
        step_row = start_col = step_col = 1
        stop_row = stop_col = matrix_len
        start_row = 0
    elif direction == 'up':
        stop_row = stop_col = matrix_len
        start_row = step_row = step_col = 1
        start_col = 0
    else:
        start_row = matrix_len - 2
        step_row = stop_row = -1
        stop_col = matrix_len
        start_col = 0
        step_col = 1

    return (start_row, step_row, stop_row, start_col, step_col, stop_col)


def evaluate_while_condition(matrix, direction, while_row, while_col):
    matrix_len = len(matrix)

    if direction == 'right':
        condition = while_col < matrix_len and not matrix[while_row][while_col]
    elif direction == 'left':
        condition = while_col >= 0 and not matrix[while_row][while_col]
    elif direction == 'up':
        condition = while_row >= 0 and not matrix[while_row][while_col]
    else:
        condition = while_row < matrix_len and not matrix[while_row][while_col]

    return condition


def prepare_while(matrix, direction, row, col):
    if direction == 'right':
        while_row = row
        while_col = col + 1
        append_in_row_indexing = while_row_increment = 0
        append_in_col_indexing = -1
        while_col_increment = 1
    elif direction == 'left':
        while_row = row
        while_col = col - 1
        append_in_row_indexing = while_row_increment = 0
        append_in_col_indexing = 1
        while_col_increment = -1
    elif direction == 'up':
        while_row = row - 1
        while_col = col
        append_in_row_indexing = 1
        append_in_col_indexing = while_col_increment = 0
        while_row_increment = -1
    else:
        while_row = row + 1
        while_col = col
        append_in_row_indexing = -1
        append_in_col_indexing = while_col_increment = 0
        while_row_increment = 1

    return (while_row, while_col, append_in_row_indexing, append_in_col_indexing, while_row_increment, while_col_increment)


def swipe_towards(matrix, while_row, while_col, direction, append_in_row_indexing, append_in_col_indexing, while_row_increment, while_col_increment, tile):
    condition = evaluate_while_condition(
        matrix, direction, while_row, while_col)

    while condition:
        matrix[while_row][while_col] = tile
        matrix[while_row + append_in_row_indexing][while_col +
                                                   append_in_col_indexing] = 0
        while_row += while_row_increment
        while_col += while_col_increment
        condition = evaluate_while_condition(
            matrix, direction, while_row, while_col)

    return matrix


def traverse(matrix, direction):
    start_row, step_row, stop_row, start_col, step_col, stop_col = prepare_for(
        matrix, direction)
    for row in range(start_row, stop_row, step_row):
        for col in range(start_col, stop_col, step_col):
            tile = matrix[row][col]
            if tile:
                while_row, while_col, append_in_row_indexing, append_in_col_indexing, while_row_increment, while_col_increment = prepare_while(
                    matrix, direction, row, col)
                swipe_towards(matrix, while_row, while_col, direction, append_in_row_indexing,
                              append_in_col_indexing, while_row_increment, while_col_increment, tile)

    return matrix


def swipe(key, screen):
    global matrix

    if won(matrix):
        game_over_func(screen, True)
        return

    if can_swipe(matrix):
        matrix_copy = deepcopy(matrix)
        matrix = traverse(matrix, key)
        matrix = combine(key, matrix)
    else:
        game_over_func(screen)
        return

    if not is_full(matrix) and did_change(matrix_copy, matrix):
        matrix = random_tiles(matrix)


def combine(direction, matrix):
    if direction == 'right':
        for row in matrix:
            for idx in range(len(row)-2, -1, -1):
                tile = row[idx]
                next_tile = row[idx + 1]
                if tile and tile == next_tile:
                    row[idx + 1] *= 2
                    row[idx] = 0
                    matrix = traverse(matrix, direction)
                    update_score(row[idx + 1])

    elif direction == 'left':
        for row in matrix:
            for idx in range(1, len(row)):
                tile = row[idx]
                prev_tile = row[idx - 1]
                if tile and tile == prev_tile:
                    row[idx - 1] *= 2
                    row[idx] = 0
                    matrix = traverse(matrix, direction)
                    update_score(row[idx - 1])

    elif direction == 'up':
        for row in range(1, len(matrix)):
            for col in range(4):
                tile = matrix[row][col]
                upper_tile = matrix[row - 1][col]
                if tile and tile == upper_tile:
                    matrix[row - 1][col] *= 2
                    matrix[row][col] = 0
                    matrix = traverse(matrix, direction)
                    update_score(matrix[row - 1][col])

    else:
        for row in range(len(matrix)-2, -1, -1):
            for col in range(4):
                tile = matrix[row][col]
                lower_tile = matrix[row + 1][col]
                if tile and tile == lower_tile:
                    matrix[row + 1][col] *= 2
                    matrix[row][col] = 0
                    matrix = traverse(matrix, direction)
                    update_score(matrix[row + 1][col])

    return matrix


def update_score(value):
    global score
    score += value 


def restart():
    global matrix, game_over, win, score
    matrix = initialize_matrix()
    game_over = False 
    win = False 
    score = 0


def game_over_func(screen, won=False):
    global win, game_over 

    game_over = True 
    win = True if won else False       


def main():
    global matrix, score, win, game_over

    run = True 
    clock = pg.time.Clock()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    matrix = initialize_matrix()
    game_over = False 
    win = False 
    score = 0

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False 
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    swipe('left', screen)
                if event.key == pg.K_RIGHT:
                    swipe('right', screen)
                if event.key == pg.K_UP:
                    swipe('up', screen)
                if event.key == pg.K_DOWN:
                    swipe('down', screen)
            if event.type == pg.MOUSEBUTTONDOWN and game_over:
                if event.button == 1:
                    mx, my = pg.mouse.get_pos()
                    if mx in range(300, 500) and my in range(365, 435):
                        restart()
            
        clock.tick(FPS)
        pg.time.delay(30)
        draw(screen, matrix)


if __name__ == '__main__':
    main()
