# Part 1 – Monte Carlo Tree Search for Connect Four

## 1. How the move generator works

The code is in `connect4_mcts.py` (function `mcts`). It repeats four steps `cycles` times and then returns the child of the root that was visited most often.

| Step | What the code does |
|---|---|
| **Selection** | From the root, go down to the child with the highest utility, as long as the node has no untried moves left and the tree height has not been reached. |
| **Expansion** | When a node still has untried moves, `expansion` (x) of them, chosen at random, are added as children. Of these new children, the one with the best objective score is used for the simulation. A node is expanded again on later visits, x moves at a time, until all its legal moves are children. |
| **Simulation** | From the node at the fixed tree height (or a finished game), moves are played until the game ends. A player always takes an immediate win, blocks the opponent's immediate win 65 % of the time, and otherwise plays a random legal move. |
| **Back-propagation** | The reward (+1 root player wins, 0 draw, −1 root player loses) is added to every node on the path. |

Before searching, `mcts` returns an immediate winning move, or an immediate blocking move, if there is one. For example, a 1-cycle search on the positions `121212` and `213171` returns column 1 straight away, which is correct in both.

### Utility function (selection)

```
utility(child) = exploit + explore + objective
exploit   = mean reward of the child (sign flipped when the opponent is choosing)
explore   = exploration * sqrt( ln(parent visits + 1) / child visits )
objective = objective_weight * objective_score(child board, root player)
```

* **Playout part:** `exploit`, the mean result of the earlier playouts through the child.
* **Objective part:** `objective_score` uses only the rules of the game. It gives 1 / −1 for a win / loss and 0 for a full board. Otherwise it adds +0.08 for each of my pieces in the centre column (−0.08 for each opponent piece) and counts lines of four cells: +0.30 for three of mine plus an empty cell, +0.06 for two of mine plus two empty cells, −0.36 for three of the opponent's plus an empty cell and −0.05 for two of the opponent's with two empty cells. The sum is divided by 3 and limited to ±0.95.
* The objective part is always calculated from the root player's point of view and added with the same sign for both players (see the limitations).

---

## 2. Experiment setup

* **Strength test**: each setting plays **20 games** (10 as player 1, 10 as player 2) against a fixed reference player: normal MCTS with `expansion=1`, `height=30`, no objective part and 150 cycles. The first two moves of every game are random so games differ. Score = (wins + ½ draws) / 20. The tested player uses 300 cycles, `expansion=2`, `height=4`, `exploration=1.2` and `objective_weight=0.25` (the default of the program, except cycles) unless a table says otherwise.
  * **The standard error of each score is about 0.10–0.11**, so two scores must differ by roughly 0.3 before I would call the difference reliable. Most of the differences below are smaller than that, and I say so each time.
* **Consistency test**: from three positions the search is run **20 times with seeds 0–19**, and the chosen column is counted. The positions where a player can win or must block at once were left out because `mcts` answers them without searching.

| Position | Moves played | Correct column |
|---|---|---|
| empty | none | 4 (known winning first move) |
| open_three | 3147 | 5 (only move that makes a double threat) |
| midgame | 4435566 | not known |

* **Speed-up used for the experiments.** `winner()` in `connect4_mcts.py` takes most of the running time because it builds the list of lines on every call. The experiment program replaces it, while it runs, by a version that returns exactly the same answer but builds the list once. The program first checks both versions on 2000 random games (they agreed in every position) and stops if they ever differ. `connect4_mcts.py` itself is not changed. Because of this, the times in the tables are about 4 times shorter than with the file as it is (500 cycles on the empty board took 3.2 s before and 0.84 s with the faster version).

---

## 3. Results

### 3.1 Number of cycles

| Cycles | W / D / L | Score | Time (20 games) |
|---:|:---:|:---:|---:|
| 50 | 5 / 1 / 14 | 0.275 | 69 s |
| 100 | 5 / 0 / 15 | 0.250 | 86 s |
| 300 | 11 / 1 / 8 | 0.575 | 170 s |
| 600 | 14 / 0 / 6 | 0.700 | 277 s |

Consistency (20 seeds). "Share" is how often the most common column was chosen; entropy is 0 when the same column is always chosen.

| Cycles | empty: share (entropy) | open_three correct | midgame: share (entropy) | ms per move (empty) |
|---:|:---:|:---:|:---:|---:|
| 50 | 0.40 (2.01) | 0.85 | 0.35 (2.28) | 121 |
| 200 | 0.65 (1.58) | 1.00 | 0.50 (1.98) | 492 |
| 300 | 0.75 (1.15) | 1.00 | 0.50 (1.98) | 755 |
| 1000 | 0.80 (0.92) | 1.00 | 0.65 (1.58) | 2637 |

### 3.2 Utility function (300 cycles)

| Setting | W / D / L | Score |
|---|:---:|:---:|
| objective_weight = 0 (objective off) | 12 / 2 / 6 | 0.650 |
| objective_weight = 0.25 (default) | 11 / 1 / 8 | 0.575 |
| objective_weight = 1.0 | 14 / 0 / 6 | 0.700 |
| exploration = 0.3 | 6 / 1 / 13 | 0.325 |
| exploration = 1.2 (default) | 11 / 1 / 8 | 0.575 |
| exploration = 2.4 | 7 / 3 / 10 | 0.425 |

Consistency (300 cycles):

| objective_weight | empty: share (entropy) | midgame: share (entropy) |
|---:|:---:|:---:|
| 0 | 0.45 (2.12) | 0.40 (1.94) |
| 0.25 (default) | 0.75 (1.15) | 0.50 (1.98) |
| 1.0 | 0.80 (1.02) | 0.50 (1.65) |

`open_three` was correct in 20 of 20 runs for all three.

### 3.3 Expansion x (300 cycles)

| x | W / D / L | Score | Time (20 games) | empty: share | midgame: share |
|---:|:---:|:---:|---:|:---:|:---:|
| 1 | 14 / 0 / 6 | 0.700 | 163 s | 0.65 | 0.40 |
| 2 (default) | 11 / 1 / 8 | 0.575 | 161 s | 0.75 | 0.50 |
| 5 | 8 / 1 / 11 | 0.425 | 174 s | – | – |
| 7 | 12 / 1 / 7 | 0.625 | 176 s | 0.50 | 0.50 |

### 3.4 Tree height (300 cycles)

| Height | W / D / L | Score | Time (20 games) | empty: share (entropy) | midgame: share |
|---:|:---:|:---:|---:|:---:|:---:|
| 1 | 11 / 0 / 9 | 0.550 | 153 s | – | – |
| 2 | 10 / 1 / 9 | 0.525 | 180 s | 0.60 (1.49) | 0.30 |
| 4 (default) | 11 / 1 / 8 | 0.575 | 162 s | 0.75 (1.15) | 0.50 |
| 10 | 12 / 0 / 8 | 0.600 | 156 s | 0.85 (0.75) | 0.50 |

`open_three` was correct in 20 of 20 runs for x = 1, 7 and for heights 2, 10.

---

## 4. Analysis

### Does the simulator always generate the same move?
**No, not across seeds. Yes, for the same seed.** The playouts and the choice of which moves to expand use a random number generator, so one seed always gives one move but different seeds can give different moves.

* On the empty board, 50 cycles chose column 4 in 8 of 20 runs (five different columns appeared in total). 300 cycles chose it 15 times and 1000 cycles 16 times.
* `open_three` was found every time from 200 cycles, and was found 17 times out of 20 at 50 cycles.
* The `midgame` position was never stable: the most common move was chosen only 35 % to 65 % of the time. Several moves seem nearly equally good there, so the random numbers decide.

### What causes the differences and the similarities?
1. **Playouts are noisy.** One playout is a win, draw or loss, so the average for a move has an error of about 0.5/√visits. If the best move is clearly better, this error is too small to matter and all seeds agree (`open_three` from 200 cycles). If two moves are close, the random numbers decide (`midgame`). More cycles reduce the error: the entropy for the empty board goes from 2.01 at 50 cycles to 0.92 at 1000.
2. **Early luck is amplified.** Selection gives more visits to a child that looks good early, so a few early playouts can send one seed down a different branch. This is a possible reason why the empty board still gave a different column in 20 % of runs at 1000 cycles; I did not test it directly.
3. **The objective part is not random, so it makes moves more repeatable.** With the objective switched off, column 4 was chosen on the empty board 9 times out of 20; with weight 0.25 it was chosen 15 times and with weight 1.0, 16 times. This is the clearest effect of the objective part in my data, but it is one position with 20 seeds.
4. **A deeper tree was more repeatable on the empty board** (share 0.60, 0.75, 0.85 for heights 2, 4, 10) but not on `midgame` (0.30, 0.50, 0.50). I only have one position showing this trend, so it may be luck.

### Number of cycles
The score rises from 0.25–0.275 (50 and 100 cycles) to 0.575 (300) and 0.700 (600). The gap between 50 and 600 cycles (about 0.4) is the one strength result that is clearly larger than the noise. The cost grows about in proportion to the cycles.

### Utility function
* **Objective weight:** the scores are 0.65, 0.575 and 0.70 for weights 0, 0.25 and 1.0, so the objective part did not make a measurable difference to strength. The consistency data above show it does change how repeatable the chosen move is.
* **Exploration:** the default (1.2) scored 0.575, with 0.325 for 0.3 and 0.425 for 2.4. The gap between 0.3 and 1.2 is about 1.6 standard errors, so too little exploration may hurt but 20 games cannot settle it.

### Expansion x
The scores (0.70, 0.575, 0.425 and 0.625 for x = 1, 2, 5, 7) follow no pattern, and the differences are within the noise. In this program `expansion` only decides how many children are added at a time, because every node eventually gets all its moves, so I would not expect a large effect.

### Tree height
The scores 0.55, 0.525, 0.575 and 0.60 for heights 1, 2, 4, 10 are all within the noise. The height did not matter for strength at 300 cycles. Height 1 means playouts start straight after the first move, so even that simple version scored about the same as the full tree in these 20 games.

### Limitations
* 20 games per setting is small: only the cycles effect is clearly larger than the noise. For the other settings the data do not show a reliable difference.
* One reference opponent and one board size. The consistency test uses only three positions.
* Settings were changed one at a time, so combinations (for example x and cycles) were not studied.
* **The objective part has the same sign for both players.** `objective_score` is from the root player's point of view, but it is added in the same way when the opponent is choosing, where it rewards moves that are good for the root player. A version with the sign flipped at the opponent's nodes scored 0.646 against this version in a separate test (24 games, 100 cycles each; 15 wins, 1 draw, 8 losses). With 24 games that is suggestive, not proof. I kept the original rule in the experiments above.
* The playout is not purely random (it takes wins and often blocks), and `mcts` answers wins and forced blocks without searching. The assignment describes a random playout.
* The weights inside `objective_score` were chosen by hand and not tuned.

### Summary
1. More cycles give stronger and more repeatable moves. This is the clearest result.
2. The generator always gives the same move for the same seed. Different results across seeds come from random playouts, and they fade when one move is clearly best or there are many cycles. They stay large where several moves are similar.
3. A larger objective weight made the move on the empty board more repeatable. For strength, I could not show an effect of the objective weight, the expansion size or the tree height with 20 games.
