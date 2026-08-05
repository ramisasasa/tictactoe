"""Headless smoke tests for the pygame layer (no window is opened)."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from tictactoe import theme as T  # noqa: E402
from tictactoe.board import O, X  # noqa: E402
from tictactoe.game import MENU, PLAYING, AI_DELAY, Game  # noqa: E402


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def advance(self, seconds):
        self.game.now += seconds
        self.game.update()

    def test_menu_button_starts_a_match(self):
        button = self.game.buttons[0]
        self.game.on_click(button.rect.center)
        self.assertEqual(self.game.state, PLAYING)
        self.assertEqual(self.game.difficulty, button.value)

    def test_clicking_a_cell_places_a_mark_and_the_ai_replies(self):
        self.game.start_match("hard")
        self.game.on_click(T.cell_rect(0).center)
        self.assertEqual(self.game.board[0], X)
        self.assertEqual(self.game.turn, O)

        self.advance(AI_DELAY + 0.01)
        self.assertEqual(len(self.game.board.available()), 7)

    def test_occupied_cells_ignore_further_clicks(self):
        self.game.start_match(None)
        self.game.on_click(T.cell_rect(4).center)
        self.game.on_click(T.cell_rect(4).center)
        self.assertEqual(self.game.board[4], X)
        self.assertEqual(self.game.turn, O)

    def test_two_player_mode_alternates_turns(self):
        self.game.start_match(None)
        for index, mark in ((0, X), (1, O), (3, X)):
            self.game.on_click(T.cell_rect(index).center)
            self.assertEqual(self.game.board[index], mark)

    def test_win_updates_the_score_and_ends_the_round(self):
        self.game.start_match(None)
        for index in (0, 3, 1, 4, 2):  # X takes the top row
            self.game.on_click(T.cell_rect(index).center)
        self.assertTrue(self.game.round_over)
        self.assertEqual(self.game.win_mark, X)
        self.assertEqual(self.game.win_line, (0, 1, 2))
        self.assertEqual(self.game.scores[X], 1)

    def test_next_round_clears_the_board_and_swaps_the_starter(self):
        self.game.start_match(None)
        self.game.on_click(T.cell_rect(0).center)
        self.game.new_round()
        self.assertEqual(self.game.board.available(), list(range(9)))
        self.assertEqual(self.game.turn, O)
        self.assertFalse(self.game.round_over)

    def test_escape_returns_to_the_menu(self):
        self.game.start_match(None)
        self.game.on_key(pygame.K_ESCAPE)
        self.assertEqual(self.game.state, MENU)

    def test_drawing_every_screen_works(self):
        self.game.draw()  # menu
        self.game.start_match(None)
        self.game.mouse = T.cell_rect(8).center
        self.game.draw()  # empty board with a hover preview
        for index in (0, 3, 1, 4, 2):
            self.game.on_click(T.cell_rect(index).center)
        self.advance(1.0)
        self.game.draw()  # finished round, winning line


if __name__ == "__main__":
    unittest.main()
