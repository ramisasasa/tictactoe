"""The pygame application: screens, input handling and rendering."""

import sys

import pygame

from . import shapes, theme as T
from .ai import DIFFICULTIES, choose_move
from .board import EMPTY, O, X, Board, other

MENU = "menu"
PLAYING = "playing"

MARK_ANIM = 0.22      # seconds for an X or O to draw itself in
WIN_ANIM = 0.40       # seconds for the winning line to sweep across
AI_DELAY = 0.45       # pause before the computer answers, so it feels human

_DIFFICULTY_BLURB = {
    "easy": "plays loose - beatable",
    "medium": "punishes real mistakes",
    "hard": "perfect play - draw at best",
}


class Button:
    def __init__(self, rect, label, value, hint=""):
        self.rect = rect
        self.label = label
        self.value = value
        self.hint = hint


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tic Tac Toe")
        self.screen = pygame.display.set_mode((T.WINDOW_W, T.WINDOW_H))
        self.canvas = pygame.Surface((T.CANVAS_W, T.CANVAS_H))
        self.clock = pygame.time.Clock()

        self.now = 0.0
        self.running = True
        self.state = MENU
        self.mouse = (0, 0)  # canvas coordinates

        self.board = Board()
        self.turn = X
        self.starter = X
        self.human_mark = X          # in one-player games
        self.difficulty = None       # None means two human players
        self.scores = {X: 0, O: 0, "draw": 0}

        self.placed_at = {}
        self.win_line = None
        self.win_mark = None
        self.win_at = 0.0
        self.round_over = False
        self.ai_ready_at = 0.0

        self.buttons = self._build_menu()

    # -- setup ---------------------------------------------------------------
    def _build_menu(self):
        entries = [(d, f"1 Player — {d.capitalize()}", _DIFFICULTY_BLURB[d]) for d in DIFFICULTIES]
        entries.append((None, "2 Players", "share the mouse"))

        buttons = []
        for i, (value, label, hint) in enumerate(entries):
            rect = pygame.Rect(
                (T.CANVAS_W - T.MENU_BUTTON_W) // 2,
                T.MENU_BUTTON_Y + i * (T.MENU_BUTTON_H + T.MENU_BUTTON_GAP),
                T.MENU_BUTTON_W,
                T.MENU_BUTTON_H,
            )
            buttons.append(Button(rect, label, value, hint))
        return buttons

    def start_match(self, difficulty):
        """Begin a fresh match (scores reset) against ``difficulty`` or a human."""
        self.difficulty = difficulty
        self.scores = {X: 0, O: 0, "draw": 0}
        self.starter = X
        self.state = PLAYING
        self.new_round(keep_starter=True)

    def new_round(self, keep_starter=False):
        if not keep_starter:
            self.starter = other(self.starter)
        self.board.reset()
        self.turn = self.starter
        self.placed_at.clear()
        self.win_line = None
        self.win_mark = None
        self.round_over = False
        self.ai_ready_at = self.now + AI_DELAY

    # -- helpers -------------------------------------------------------------
    @property
    def ai_mark(self):
        return None if self.difficulty is None else other(self.human_mark)

    def waiting_on_ai(self):
        return not self.round_over and self.turn == self.ai_mark

    def place(self, index):
        if self.round_over or not self.board.play(index, self.turn):
            return
        self.placed_at[index] = self.now

        mark, line = self.board.winner()
        if mark is not None:
            self.win_mark, self.win_line = mark, line
            self.win_at = self.now + MARK_ANIM * 0.6
            self.round_over = True
            self.scores[mark] += 1
        elif self.board.is_full():
            self.round_over = True
            self.scores["draw"] += 1
        else:
            self.turn = other(self.turn)
            self.ai_ready_at = self.now + AI_DELAY

    # -- loop ----------------------------------------------------------------
    def run(self):
        while self.running:
            self.now += self.clock.tick(T.FPS) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse = (event.pos[0] * T.SS, event.pos[1] * T.SS)
            elif event.type == pygame.KEYDOWN:
                self.on_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse = (event.pos[0] * T.SS, event.pos[1] * T.SS)
                self.on_click(self.mouse)

    def on_key(self, key):
        if key == pygame.K_q:
            self.running = False
        elif key == pygame.K_ESCAPE:
            if self.state == MENU:
                self.running = False
            else:
                self.state = MENU
        elif self.state == PLAYING:
            if key == pygame.K_m:
                self.state = MENU
            elif key in (pygame.K_SPACE, pygame.K_r):
                self.new_round(keep_starter=not self.round_over)

    def on_click(self, pos):
        if self.state == MENU:
            for button in self.buttons:
                if button.rect.collidepoint(pos):
                    self.start_match(button.value)
            return

        if self.round_over:
            self.new_round()
            return
        if self.waiting_on_ai():
            return
        index = T.cell_at(pos)
        if index is not None and self.board[index] == EMPTY:
            self.place(index)

    def update(self):
        if self.state == PLAYING and self.waiting_on_ai() and self.now >= self.ai_ready_at:
            move = choose_move(self.board, self.turn, self.difficulty)
            if move is not None:
                self.place(move)

    # -- drawing -------------------------------------------------------------
    def draw(self):
        self.canvas.fill(T.BG)
        if self.state == MENU:
            self.draw_menu()
        else:
            self.draw_game()
        pygame.transform.smoothscale(self.canvas, (T.WINDOW_W, T.WINDOW_H), self.screen)
        pygame.display.flip()

    def draw_menu(self):
        shapes.draw_text(self.canvas, "TIC TAC TOE", 46, T.TEXT,
                         center=(T.CANVAS_W // 2, T.MENU_TITLE_Y), bold=True)
        shapes.draw_text(self.canvas, "you are X and always move first", 18, T.MUTED,
                         center=(T.CANVAS_W // 2, T.MENU_SUBTITLE_Y))

        for button in self.buttons:
            hovered = button.rect.collidepoint(self.mouse)
            accent = T.O_COLOR if button.value is None else T.X_COLOR
            pygame.draw.rect(self.canvas, T.PANEL_HI if hovered else T.PANEL,
                             button.rect, border_radius=T.s(14))
            bar = pygame.Rect(button.rect.left, button.rect.top, T.s(5), button.rect.height)
            pygame.draw.rect(self.canvas, accent, bar,
                             border_top_left_radius=T.s(14), border_bottom_left_radius=T.s(14))
            shapes.draw_text(self.canvas, button.label, 21, T.TEXT if hovered else T.MUTED,
                             center=(button.rect.centerx, button.rect.centery - T.s(10)), bold=True)
            shapes.draw_text(self.canvas, button.hint, 14, T.MUTED,
                             center=(button.rect.centerx, button.rect.centery + T.s(14)))

        shapes.draw_text(self.canvas, "click a mode to start  ·  Esc quits", 15, T.MUTED,
                         center=(T.CANVAS_W // 2, T.FOOTER_Y))

    def draw_game(self):
        shapes.draw_text(self.canvas, "TIC TAC TOE", 26, T.TEXT,
                         center=(T.CANVAS_W // 2, T.TITLE_Y), bold=True)
        self.draw_scores()
        shapes.draw_text(self.canvas, self.status_text(), 20, self.status_color(),
                         center=(T.CANVAS_W // 2, T.STATUS_Y))

        shapes.draw_grid(self.canvas, T.GRID, T.GRID_WIDTH)
        self.draw_hover()
        self.draw_marks()

        if self.win_line is not None and self.now >= self.win_at:
            progress = (self.now - self.win_at) / WIN_ANIM
            shapes.draw_win_line(self.canvas, self.win_line, T.ACCENT, progress)

        hint = ("click for the next round  ·  M menu  ·  Q quit" if self.round_over
                else "SPACE restarts  ·  M menu  ·  Q quit")
        shapes.draw_text(self.canvas, hint, 15, T.MUTED, center=(T.CANVAS_W // 2, T.FOOTER_Y))

    def draw_scores(self):
        gap = T.s(16)
        centers = (
            T.CANVAS_W // 2 - T.SCORE_W - gap // 2,
            T.CANVAS_W // 2,
            T.CANVAS_W // 2 + T.SCORE_W + gap // 2,
        )
        labels = ("X", "DRAWS", "O")
        colors = (T.X_COLOR, T.MUTED, T.O_COLOR)
        values = (self.scores[X], self.scores["draw"], self.scores[O])

        for center_x, label, color, value in zip(centers, labels, colors, values):
            rect = pygame.Rect(0, 0, T.SCORE_W, T.SCORE_H)
            rect.center = (center_x, T.SCORE_Y)
            active = not self.round_over and label == self.turn
            pygame.draw.rect(self.canvas, T.PANEL_HI if active else T.PANEL, rect,
                             border_radius=T.s(12))
            if active:
                pygame.draw.rect(self.canvas, color, rect, width=T.s(2), border_radius=T.s(12))
            shapes.draw_text(self.canvas, self.score_caption(label), 13, color,
                             center=(rect.centerx, rect.centery - T.s(11)), bold=True)
            shapes.draw_text(self.canvas, str(value), 22, T.TEXT,
                             center=(rect.centerx, rect.centery + T.s(11)), bold=True)

    def score_caption(self, label):
        if self.difficulty is None or label == "DRAWS":
            return label
        return f"{label}  YOU" if label == self.human_mark else f"{label}  CPU"

    def draw_hover(self):
        if self.round_over or self.waiting_on_ai():
            return
        index = T.cell_at(self.mouse)
        if index is None or self.board[index] != EMPTY:
            return
        rect = T.cell_rect(index).inflate(-T.s(10), -T.s(10))
        pygame.draw.rect(self.canvas, T.CELL_HOVER, rect, border_radius=T.s(16))
        shapes.draw_mark(self.canvas, T.cell_rect(index), self.turn, 1.0, alpha=46)

    def draw_marks(self):
        for index in range(9):
            mark = self.board[index]
            if mark == EMPTY:
                continue
            progress = (self.now - self.placed_at.get(index, 0.0)) / MARK_ANIM
            shapes.draw_mark(self.canvas, T.cell_rect(index), mark, min(1.0, progress))

    def status_text(self):
        if self.win_mark is not None:
            if self.difficulty is None:
                return f"{self.win_mark} wins the round"
            return "you win the round" if self.win_mark == self.human_mark else "the computer wins"
        if self.round_over:
            return "a draw - nobody blinked"
        if self.waiting_on_ai():
            return "computer is thinking..."
        if self.difficulty is None:
            return f"{self.turn} to move"
        return "your move"

    def status_color(self):
        if self.win_mark is not None:
            return T.ACCENT
        if self.round_over:
            return T.MUTED
        return T.MARK_COLORS[self.turn]


def main():
    Game().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
