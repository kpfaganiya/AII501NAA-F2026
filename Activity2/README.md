# AII501NAA-F2026 - Activity 2

| Part | Topic | Weight | Where |
|------|-------|--------|-------|
| 1 | Monte Carlo Tree Search move generator for Connect Four | 60% | `connect4_mcts.py`, `test_connect4_mcts.py`, `REPORT.md` |
| 2 | Propositional logic – satisfiability | 10% | `LOGIC_ANSWERS.md` |
| 3 | Models (model counting) | 10% | `LOGIC_ANSWERS.md` |
| 4 | Propositional logic – resolution | 20% | `LOGIC_ANSWERS.md` |

Parts 2–4 are written answers only (no code).

## Files
```
Activity2/
├── README.md               this file
├── REPORT.md               Part 1 report
├── LOGIC_ANSWERS.md        answers to Parts 2, 3 and 4
├── connect4_mcts.py        Connect Four rules + MCTS move generator
└── test_connect4_mcts.py   unit tests
```

## Setup
Python 3.8 or newer. No extra packages are needed (only the standard library: `argparse`, `math`, `random`, `unittest`).

## Run
```bash
cd Activity2

# ask the MCTS for a move on an empty board (default settings)
python connect4_mcts.py

# change the settings
python connect4_mcts.py --cycles 1000 --expansion 3 --height 6 --seed 5

# play as player 2 (the empty board is still the starting position)
python connect4_mcts.py --player 2 --cycles 500
```
The program prints the board, the recommended column (numbered 1-7) and the settings used.

Command-line options:

| Option | Meaning | Default |
|---|---|---|
| `--cycles` | number of select / expand / simulate / back-propagate cycles | 500 |
| `--expansion` | number of nodes expanded at a time (x) | 2 |
| `--height` | fixed tree height; a playout starts at this depth | 4 |
| `--exploration` | weight of the exploration term | 1.2 |
| `--objective-weight` | weight of the rule-based objective score | 0.25 |
| `--seed` | random seed (the same seed gives the same move) | 1 |
| `--player` | player to move (1 or 2) | 1 |

Use it from Python:
```python
from connect4_mcts import new_board, play_move, mcts

board = new_board()
board = play_move(board, 3, 1)                  # player 1 plays column 4 (columns are 0-6 in code)
col = mcts(board, player=2, cycles=500, expansion=3, height=6, seed=1)
print(col + 1)                                  # recommended column for player 2, numbered 1-7
```

## Tests
```bash
python -m unittest test_connect4_mcts -v
```
The tests check that a new board has seven legal moves, that a piece falls to the bottom of its column, that four in a
row horizontally is detected as a win, that three in a column is not a win, and that `mcts` returns a legal column.

## How the program works
`connect4_mcts.py` contains:

* **Game rules:** `new_board`, `legal_moves`, `play_move`, `winner`, `terminal`.
* **Objective score:** `objective_score(board, player)` is a rule-based evaluation between -1 and 1 (win/loss, centre
  column, and open "two" and "three" lines for each player).
* **Search:** `mcts(...)` repeats `cycles` times:
  1. **Selection:** go down the tree choosing the child with the highest utility (while the node has no untried moves
     and the tree height has not been reached).
  2. **Expansion:** when a node still has untried moves, `expansion` of them are picked at random and added as children.
     One new child (the one with the best objective score) is used for the simulation.
  3. **Simulation:** from the node at the fixed tree height (or a finished game), moves are played until the game ends.
  4. **Back-propagation:** the reward is added to every node on the path.
* The move returned is the child of the root that was visited most often.

Utility used in selection:
```
utility = exploit + explore + objective
exploit   = mean reward of the child (sign flipped when the opponent is choosing)
explore   = exploration * sqrt( ln(parent visits + 1) / child visits )
objective = objective_weight * objective_score(child board, root player)
```

## Assumptions
* The board is 6 rows x 7 columns. Players are 1 (moves first) and 2. Columns are 0-6 in the code and 1-7 in the printed output.
* Reward is +1 if the root player wins, 0 for a draw and -1 if the root player loses.
* `expansion` (x): the first time a node is reached, x randomly chosen untried moves become children. The node is expanded
  again, x more at a time, on later visits until all its legal moves are children. So x controls how fast the tree widens.
* `height`: a node at depth `height` is not expanded; a playout is run from it.
* The playout is not purely random: a player always takes an immediate win, blocks the opponent's immediate win about
  65 % of the time, and otherwise plays a random legal move.
* Before searching, `mcts` returns an immediate winning move or an immediate blocking move if one exists.
* The search is repeatable: the same board, settings and seed always give the same move. Different seeds can give
  different moves.
* Running `connect4_mcts.py` from the command line searches the empty board once; it is not an interactive game.
