import pygame

# --- settings (placeholder colors/sizes, we'll style this later) ---
WIDTH = 600
HEIGHT = 600
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
BOARD_Y = 110                         # top edge
CELL = BOARD_SIZE // 3                # one cell is 150x150
LINE_WIDTH = 6

# --- scenery layout (home page) ---
TILE = 64                                  # one terrain tile is 64x64 pixels
FOAM_SIZE = 192                            # one foam frame is 192x192
FOAM_FRAMES = 16                           # the sheet holds 16 frames in a row

# where the elevated-island tiles live in the tilemap (tile coordinates):
# columns 5,6,7 are the left edge / middle / right edge of a wide island,
# column 8 is the 1-tile-wide pillar version
ROW_GRASS_TOP = 0      # grass with a bushy top edge
ROW_GRASS_MID = 1      # plain grass
ROW_GRASS_BUSH = 2     # the plateau's bushy bottom edge (pillars use row 3)
ROW_CLIFF_WALL = 4     # rocky cliff wall (for taller cliffs)
ROW_CLIFF_BASE = 5     # rocky cliff base with rounded feet

# the coastline: each island is [x, y, columns, middle rows, cliff rows]
# (x and y are pixels; islands may hang off the screen edges on purpose)
ISLANDS = [
    [-96, 32, 5, 2, 1],    # big island, cut off at the left
    [160, 32, 1, 2, 2],    # tall pillar standing in front of it
    [288, 16, 4, 2, 1],    # big island on the right
    [556, 64, 1, 1, 2],    # thin strip peeking in at the right edge
]

# --- setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

# --- images ---
tilemap = pygame.image.load("assets/tilemap.png").convert_alpha()
foam_sheet = pygame.image.load("assets/water_foam.png").convert_alpha()
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

# each button is [rectangle, label]
# home buttons are blue-button images, so the rects match the image (384x128)
home_buttons = [
    [pygame.Rect(108, 250, 384, 128), "2 Players"],
    [pygame.Rect(108, 400, 384, 128), "Play vs Computer"],
]

difficulty_buttons = [
    [pygame.Rect(150, 230, 300, 70), "Easy"],
    [pygame.Rect(150, 330, 300, 70), "Medium"],
    [pygame.Rect(150, 430, 300, 70), "Impossible"],
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


def island_rows(mid_rows, cliff_rows, narrow):
    """The tilemap row for each row of an island, from top to bottom."""
    rows = [ROW_GRASS_TOP]
    for i in range(mid_rows):
        rows.append(ROW_GRASS_MID)
    rows.append(3 if narrow else ROW_GRASS_BUSH)   # pillars use their own edge tile
    if cliff_rows == 2:
        rows.append(ROW_CLIFF_WALL)
    rows.append(ROW_CLIFF_BASE)
    return rows


def draw_scenery():
    """Draw the whole coastline: foam for every island, then their tiles."""
    # which foam frame to show right now (changes over time = animation)
    frame = (pygame.time.get_ticks() // 120) % FOAM_FRAMES
    foam = foam_sheet.subsurface((frame * FOAM_SIZE, 0, FOAM_SIZE, FOAM_SIZE))

    # 1) foam first, under every island's border tiles
    for x, y, cols, mid_rows, cliff_rows in ISLANDS:
        rows = island_rows(mid_rows, cliff_rows, cols == 1)
        for ty in range(len(rows)):
            for tx in range(cols):
                on_border = tx == 0 or ty == 0 or tx == cols - 1 or ty == len(rows) - 1
                if on_border:
                    # the foam picture is bigger than a tile, so shift it
                    # so its middle sits on the tile's middle
                    fx = x + tx * TILE - (FOAM_SIZE - TILE) // 2
                    fy = y + ty * TILE - (FOAM_SIZE - TILE) // 2
                    screen.blit(foam, (fx, fy))

    # 2) then every island's terrain tiles
    for x, y, cols, mid_rows, cliff_rows in ISLANDS:
        rows = island_rows(mid_rows, cliff_rows, cols == 1)
        for ty in range(len(rows)):
            for tx in range(cols):
                if cols == 1:
                    sx = 8            # 1-wide pillar tiles
                elif tx == 0:
                    sx = 5            # left edge
                elif tx == cols - 1:
                    sx = 7            # right edge
                else:
                    sx = 6            # middle
                tile = tilemap.subsurface((sx * TILE, rows[ty] * TILE, TILE, TILE))
                screen.blit(tile, (x + tx * TILE, y + ty * TILE))


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
                for rect, label in home_buttons:
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
        screen.fill(WATER_COLOR)
        draw_scenery()

        # title on the red ribbon
        screen.blit(ribbon_title, ((WIDTH - 512) // 2, 20))
        draw_text("TIC TAC TOE", title_font, BUTTON_TEXT, (WIDTH // 2, 76))

        # paper panel behind the mode buttons
        screen.blit(panel_paper, ((WIDTH - 512) // 2, 150))

        # mode buttons (pressed-looking when hovered)
        for rect, label in home_buttons:
            if rect.collidepoint(mouse_pos):
                screen.blit(button_blue_hover, rect)
            else:
                screen.blit(button_blue, rect)
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
