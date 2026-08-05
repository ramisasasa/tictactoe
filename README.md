# Tic Tac Toe

A tic-tac-toe game built with [pygame](https://www.pygame.org/): play a friend on
the same mouse, or take on a computer opponent that plays perfect minimax.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

Python 3.8+ and pygame 2.x.

## Playing

Pick a mode from the menu, then click a square to place your mark.

| Input | Action |
| --- | --- |
| Left click | Place a mark (or start the next round once one is finished) |
| `Space` / `R` | Restart the current round |
| `M` | Back to the menu |
| `Esc` | Back to the menu, or quit from the menu |
| `Q` | Quit |

In one-player games you are **X** and move first. Difficulty controls how often
the computer plays the perfect move: `easy` mostly wanders, `medium` punishes
real mistakes, and `hard` is unbeatable — a draw is the best you can manage.
The starting player alternates each round, and the score is kept for the match.

## Layout

```
main.py               entry point
tictactoe/board.py    the rules: moves, win detection, draws
tictactoe/ai.py       minimax with alpha-beta pruning + difficulty levels
tictactoe/theme.py    colours, layout metrics, fonts
tictactoe/shapes.py   drawing primitives (marks, grid, winning line)
tictactoe/game.py     screens, input handling, the main loop
tests/                unit tests
```

`board.py` and `ai.py` never import pygame, so the rules and the opponent can be
tested — and reused — without opening a window. Everything is rendered onto a
canvas at twice the window size and scaled down on the way to the screen, which
is what keeps the marks and grid lines smooth.

## Tests

```bash
python -m unittest discover -s tests -t .
```

The suite covers the rules, proves the hard AI cannot be beaten (it brute-forces
every opening pair of human moves), and runs the pygame layer headlessly through
a full round. Set `SDL_VIDEODRIVER=dummy` if your environment has no display.
