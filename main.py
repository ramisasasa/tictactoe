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

# each button is [rectangle, label]
buttons = [
    [pygame.Rect(150, 260, 300, 70), "2 Players"],
    [pygame.Rect(150, 360, 300, 70), "Play vs Computer"],
]


def draw_text(text, font, color, center):
    """Draw text with its middle at the given (x, y) point."""
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
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
            for rect, label in buttons:
                if rect.collidepoint(event.pos):
                    print(label + " was clicked")

    # 2) UPDATE (nothing yet)

    # 3) DRAW
    screen.fill(BACKGROUND)
    draw_text("TIC TAC TOE", title_font, TITLE_COLOR, (WIDTH // 2, 150))

    for rect, label in buttons:
        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER
        else:
            color = BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)
        draw_text(label, button_font, BUTTON_TEXT, rect.center)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
