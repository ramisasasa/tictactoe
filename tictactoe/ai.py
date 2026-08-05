"""Computer opponent: minimax with alpha-beta pruning, plus difficulty levels."""

import random

from .board import EMPTY, Board, other

EASY = "easy"
MEDIUM = "medium"
HARD = "hard"

DIFFICULTIES = (EASY, MEDIUM, HARD)

#: How often each difficulty plays the perfect move instead of a random one.
_OPTIMAL_CHANCE = {EASY: 0.15, MEDIUM: 0.65, HARD: 1.0}


def _minimax(board, mark, me, depth, alpha, beta):
    """Score the position for ``me`` with ``mark`` to move.

    Wins are worth more the sooner they happen, so the AI closes games out
    instead of dawdling once it is winning.
    """
    winner, _ = board.winner()
    if winner == me:
        return 10 - depth
    if winner is not None:
        return depth - 10
    if board.is_full():
        return 0

    if mark == me:
        best = -100
        for move in board.available():
            board.cells[move] = mark
            best = max(best, _minimax(board, other(mark), me, depth + 1, alpha, beta))
            board.cells[move] = EMPTY
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best

    best = 100
    for move in board.available():
        board.cells[move] = mark
        best = min(best, _minimax(board, other(mark), me, depth + 1, alpha, beta))
        board.cells[move] = EMPTY
        beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def best_move(board, mark, rng=random):
    """The strongest move for ``mark``; ties are broken randomly."""
    moves = board.available()
    if not moves:
        return None

    scored = []
    work = Board(board.cells)
    for move in moves:
        work.cells[move] = mark
        score = _minimax(work, other(mark), mark, 1, -100, 100)
        work.cells[move] = EMPTY
        scored.append((score, move))

    top = max(score for score, _ in scored)
    return rng.choice([move for score, move in scored if score == top])


def choose_move(board, mark, difficulty=HARD, rng=random):
    """Pick a move for ``mark`` at the requested difficulty."""
    moves = board.available()
    if not moves:
        return None
    if rng.random() < _OPTIMAL_CHANCE.get(difficulty, 1.0):
        return best_move(board, mark, rng)
    return rng.choice(moves)
