import pygame
import random

# --- settings ---
WIDTH = 900
HEIGHT = 700
WATER_COLOR = (71, 171, 169)
BUTTON_TEXT = (255, 255, 255)
TITLE_COLOR = (90, 60, 40)
BANNER_TEXT_COLOR = (101, 52, 22)
TURN_X_COLOR = (30, 90, 160)      # blue
TURN_O_COLOR = (200, 60, 60)      # red
FPS = 60

# --- board layout ---
BOARD_SIZE = 585                      # the whole wood board image, frame included
BOARD_X = (WIDTH - BOARD_SIZE) // 2   # left edge (centers it)
BOARD_Y = 95                          # top edge

# divider positions for the board's 9 cells (not perfectly equal - hand-drawn art)
COL_BOUNDS = [55, 211, 373, 529]
ROW_BOUNDS = [36, 190, 356, 513]


def cell_index(pos, bounds):
    """Which of the 3 columns/rows a board-local coordinate falls in, or -1."""
    for i in range(3):
        if bounds[i] <= pos < bounds[i + 1]:
            return i
    return -1


def cell_center(i, bounds):
    """The midpoint of column/row i, in board-local coordinates."""
    return (bounds[i] + bounds[i + 1]) // 2

# --- battlefield (game page) ---
GRASS_TILE = 64
UNIT_SIZE = 110
UNIT_ANIM_SPEED = 160                 # ms per idle animation frame
UNIT_FEET_Y = round(137 / 192 * UNIT_SIZE)   # feet position within the sprite frame

BLUE_UNIT_SPOTS = [(78, 210), (78, 400), (78, 590)]
RED_UNIT_SPOTS = [(822, 210), (822, 400), (822, 590)]

# --- home page scenery ---
BG_X = 66     # centers the island within the background picture
BG_Y = -60    # shifts the picture up: less sky, more water on screen

SPRITE = 192                               # foam / archer frames are 192x192
FOAM_FRAMES = 16
ANIM_SPEED = 120                           # ms per animation frame

FOAM_SPOTS = [
    (40, 614), (96, 627), (152, 622), (208, 626),
    (264, 641), (320, 642), (376, 645), (432, 645),
    (488, 646), (544, 627), (600, 629), (656, 626),
    (712, 635),
]
ARCHER_BLUE_SPOT = (113, 228)
ARCHER_RED_SPOT = (672, 174)

BUTTON_W = 352
BUTTON_H = 80
BUTTON_CX = 450                  # middle of the island
BACK_SIZE = 64

# --- setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

# --- images ---
background = pygame.image.load("assets/background.png").convert_alpha()
# make the water transparent so the animated foam shows through
pixels = pygame.PixelArray(background)
pixels.replace(pygame.Color(71, 171, 169, 255), pygame.Color(0, 0, 0, 0))
del pixels

foam_sheet = pygame.image.load("assets/water_foam.png").convert_alpha()


def load_frames(path, flip):
    """Cut the 8 frames out of a unit spritesheet (192x192 each)."""
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(8):
        frame = sheet.subsurface((i * 192, 0, 192, 192))
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        frames.append(frame)
    return frames


archer_blue = load_frames("assets/archer_blue.png", False)  # faces right
archer_red = load_frames("assets/archer_red.png", True)     # flipped to face left
btn_blue = pygame.image.load("assets/btn_blue.png").convert_alpha()
btn_blue_hover = pygame.image.load("assets/btn_blue_hover.png").convert_alpha()
btn_red = pygame.image.load("assets/btn_red.png").convert_alpha()
btn_red_hover = pygame.image.load("assets/btn_red_hover.png").convert_alpha()
bar_restart = pygame.image.load("assets/bar_restart.png").convert_alpha()
grass_tile = pygame.image.load("assets/tilemap.png").convert_alpha().subsurface((64, 64, 64, 64))
unit_shadow = pygame.image.load("assets/unit_shadow.png").convert_alpha()
unit_shadow = pygame.transform.scale(unit_shadow, (UNIT_SIZE, UNIT_SIZE // 3))


def load_unit(path, flip):
    """Like load_frames, but each frame is scaled down to UNIT_SIZE."""
    frames = load_frames(path, flip)
    return [pygame.transform.smoothscale(frame, (UNIT_SIZE, UNIT_SIZE)) for frame in frames]


warrior_blue = load_unit("assets/warrior_blue_idle.png", False)  # faces right
warrior_red = load_unit("assets/warrior_red_idle.png", True)     # flipped to face left


def load_trimmed(path, size):
    """Crop an image's transparent padding, then scale it to exactly `size`."""
    image = pygame.image.load(path).convert_alpha()
    mask = pygame.mask.from_surface(image, 8)
    content = max(mask.get_bounding_rects(), key=lambda r: r.width * r.height)
    return pygame.transform.scale(image.subsurface(content), size)


def load_fitted(path, box_size):
    """Crop an image's padding, then scale it to fit inside box_size without stretching."""
    image = pygame.image.load(path).convert_alpha()
    mask = pygame.mask.from_surface(image, 8)
    content = max(mask.get_bounding_rects(), key=lambda r: r.width * r.height)
    trimmed = image.subsurface(content)
    scale = box_size / max(trimmed.get_width(), trimmed.get_height())
    size = (round(trimmed.get_width() * scale), round(trimmed.get_height() * scale))
    return pygame.transform.smoothscale(trimmed, size)

icon_back = pygame.image.load("assets/icon_back.png").convert_alpha()
icon_back_big = pygame.transform.scale(icon_back, (BACK_SIZE + 10, BACK_SIZE + 10))


def load_board(path, box_size):
    """Like load_fitted, but centers the result on a full box_size square canvas."""
    fitted = load_fitted(path, box_size)
    canvas = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
    canvas.blit(fitted, ((box_size - fitted.get_width()) // 2, (box_size - fitted.get_height()) // 2))
    return canvas


board_wood = load_board("assets/boardwood.png", BOARD_SIZE)

# X/O mark size: the smallest cell dimension, so every cell keeps clear margin
smallest_cell = COL_BOUNDS[1] - COL_BOUNDS[0]
for i in range(3):
    col_width = COL_BOUNDS[i + 1] - COL_BOUNDS[i]
    if col_width < smallest_cell:
        smallest_cell = col_width
    row_height = ROW_BOUNDS[i + 1] - ROW_BOUNDS[i]
    if row_height < smallest_cell:
        smallest_cell = row_height
MARK_BOX = round(smallest_cell * 0.55)
mark_x = load_fitted("assets/swords.png", MARK_BOX)
mark_o = load_fitted("assets/target.png", MARK_BOX)
MARKS = {"X": mark_x, "O": mark_o}

FONT = "assets/fonts/ThaleahFat.ttf"
title_font = pygame.font.Font(FONT, 64)
button_font = pygame.font.Font(FONT, 34)
small_font = pygame.font.Font(FONT, 26)

# --- game state ---
page = "home"          # "home", "difficulty" or "game"
mode = ""               # "2 Players", "Easy", "Medium" or "Impossible"

# board[row][col]: "" = empty, board[0][0] is top-left, board[2][2] is bottom-right
board = [["", "", ""],
         ["", "", ""],
         ["", "", ""]]

turn = "X"              # whose turn it is
winner = ""              # "", "X", "O" or "Tie"

COMPUTER_DELAY = 1000    # ms the computer waits before playing its move
computer_ready_at = 0

# each button is [rectangle, label, normal image, hover image]
home_buttons = [
    [pygame.Rect(BUTTON_CX - BUTTON_W // 2, 345, BUTTON_W, BUTTON_H),
     "2 Players", btn_blue, btn_blue_hover],
    [pygame.Rect(BUTTON_CX - BUTTON_W // 2, 421, BUTTON_W, BUTTON_H),
     "Play vs Computer", btn_red, btn_red_hover],
]

difficulty_buttons = [
    [pygame.Rect(BUTTON_CX - BUTTON_W // 2, 250, BUTTON_W, BUTTON_H),
     "Easy", btn_blue, btn_blue_hover],
    [pygame.Rect(BUTTON_CX - BUTTON_W // 2, 350, BUTTON_W, BUTTON_H),
     "Medium", btn_blue, btn_blue_hover],
    [pygame.Rect(BUTTON_CX - BUTTON_W // 2, 450, BUTTON_W, BUTTON_H),
     "Impossible", btn_blue, btn_blue_hover],
]

restart_rect = pygame.Rect(WIDTH - 190, 25, 170, 42)
back_rect = pygame.Rect(20, 20, BACK_SIZE, BACK_SIZE)


def new_board():
    """Give back a fresh empty board."""
    return [["", "", ""],
            ["", "", ""],
            ["", "", ""]]


def fresh_round():
    """The board/turn/winner for a brand new round."""
    return new_board(), "X", ""


def draw_back_button(mouse_pos):
    """The arrow in the top-left corner; it grows a little when hovered."""
    if back_rect.collidepoint(mouse_pos):
        screen.blit(icon_back_big, (back_rect.x - 5, back_rect.y - 5))
    else:
        screen.blit(icon_back, back_rect)


def draw_text(text, font, color, center):
    """Draw text with its middle at the given (x, y) point."""
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    screen.blit(image, rect)


def draw_buttons(buttons, mouse_pos):
    """Draw every button in the list, swapping in its hover image when hovered."""
    for rect, label, image, hover_image in buttons:
        if rect.collidepoint(mouse_pos):
            screen.blit(hover_image, rect)
        else:
            screen.blit(image, rect)
        draw_text(label, button_font, BUTTON_TEXT, rect.center)


def draw_grass():
    """Tile the plain grass background across the whole screen."""
    for y in range(0, HEIGHT, GRASS_TILE):
        for x in range(0, WIDTH, GRASS_TILE):
            screen.blit(grass_tile, (x, y))


def draw_battlefield():
    """The grass, plus a row of warriors standing guard on each side."""
    draw_grass()

    frame = (pygame.time.get_ticks() // UNIT_ANIM_SPEED) % 8
    for frames, spots in [(warrior_blue, BLUE_UNIT_SPOTS), (warrior_red, RED_UNIT_SPOTS)]:
        for fx, fy in spots:
            shadow_rect = unit_shadow.get_rect(center=(fx, fy))
            screen.blit(unit_shadow, shadow_rect)
            unit_rect = frames[frame].get_rect(midtop=(fx, fy - UNIT_FEET_Y))
            screen.blit(frames[frame], unit_rect)


def draw_grid():
    """Draw the wood board - its own art already has the 9 cells divided."""
    screen.blit(board_wood, (BOARD_X, BOARD_Y))


def clicked_cell(pos):
    """Turn a mouse position into (row, col), or (-1, -1) if off the board."""
    x, y = pos
    col = cell_index(x - BOARD_X, COL_BOUNDS)
    row = cell_index(y - BOARD_Y, ROW_BOUNDS)
    if col == -1 or row == -1:
        return -1, -1
    return row, col


def draw_scenery():
    """Water, animated foam, the island picture, then the archers."""
    screen.fill(WATER_COLOR)

    frame = (pygame.time.get_ticks() // ANIM_SPEED) % FOAM_FRAMES
    foam = foam_sheet.subsurface(((frame % FOAM_FRAMES) * 192, 0, 192, 192))
    for cx, cy in FOAM_SPOTS:
        screen.blit(foam, (BG_X + cx - SPRITE // 2, BG_Y + cy - SPRITE // 2))

    screen.blit(background, (BG_X, BG_Y))

    shot = frame % 8
    for frames, (fx, fy) in [(archer_blue, ARCHER_BLUE_SPOT), (archer_red, ARCHER_RED_SPOT)]:
        screen.blit(frames[shot], (BG_X + fx - SPRITE // 2, BG_Y + fy - int(SPRITE * 0.78)))


def check_winner():
    """Look at the board and return "X", "O", "Tie", or "" (game still going)."""
    # rows
    for row in range(3):
        if board[row][0] != "" and board[row][0] == board[row][1] == board[row][2]:
            return board[row][0]

    # columns
    for col in range(3):
        if board[0][col] != "" and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]

    # diagonals
    if board[1][1] != "":
        if board[0][0] == board[1][1] == board[2][2]:
            return board[1][1]
        if board[0][2] == board[1][1] == board[2][0]:
            return board[1][1]

    # still going, or a tie
    for row in range(3):
        for col in range(3):
            if board[row][col] == "":
                return ""
    return "Tie"


def empty_cells():
    """A list of every (row, col) that is still empty."""
    cells = []
    for row in range(3):
        for col in range(3):
            if board[row][col] == "":
                cells.append((row, col))
    return cells


def find_winning_move(mark):
    """The (row, col) where `mark` would win right now, or None."""
    for row, col in empty_cells():
        board[row][col] = mark
        won = check_winner() == mark
        board[row][col] = ""
        if won:
            return row, col
    return None


def easy_move():
    """Pick a random empty cell."""
    return random.choice(empty_cells())


def medium_move():
    """Win if possible, block if necessary, otherwise random."""
    win = find_winning_move("O")
    if win is not None:
        return win
    block = find_winning_move("X")
    if block is not None:
        return block
    return random.choice(empty_cells())


def impossible_move():
    """Win, block, then center > corner > random."""
    win = find_winning_move("O")
    if win is not None:
        return win
    block = find_winning_move("X")
    if block is not None:
        return block

    if board[1][1] == "":
        return 1, 1

    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    open_corners = []
    for row, col in corners:
        if board[row][col] == "":
            open_corners.append((row, col))
    if open_corners:
        return random.choice(open_corners)

    return random.choice(empty_cells())


def computer_move():
    """Pick the computer's move for whichever difficulty is selected."""
    if mode == "Easy":
        return easy_move()
    elif mode == "Medium":
        return medium_move()
    else:
        return impossible_move()


def draw_marks():
    """Draw the X's and O's stored in the board."""
    for row in range(3):
        for col in range(3):
            mark = board[row][col]
            if mark == "":
                continue
            center_x = BOARD_X + cell_center(col, COL_BOUNDS)
            center_y = BOARD_Y + cell_center(row, ROW_BOUNDS)
            image = MARKS[mark]
            rect = image.get_rect(center=(center_x, center_y))
            screen.blit(image, rect)


# --- game loop ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    # 1) INPUT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if page == "home":
                for rect, label, image, hover_image in home_buttons:
                    if rect.collidepoint(event.pos):
                        if label == "Play vs Computer":
                            page = "difficulty"
                        else:
                            mode = "2 Players"
                            page = "game"
                            board, turn, winner = fresh_round()

            elif page == "difficulty":
                if back_rect.collidepoint(event.pos):
                    page = "home"
                else:
                    for rect, label, image, hover_image in difficulty_buttons:
                        if rect.collidepoint(event.pos):
                            mode = label
                            page = "game"
                            board, turn, winner = fresh_round()

            elif page == "game":
                if back_rect.collidepoint(event.pos):
                    if mode == "2 Players":
                        page = "home"
                    else:
                        page = "difficulty"
                elif restart_rect.collidepoint(event.pos):
                    board, turn, winner = fresh_round()
                else:
                    # human is always X in vs-computer modes
                    my_turn = mode == "2 Players" or turn == "X"
                    row, col = clicked_cell(event.pos)
                    if winner == "" and my_turn and row != -1 and board[row][col] == "":
                        board[row][col] = turn
                        winner = check_winner()
                        if turn == "X":
                            turn = "O"
                        else:
                            turn = "X"

                        if winner == "" and mode != "2 Players" and turn == "O":
                            computer_ready_at = pygame.time.get_ticks() + COMPUTER_DELAY

    # 2) UPDATE
    if page == "game" and winner == "" and mode != "2 Players" and turn == "O":
        if pygame.time.get_ticks() >= computer_ready_at:
            row, col = computer_move()
            board[row][col] = "O"
            winner = check_winner()
            turn = "X"

    # 3) DRAW
    if page == "home":
        draw_scenery()
        draw_text("TIC TAC TOE", title_font, BANNER_TEXT_COLOR, (440, 114))

        for rect, label, image, hover_image in home_buttons:
            if rect.collidepoint(mouse_pos):
                screen.blit(hover_image, rect)
            else:
                screen.blit(image, rect)
            draw_text(label, button_font, BUTTON_TEXT, rect.center)

    elif page == "difficulty":
        draw_grass()
        draw_text("Choose Difficulty", title_font, TITLE_COLOR, (WIDTH // 2, 130))
        draw_buttons(difficulty_buttons, mouse_pos)
        draw_back_button(mouse_pos)

    elif page == "game":
        draw_battlefield()
        turn_color = TURN_X_COLOR if turn == "X" else TURN_O_COLOR
        if winner == "":
            if mode == "2 Players":
                status = turn + "'s turn"
            elif turn == "X":
                status = "Your turn"
            else:
                status = "Computer is thinking..."
            draw_text(mode + "  -  " + status, button_font, turn_color, (WIDTH // 2, 50))
        elif winner == "Tie":
            draw_text("It's a tie!", title_font, TITLE_COLOR, (WIDTH // 2, 50))
        else:
            winner_color = TURN_X_COLOR if winner == "X" else TURN_O_COLOR
            draw_text(winner + " wins!", title_font, winner_color, (WIDTH // 2, 50))
        draw_grid()
        draw_marks()

        if restart_rect.collidepoint(mouse_pos):
            bar = pygame.transform.scale(bar_restart, (180, 45))
            bar_rect = bar.get_rect(center=restart_rect.center)
        else:
            bar = bar_restart
            bar_rect = restart_rect
        screen.blit(bar, bar_rect)
        draw_text("Restart", small_font, BUTTON_TEXT, restart_rect.center)

        draw_back_button(mouse_pos)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
