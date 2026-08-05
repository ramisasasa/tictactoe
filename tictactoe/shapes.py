"""Drawing primitives: text, round-capped strokes, and the X / O marks."""

import math

import pygame

from . import theme as T


def ease_out(t):
    """Cubic ease-out, clamped to 0..1."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp_point(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def draw_text(surface, text, size, color, center=None, topleft=None, bold=False):
    """Render ``text`` and return the rect it occupied."""
    image = T.font(size, bold).render(text, True, color)
    rect = image.get_rect()
    if center is not None:
        rect.center = center
    elif topleft is not None:
        rect.topleft = topleft
    surface.blit(image, rect)
    return rect


def stroke(surface, color, start, end, width):
    """A line with round caps, so strokes never look chopped off."""
    pygame.draw.line(surface, color, start, end, width)
    radius = width // 2
    if radius > 0:
        pygame.draw.circle(surface, color, start, radius)
        pygame.draw.circle(surface, color, end, radius)


def draw_x(surface, rect, color, width, progress=1.0):
    """Draw an X inside ``rect``; ``progress`` animates the two strokes."""
    inset = rect.width * 0.26
    left, top = rect.left + inset, rect.top + inset
    right, bottom = rect.right - inset, rect.bottom - inset

    first = ease_out(progress / 0.55)
    second = ease_out((progress - 0.45) / 0.55)

    if first > 0:
        stroke(surface, color, (left, top), lerp_point((left, top), (right, bottom), first), width)
    if second > 0:
        stroke(surface, color, (right, top), lerp_point((right, top), (left, bottom), second), width)


def draw_o(surface, rect, color, width, progress=1.0):
    """Draw an O inside ``rect``; ``progress`` sweeps the circle clockwise.

    A finished O is a single ring. A partial one is stamped from overlapping
    dots along the arc — thick polylines leave spikes at the joints.
    """
    swept = ease_out(progress)
    if swept <= 0:
        return

    center = rect.center
    radius = rect.width * 0.24
    if swept >= 0.999:
        pygame.draw.circle(surface, color, center, radius + width // 2, width)
        return

    steps = max(2, int(110 * swept))
    for i in range(steps + 1):
        angle = -math.pi / 2 + 2 * math.pi * swept * (i / steps)
        point = (center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius)
        pygame.draw.circle(surface, color, point, width // 2)


def draw_mark(surface, rect, mark, progress=1.0, alpha=255):
    """Draw ``mark`` in ``rect``, optionally translucent (used for previews)."""
    color = T.MARK_COLORS[mark]
    if alpha >= 255:
        target, offset = surface, (0, 0)
    else:
        target = pygame.Surface(rect.size, pygame.SRCALPHA)
        offset = rect.topleft
        rect = pygame.Rect(0, 0, rect.width, rect.height)

    if mark == "X":
        draw_x(target, rect, color, T.MARK_WIDTH, progress)
    else:
        draw_o(target, rect, color, T.MARK_WIDTH, progress)

    if target is not surface:
        target.set_alpha(alpha)
        surface.blit(target, offset)


def draw_grid(surface, color, width):
    """The four inner lines of the board, inset a little at both ends."""
    board = T.board_rect()
    pad = T.CELL * 0.06
    for i in (1, 2):
        x = board.left + i * T.CELL
        stroke(surface, color, (x, board.top + pad), (x, board.bottom - pad), width)
        y = board.top + i * T.CELL
        stroke(surface, color, (board.left + pad, y), (board.right - pad, y), width)


def draw_win_line(surface, line, color, progress=1.0):
    """A glowing stroke through the three winning cells."""
    start = T.cell_rect(line[0]).center
    end = T.cell_rect(line[2]).center

    # extend slightly past the outer cell centres so the line reads as a slash
    direction = (end[0] - start[0], end[1] - start[1])
    length = math.hypot(*direction) or 1
    unit = (direction[0] / length, direction[1] / length)
    overshoot = T.CELL * 0.28
    start = (start[0] - unit[0] * overshoot, start[1] - unit[1] * overshoot)
    end = (end[0] + unit[0] * overshoot, end[1] + unit[1] * overshoot)
    tip = lerp_point(start, end, ease_out(progress))

    glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    stroke(glow, (*color, 52), start, tip, int(T.WIN_WIDTH * 2.4))
    surface.blit(glow, (0, 0))
    stroke(surface, color, start, tip, T.WIN_WIDTH)
