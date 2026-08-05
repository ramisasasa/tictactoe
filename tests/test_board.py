import unittest

from tictactoe.board import EMPTY, O, X, Board, other


class TestBoard(unittest.TestCase):
    def test_starts_empty(self):
        board = Board()
        self.assertEqual(board.available(), list(range(9)))
        self.assertFalse(board.is_over())

    def test_play_rejects_occupied_cell(self):
        board = Board()
        self.assertTrue(board.play(4, X))
        self.assertFalse(board.play(4, O))
        self.assertEqual(board[4], X)

    def test_undo_frees_the_cell(self):
        board = Board()
        board.play(0, X)
        board.undo(0)
        self.assertEqual(board[0], EMPTY)

    def test_detects_row_column_and_diagonal_wins(self):
        cases = {
            (3, 4, 5): "row",
            (1, 4, 7): "column",
            (0, 4, 8): "diagonal",
            (2, 4, 6): "anti-diagonal",
        }
        for line, name in cases.items():
            board = Board()
            for index in line:
                board.play(index, X)
            with self.subTest(shape=name):
                self.assertEqual(board.winner(), (X, line))
                self.assertTrue(board.is_over())

    def test_full_board_without_winner_is_a_draw(self):
        board = Board(list("XXOOOXXOX"))
        self.assertEqual(board.winner(), (None, None))
        self.assertTrue(board.is_full())
        self.assertTrue(board.is_over())

    def test_copy_is_independent(self):
        board = Board()
        clone = board.copy()
        clone.play(0, X)
        self.assertEqual(board[0], EMPTY)

    def test_other(self):
        self.assertEqual(other(X), O)
        self.assertEqual(other(O), X)

    def test_rejects_wrong_size(self):
        with self.assertRaises(ValueError):
            Board(["X", "O"])


if __name__ == "__main__":
    unittest.main()
