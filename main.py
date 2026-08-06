import pygame

# --- settings (placeholder colors/sizes, we'll style this later) ---
WIDTH = 600
HEIGHT = 600
BACKGROUND = (240, 230, 200)
BUTTON_COLOR = (150, 110, 70)
BUTTON_HOVER = (185, 140, 95)
BUTTON_TEXT = (255, 255, 255)
TITLE_COLOR = (90, 60, 40)
FPS = 60

# --- setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont(None, 70)
button_font = pygame.font.SysFont(None, 40)

# which page we are on: "home" or "difficulty"
page = "home"

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
                            print(label + " was clicked")

            elif page == "difficulty":
                for rect, label in difficulty_buttons:
                    if rect.collidepoint(event.pos):
                        print(label + " was clicked")

    # 2) UPDATE (nothing yet)

    # 3) DRAW
    screen.fill(BACKGROUND)

    if page == "home":
        draw_text("TIC TAC TOE", title_font, TITLE_COLOR, (WIDTH // 2, 150))
        draw_buttons(home_buttons, mouse_pos)

    elif page == "difficulty":
        draw_text("Choose Difficulty", title_font, TITLE_COLOR, (WIDTH // 2, 130))
        draw_buttons(difficulty_buttons, mouse_pos)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
