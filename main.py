import pygame

# --- settings (placeholder colors/sizes, we'll style this later) ---
WIDTH = 900
HEIGHT = 700
BACKGROUND = (240, 230, 200)
WATER_COLOR = (71, 171, 169)
BUTTON_COLOR = (150, 110, 70)
BUTTON_HOVER = (185, 140, 95)
BUTTON_TEXT = (255, 255, 255)
TITLE_COLOR = (90, 60, 40)
GRID_COLOR = (90, 60, 40)
X_COLOR = (60, 90, 160)
O_COLOR = (170, 70, 60)
FPS = 60

# --- board layout ---
BOARD_SIZE = 450                      # the grid is 450x450 pixels
BOARD_X = (WIDTH - BOARD_SIZE) // 2   # left edge (centers it: 75)
BOARD_Y = 130                         # top edge
CELL = BOARD_SIZE // 3                # one cell is 150x150
LINE_WIDTH = 6

# --- home page scenery ---
# the background picture (736x864) is drawn at full size. BG_X centers the
# island itself (it is not centered inside its own picture), and BG_Y
# shifts the picture up so there is less sky and more water on screen.
BG_X = 66
BG_Y = -60

SPRITE = 192                               # foam / archer frames are 192x192
FOAM_FRAMES = 16                           # the foam sheet holds 16 frames
ANIM_SPEED = 120                           # ms per animation frame

# positions measured inside the background picture; drawing adds BG_X/BG_Y,
# so moving the picture moves everything with it automatically
FOAM_SPOTS = [
    (90, 645), (170, 652), (250, 658), (330, 658), (410, 658),
    (490, 658), (570, 650), (650, 640),
]
ARCHER_BLUE_SPOT = (113, 228)
ARCHER_RED_SPOT = (672, 174)

# --- the wood-framed button plates ---
PLATE_DARK = (62, 48, 60)        # dark outline
PLATE_WOOD = (217, 172, 114)     # tan frame
PLATE_WOOD_HOVER = (240, 205, 150)
PLATE_BLUE = (72, 100, 128)
PLATE_RED = (199, 75, 85)

# --- setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

# --- images ---
background = pygame.image.load("assets/background.png").convert_alpha()
# the water in the picture is painted in one exact color; turn every pixel
# of that color transparent so the animated foam can show through under it
pixels = pygame.PixelArray(background)
pixels.replace(pygame.Color(71, 171, 169, 255), pygame.Color(0, 0, 0, 0))
del pixels

foam_sheet = pygame.image.load("assets/water_foam.png").convert_alpha()


def load_archer(path, flip):
    """Cut the 8 shooting frames out of an archer sheet, scaled to fit."""
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(8):
        frame = sheet.subsurface((i * 192, 0, 192, 192))
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        frames.append(frame)
    return frames


archer_blue = load_archer("assets/archer_blue.png", False)  # faces right
archer_red = load_archer("assets/archer_red.png", True)     # flipped to face left
ribbon_title = pygame.image.load("assets/ribbon_title.png").convert_alpha()
panel_paper = pygame.image.load("assets/panel_paper.png").convert_alpha()
button_blue = pygame.image.load("assets/button_blue.png").convert_alpha()
button_blue_hover = pygame.image.load("assets/button_blue_hover.png").convert_alpha()

title_font = pygame.font.SysFont(None, 70)
button_font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 32)
mark_font = pygame.font.SysFont(None, 150)

# which page we are on: "home", "difficulty" or "game"
page = "home"

# which mode was picked: "2 Players", "Easy", "Medium" or "Impossible"
mode = ""

# the board: 3 rows of 3 cells, "" means empty.
# board[row][col] -> board[0][0] is top-left, board[2][2] is bottom-right
board = [["", "", ""],
         ["", "", ""],
         ["", "", ""]]

# whose turn it is: "X" or "O"
turn = "X"

# how the game ended: "" = still going, "X" or "O" = that player won, "Tie"
winner = ""

# home buttons are [rectangle, label, plate color]
home_buttons = [
    [pygame.Rect((WIDTH - 384) // 2, 345, 384, 80), "2 Players", PLATE_BLUE],
    [pygame.Rect((WIDTH - 384) // 2, 450, 384, 80), "Play vs Computer", PLATE_RED],
]

difficulty_buttons = [
    [pygame.Rect((WIDTH - 300) // 2, 250, 300, 70), "Easy"],
    [pygame.Rect((WIDTH - 300) // 2, 350, 300, 70), "Medium"],
    [pygame.Rect((WIDTH - 300) // 2, 450, 300, 70), "Impossible"],
]

# the restart button in the top-left corner of the game page
restart_rect = pygame.Rect(20, 20, 130, 45)


def new_board():
    """Give back a fresh empty board."""
    return [["", "", ""],
            ["", "", ""],
            ["", "", ""]]


def draw_text(text, font, color, center):
    """Draw text with its middle at the given (x, y) point."""
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    screen.blit(image, rect)


def draw_buttons(buttons, mouse_pos):
    """Draw every button in the list, highlighting the hovered one."""
    for rect, label in buttons:
        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER
        else:
            color = BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)
        draw_text(label, button_font, BUTTON_TEXT, rect.center)


def draw_grid():
    """Draw the four inner lines of the tic-tac-toe board."""
    for i in range(1, 3):
        # vertical line number i
        x = BOARD_X + i * CELL
        pygame.draw.line(screen, GRID_COLOR, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), LINE_WIDTH)
        # horizontal line number i
        y = BOARD_Y + i * CELL
        pygame.draw.line(screen, GRID_COLOR, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), LINE_WIDTH)


def clicked_cell(pos):
    """Turn a mouse position into (row, col), or (-1, -1) if off the board."""
    col = (pos[0] - BOARD_X) // CELL
    row = (pos[1] - BOARD_Y) // CELL
    if col < 0 or col > 2 or row < 0 or row > 2:
        return -1, -1
    return row, col


def draw_scenery():
    """Water color, animated foam, the island picture, then the archers."""
    screen.fill(WATER_COLOR)

    # which animation frame to show right now (changes over time = animation)
    frame = (pygame.time.get_ticks() // ANIM_SPEED) % FOAM_FRAMES

    foam = foam_sheet.subsurface(((frame % FOAM_FRAMES) * 192, 0, 192, 192))
    for cx, cy in FOAM_SPOTS:
        screen.blit(foam, (BG_X + cx - SPRITE // 2, BG_Y + cy - SPRITE // 2))

    # the island picture (its water pixels were made transparent at load,
    # so the foam peeks out from underneath the cliffs)
    screen.blit(background, (BG_X, BG_Y))

    # archers shooting at each other from the tower tops (8-frame loop)
    shot = frame % 8
    for frames, (fx, fy) in [(archer_blue, ARCHER_BLUE_SPOT), (archer_red, ARCHER_RED_SPOT)]:
        # position the frame so the archer's feet land on the spot
        screen.blit(frames[shot], (BG_X + fx - SPRITE // 2, BG_Y + fy - int(SPRITE * 0.78)))


def draw_plate(rect, color, hovered):
    """A wood-framed colored plate, like a sign lying on the grass."""
    if hovered:
        wood = PLATE_WOOD_HOVER
    else:
        wood = PLATE_WOOD
    pygame.draw.rect(screen, PLATE_DARK, rect.inflate(12, 12), border_radius=18)
    pygame.draw.rect(screen, wood, rect.inflate(6, 6), border_radius=15)
    pygame.draw.rect(screen, PLATE_DARK, rect, border_radius=12)
    pygame.draw.rect(screen, color, rect.inflate(-6, -6), border_radius=10)


def check_winner():
    """Look at the board and return "X", "O", "Tie", or "" (game still going)."""
    # 1) rows: three equal marks side by side
    for row in range(3):
        if board[row][0] != "" and board[row][0] == board[row][1] == board[row][2]:
            return board[row][0]

    # 2) columns: three equal marks stacked up
    for col in range(3):
        if board[0][col] != "" and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]

    # 3) the two diagonals
    if board[1][1] != "":
        if board[0][0] == board[1][1] == board[2][2]:
            return board[1][1]
        if board[0][2] == board[1][1] == board[2][0]:
            return board[1][1]

    # 4) any empty cell left? then the game is still going
    for row in range(3):
        for col in range(3):
            if board[row][col] == "":
                return ""

    # 5) board full and nobody won
    return "Tie"


def draw_marks():
    """Draw the X's and O's stored in the board."""
    for row in range(3):
        for col in range(3):
            mark = board[row][col]
            if mark == "":
                continue
            center_x = BOARD_X + col * CELL + CELL // 2
            center_y = BOARD_Y + row * CELL + CELL // 2
            if mark == "X":
                color = X_COLOR
            else:
                color = O_COLOR
            draw_text(mark, mark_font, color, (center_x, center_y))


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
                for rect, label, color in home_buttons:
                    if rect.collidepoint(event.pos):
                        if label == "Play vs Computer":
                            page = "difficulty"
                        else:
                            mode = "2 Players"
                            page = "game"
                            board = new_board()
                            turn = "X"
                            winner = ""

            elif page == "difficulty":
                for rect, label in difficulty_buttons:
                    if rect.collidepoint(event.pos):
                        mode = label
                        page = "game"
                        board = new_board()
                        turn = "X"
                        winner = ""

            elif page == "game":
                if restart_rect.collidepoint(event.pos):
                    board = new_board()
                    turn = "X"
                    winner = ""
                else:
                    row, col = clicked_cell(event.pos)
                    if winner == "" and row != -1 and board[row][col] == "":
                        board[row][col] = turn
                        winner = check_winner()
                        if turn == "X":
                            turn = "O"
                        else:
                            turn = "X"

    # 2) UPDATE (nothing yet)

    # 3) DRAW
    if page == "home":
        draw_scenery()

        # mode buttons: wood-framed plates (no title yet, coming later)
        for rect, label, color in home_buttons:
            draw_plate(rect, color, rect.collidepoint(mouse_pos))
            draw_text(label, button_font, BUTTON_TEXT, rect.center)

    elif page == "difficulty":
        screen.fill(BACKGROUND)
        draw_text("Choose Difficulty", title_font, TITLE_COLOR, (WIDTH // 2, 130))
        draw_buttons(difficulty_buttons, mouse_pos)

    elif page == "game":
        screen.fill(BACKGROUND)
        if winner == "":
            draw_text(mode + "  -  " + turn + "'s turn", button_font, TITLE_COLOR, (WIDTH // 2, 50))
        elif winner == "Tie":
            draw_text("It's a tie!", title_font, TITLE_COLOR, (WIDTH // 2, 50))
        else:
            draw_text(winner + " wins!", title_font, TITLE_COLOR, (WIDTH // 2, 50))
        draw_grid()
        draw_marks()

        # the restart button
        if restart_rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER
        else:
            color = BUTTON_COLOR
        pygame.draw.rect(screen, color, restart_rect, border_radius=10)
        draw_text("Restart", small_font, BUTTON_TEXT, restart_rect.center)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
