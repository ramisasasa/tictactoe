"""Game rules for tic-tac-toe.

Deliberately free of pygame imports so the rules can be tested (and reused)
without a display.
"""

EMPTY = " "
X = "X"
O = "O"

#: Every triple of cell indices that wins the game.
LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


def other(mark):
    """Return the mark belonging to the opponent of ``mark``."""
    return O if mark == X else X


class Board:
    """A 3x3 grid stored as a flat list of nine cells, indexed 0..8."""

    def __init__(self, cells=None):
        self.cells = list(cells) if cells is not None else [EMPTY] * 9
        if len(self.cells) != 9:
            raise ValueError("a board needs exactly 9 cells")

    def copy(self):
        return Board(self.cells)

    def __getitem__(self, index):
        return self.cells[index]

    def available(self):
        """Indices of the cells that are still free."""
        return [i for i, cell in enumerate(self.cells) if cell == EMPTY]

    def play(self, index, mark):
        """Place ``mark`` on a free cell. Returns True when the move was made."""
        if self.cells[index] != EMPTY:
            return False
        self.cells[index] = mark
        return True

    def undo(self, index):
        self.cells[index] = EMPTY

    def winner(self):
        """Return ``(mark, line)`` for a win, or ``(None, None)``."""
        for line in LINES:
            a, b, c = line
            if self.cells[a] != EMPTY and self.cells[a] == self.cells[b] == self.cells[c]:
                return self.cells[a], line
        return None, None

    def is_full(self):
        return EMPTY not in self.cells

    def is_over(self):
        return self.winner()[0] is not None or self.is_full()

    def reset(self):
        self.cells = [EMPTY] * 9

    def __str__(self):
        rows = ["|".join(self.cells[i:i + 3]) for i in range(0, 9, 3)]
        return "\n-+-+-\n".join(rows)
