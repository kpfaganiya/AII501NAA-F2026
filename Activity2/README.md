# AII501NAA-F2026 – Activity 2

| Part | Topic | Weight | Files |
|------|-------|--------|-------|
| 1 | Monte Carlo Tree Search move generator for Connect Four | 60% | `connect4_mcts.py`, `test_connect4_mcts.py`, `run_experiments.py`, `results/`, `REPORT.md` |
| 2 | Propositional logic – satisfiability | 10% | `LOGIC_ANSWERS.md` |
| 3 | Models (model counting) | 10% | `LOGIC_ANSWERS.md` |
| 4 | Propositional logic – resolution | 20% | `LOGIC_ANSWERS.md` |

Parts 2–4 are written answers. `check_logic.py` is a small script that double-checks them.

## Files
```
Activity2/
├── README.md               this file
├── REPORT.md               Part 1 report (design, data, analysis)
├── LOGIC_ANSWERS.md        answers to Parts 2-4
├── connect4_mcts.py        Connect Four rules + MCTS move generator
├── test_connect4_mcts.py   unit tests for the game and the MCTS
├── run_experiments.py      runs the experiments, writes results/*.csv
├── check_logic.py          checks the answers to Parts 2-4
├── test_logic.py           test for the Parts 2-4 answers
├── comparison/             your first version of the code vs the corrected one (24 games)
└── results/                data used in the report (CSV + raw log)
```

## Setup
Python 3.8 or newer. No extra packages are needed.

## Run
```bash
cd Activity2

# ask the MCTS for a move on an empty board
python connect4_mcts.py
python connect4_mcts.py --cycles 1000 --expansion 3 --height 6 --seed 5

# use it from Python
python -c "
from connect4_mcts import new_board, play_move, mcts
board = new_board()
board = play_move(board, 3, 1)               # player 1 plays column 4
print(mcts(board, player=2, cycles=500, expansion=3, height=6, seed=1) + 1)
"

# experiments (about 45 minutes in total); results go to results/
python run_experiments.py
python run_experiments.py --quick            # 1 minute test run
python run_experiments.py strength           # only the strength experiments
python run_experiments.py consistency        # only the consistency experiment

# check the answers for Parts 2-4
python check_logic.py

# first version of the code vs the corrected version (about 3 minutes)
python comparison/compare_original_vs_fixed.py
```

### Settings of `mcts(...)`
| Argument | Meaning | Default |
|---|---|---|
| `cycles` | number of select/expand/simulate/back-propagate cycles | 500 |
| `expansion` | nodes expanded each time a node is expanded (x) | 2 |
| `height` | fixed tree height; a random playout starts at this depth | 4 |
| `exploration` | weight of the exploration term | 1.2 |
| `objective_weight` | weight of the rule-based objective score | 0.25 |
| `seed` | random seed (same seed = same move) | 1 |
| `rollout_policy` | `"random"` (default) or `"tactical"` (always take a win, usually block a loss) | `"random"` |
| `root_shortcut` | play an immediate win / block an immediate loss without searching | `True` |

## Tests
```bash
python -m unittest discover -p "test_*.py" -v
```
They check the board rules (all four win directions, no wrap-around, full columns), the objective function, the
playouts, the MCTS (takes a win, blocks a loss, same seed gives the same move, bad settings raise errors) and the
answers to Parts 2-4.

## Assumptions
* Board is 6 rows x 7 columns. Players are 1 (moves first) and 2. Columns are 0-6 in code and 1-7 in the printed output.
* `expansion` (x): the first time a node is reached, x randomly chosen untried moves become children. The node is
  expanded again, x more at a time, the next times it is reached, until all its legal moves are children.
* `height`: a node at depth `height` is not expanded further; a random playout is run from it.
* Rewards are +1 (root player wins), 0 (draw) and -1 (root player loses). The objective score is from the root
  player's point of view, so it is added for the root player's moves and subtracted for the opponent's moves.
* The experiment results can be repeated because all seeds are fixed. A different seed gives slightly different numbers.
* The strength experiments use 20 games per setting, so each score has a standard error of about 0.1 (see the report).
