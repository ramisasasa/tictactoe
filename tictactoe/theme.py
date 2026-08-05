"""Colours, layout metrics and fonts.

Everything is drawn onto a canvas that is ``SS`` times larger than the window
and scaled down for display, which gives cheap anti-aliasing on the grid, the
marks and the winning line. All the metrics below are therefore expressed in
canvas pixels via :func:`s`.
"""

import pygame

SS = 2  # supersampling factor

WINDOW_W, WINDOW_H = 640, 800
CANVAS_W, CANVAS_H = WINDOW_W * SS, WINDOW_H * SS

FPS = 60


def s(value):
    """Convert a logical (window) measurement into canvas pixels."""
    return int(round(value * SS))


# --- layout -----------------------------------------------------------------
BOARD_SIZE = s(560)
BOARD_X = s(40)
BOARD_Y = s(196)
CELL = BOARD_SIZE // 3
GRID_WIDTH = s(5)
MARK_WIDTH = s(14)
WIN_WIDTH = s(9)

TITLE_Y = s(54)
SCORE_Y = s(120)
SCORE_H = s(56)
SCORE_W = s(168)
STATUS_Y = s(176)
FOOTER_Y = s(778)

MENU_TITLE_Y = s(150)
MENU_SUBTITLE_Y = s(200)
MENU_BUTTON_Y = s(272)
MENU_BUTTON_W = s(360)
MENU_BUTTON_H = s(64)
MENU_BUTTON_GAP = s(18)

# --- colours ----------------------------------------------------------------
BG = (17, 20, 27)
PANEL = (26, 31, 42)
PANEL_HI = (35, 42, 56)
GRID = (55, 64, 84)
TEXT = (228, 233, 242)
MUTED = (129, 141, 163)
X_COLOR = (94, 200, 229)
O_COLOR = (247, 132, 132)
ACCENT = (250, 204, 21)
CELL_HOVER = (30, 36, 49)

MARK_COLORS = {"X": X_COLOR, "O": O_COLOR}

_FONT_FAMILIES = "dejavusans,freesans,liberationsans,arial,helvetica"
_FONT_CACHE = {}


def font(size, bold=False):
    """A cached font at a logical ``size``, scaled up for the canvas."""
    key = (size, bold)
    cached = _FONT_CACHE.get(key)
    if cached is None:
        path = pygame.font.match_font(_FONT_FAMILIES, bold=bold)
        if path:
            cached = pygame.font.Font(path, s(size))
        else:  # no system fonts available (minimal containers, CI, ...)
            cached = pygame.font.Font(None, s(size + 4))
            cached.set_bold(bold)
        _FONT_CACHE[key] = cached
    return cached


def cell_rect(index):
    """The canvas rectangle of board cell ``index``."""
    row, col = divmod(index, 3)
    return pygame.Rect(BOARD_X + col * CELL, BOARD_Y + row * CELL, CELL, CELL)


def board_rect():
    return pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)


def cell_at(pos):
    """The cell index under a canvas position, or ``None``."""
    if not board_rect().collidepoint(pos):
        return None
    col = int((pos[0] - BOARD_X) // CELL)
    row = int((pos[1] - BOARD_Y) // CELL)
    if 0 <= col < 3 and 0 <= row < 3:
        return row * 3 + col
    return None
