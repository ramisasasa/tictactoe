import pygame

# --- settings (placeholder colors/sizes, we'll style this later) ---
WIDTH = 600
HEIGHT = 600
BACKGROUND = (240, 230, 200)
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
BOARD_Y = 110                         # top edge
CELL = BOARD_SIZE // 3                # one cell is 150x150
LINE_WIDTH = 6

# --- setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont(None, 70)
button_font = pygame.font.SysFont(None, 40)
mark_font = pygame.font.SysFont(None, 150)

# which page we are on: "home", "difficulty" or "game"
page = "home"

# which mode was picked: "2 Players", "Easy", "Medium" or "Impossible"
mode = ""

# the board: 9 cells, "" means empty. Index 0 is top-left, 8 is bottom-right:
#   0 | 1 | 2
#   3 | 4 | 5
#   6 | 7 | 8
board = ["", "", "", "", "", "", "", "", ""]

# whose turn it is: "X" or "O"
turn = "X"

# each button is [rectangle, label]
home_buttons = [
    [pygame.Rect(150, 260, 300, 70), "2 Players"],
    [pygame.Rect(150, 360, 300, 70), "Play vs Computer"],
]

difficulty_buttons = [
    [pygame.Rect(150, 230, 300, 70), "Easy"],
    [pygame.Rect(150, 330, 300, 70), "Medium"],
    [pygame.Rect(150, 430, 300, 70), "Impossible"],
]


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
    """Turn a mouse position into a cell index 0-8, or -1 if off the board."""
    col = (pos[0] - BOARD_X) // CELL
    row = (pos[1] - BOARD_Y) // CELL
    if col < 0 or col > 2 or row < 0 or row > 2:
        return -1
    return row * 3 + col


def draw_marks():
    """Draw the X's and O's stored in the board list."""
    for index in range(9):
        if board[index] == "":
            continue
        row = index // 3
        col = index % 3
        center_x = BOARD_X + col * CELL + CELL // 2
        center_y = BOARD_Y + row * CELL + CELL // 2
        if board[index] == "X":
            color = X_COLOR
        else:
            color = O_COLOR
        draw_text(board[index], mark_font, color, (center_x, center_y))


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
                for rect, label in home_buttons:
                    if rect.collidepoint(event.pos):
                        if label == "Play vs Computer":
                            page = "difficulty"
                        else:
                            mode = "2 Players"
                            page = "game"
                            board = ["", "", "", "", "", "", "", "", ""]
                            turn = "X"

            elif page == "difficulty":
                for rect, label in difficulty_buttons:
                    if rect.collidepoint(event.pos):
                        mode = label
                        page = "game"
                        board = ["", "", "", "", "", "", "", "", ""]
                        turn = "X"

            elif page == "game":
                index = clicked_cell(event.pos)
                if index != -1 and board[index] == "":
                    board[index] = turn
                    if turn == "X":
                        turn = "O"
                    else:
                        turn = "X"

    # 2) UPDATE (nothing yet)

    # 3) DRAW
    screen.fill(BACKGROUND)

    if page == "home":
        draw_text("TIC TAC TOE", title_font, TITLE_COLOR, (WIDTH // 2, 150))
        draw_buttons(home_buttons, mouse_pos)

    elif page == "difficulty":
        draw_text("Choose Difficulty", title_font, TITLE_COLOR, (WIDTH // 2, 130))
        draw_buttons(difficulty_buttons, mouse_pos)

    elif page == "game":
        draw_text(mode + "  -  " + turn + "'s turn", button_font, TITLE_COLOR, (WIDTH // 2, 50))
        draw_grid()
        draw_marks()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
