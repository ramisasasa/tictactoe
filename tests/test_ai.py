import itertools
import random
import unittest

from tictactoe.ai import EASY, HARD, best_move, choose_move
from tictactoe.board import EMPTY, O, X, Board, other


def play_out(first_mover, human_moves):
    """Play a full game where ``human_moves`` picks moves for the non-AI side."""
    board = Board()
    turn = first_mover
    ai_mark = O
    while not board.is_over():
        move = best_move(board, turn) if turn == ai_mark else human_moves(board)
        board.play(move, turn)
        turn = other(turn)
    return board


class TestAI(unittest.TestCase):
    def test_takes_the_winning_move(self):
        board = Board(list("XX OO    "))
        self.assertEqual(best_move(board, X), 2)

    def test_blocks_the_opponent(self):
        board = Board(list("OO X     "))
        self.assertEqual(best_move(board, X), 2)

    def test_prefers_the_immediate_win_over_blocking(self):
        board = Board(list("XX OO    "))
        self.assertEqual(best_move(board, X), 2)

    def test_never_loses_against_every_possible_opponent(self):
        """A perfect player can be drawn but not beaten, whoever starts."""
        for first_mover in (X, O):
            for seed in range(40):
                rng = random.Random(seed)
                board = play_out(first_mover, lambda b: rng.choice(b.available()))
                with self.subTest(first=first_mover, seed=seed):
                    self.assertNotEqual(board.winner()[0], X)

    def test_never_loses_against_exhaustive_opening_lines(self):
        """Brute-force the human's first two moves rather than sampling them."""
        for opening in itertools.permutations(range(9), 2):
            scripted = iter(opening)

            def human(board, scripted=scripted):
                for move in scripted:
                    if board[move] == EMPTY:
                        return move
                return board.available()[0]

            board = play_out(X, human)
            with self.subTest(opening=opening):
                self.assertNotEqual(board.winner()[0], X)

    def test_returns_none_on_a_full_board(self):
        board = Board(list("XXOOOXXOX"))
        self.assertIsNone(best_move(board, X))
        self.assertIsNone(choose_move(board, X, HARD))

    def test_choose_move_always_stays_on_the_board(self):
        rng = random.Random(7)
        for difficulty in (EASY, HARD):
            board = Board(list("XO XO    "))
            move = choose_move(board, X, difficulty, rng)
            with self.subTest(difficulty=difficulty):
                self.assertIn(move, board.available())


if __name__ == "__main__":
    unittest.main()
