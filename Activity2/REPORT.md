# Part 1 – Monte Carlo Tree Search for Connect Four

## 1. How the move generator works

The code is in `connect4_mcts.py` (function `mcts`). Each cycle has four steps, repeated `cycles` times, and the move visited most often at the root is returned.

| Step | What the code does |
|---|---|
| **Selection** | From the root, go down to the child with the highest utility while the node has no untried moves left and the tree height has not been reached. |
| **Expansion** | When a node still has untried moves, `expansion` (x) of them, chosen at random, are added as children. One of these new children (the one with the best objective score for the player choosing) is used for the simulation. |
| **Simulation** | At the fixed tree height (or a finished game), random legal moves are played until the game ends. |
| **Back-propagation** | The reward (+1 root player wins, 0 draw, −1 root player loses) is added to every node on the path. |

### Utility function (selection)

```
utility(child) = exploit + explore + objective
exploit   = mean reward of the child (sign flipped when the opponent is choosing)
explore   = exploration * sqrt( ln(parent visits + 1) / child visits )
objective = objective_weight * objective_score(child board)      (sign flipped when the opponent is choosing)
```

* **Playout part:** `exploit`, the mean result of the earlier playouts through the child.
* **Objective part:** `objective_score` is worked out only from the rules of the game: 1 / −1 for a win / loss, 0 for a full board, otherwise a sum of small values for centre-column pieces and for open "two" and "three" lines for each player, divided by 3 and limited to ±0.95.
* The reward and the objective score are both from the root player's point of view, so the opponent (who wants the root player to do badly) **minimises** them. That is why the sign is flipped at the opponent's nodes.

### Changes I made to the first version of the code

| Change | Why | Effect |
|---|---|---|
| Sign of the objective part flipped at the opponent's nodes (selection and the choice of the new child) | In the first version the objective was added with the same sign for both players, so at the opponent's turn it favoured moves that are good for the root player | Playing strength (see 3.6) |
| `rollout_policy` option; default `"random"`; the first version's playout (always take a win, block a loss 65 % of the time) is kept as `"tactical"` | The assignment asks for a random playout policy | Both are compared in 3.5 |
| `root_shortcut` option (default `True`) | The first version always played an immediate win/block without searching. Now it can be switched off to test the search itself | Used in the consistency test |
| Win lines worked out once instead of on every call of `winner()` | Speed: 88 % of the time was spent there | None on results (checked identical on 3000 random positions); 500 cycles went from 3.2 s to 0.84 s |

---

## 2. Experiment setup

* **Strength test** (`results/strength_*.csv`): each setting plays **20 games** (10 as player 1, 10 as player 2) against a fixed reference player: normal MCTS with `expansion=1`, `height=30`, no objective part and 150 cycles. The first two moves of every game are random so games differ. Score = (wins + ½ draws) / 20. The player under test uses 300 cycles, `expansion=2`, `height=4`, `exploration=1.2`, `objective_weight=0.25` and random playouts unless the table says otherwise.
  * **The standard error of each score is about 0.10–0.11.** Two scores must differ by roughly 0.3 before I would call the difference reliable. Most differences below are smaller, and I say so.
* **Consistency test** (`results/consistency.csv`): from five positions the search is run **20 times with seeds 0–19**, with `root_shortcut=False`, and the chosen column is counted.

| Position | Moves played | Correct column |
|---|---|---|
| empty | none | 4 (known winning first move) |
| win_in_1 | 121212 | 1 (completes four in a column) |
| must_block | 213171 | 1 (blocks the opponent's four in a column) |
| open_three | 3147 | 5 (only move that makes a double threat) |
| midgame | 4435566 | not known |

All data and the raw output are in `results/`. The consistency log lost its last line when the program stopped before saving the CSV, so I re-ran that one cell (same fixed seeds) and rebuilt the CSV from the log.

---

## 3. Results

### 3.1 Number of cycles

| Cycles | W / D / L | Score | Time (20 games) |
|---:|:---:|:---:|---:|
| 50 | 3 / 1 / 16 | 0.175 | 17 s |
| 100 | 8 / 0 / 12 | 0.400 | 23 s |
| 300 | 11 / 1 / 8 | 0.575 | 60 s |
| 600 | 15 / 0 / 5 | 0.750 | 96 s |

Consistency (20 seeds each). "Share" is how often the most common column was chosen; entropy is 0 when the same column is always chosen.

| Cycles | empty: share (entropy) | must_block correct | open_three correct | midgame: share (entropy) | ms per move (empty) |
|---:|:---:|:---:|:---:|:---:|---:|
| 50 | 0.35 (2.56) | 0.85 | 0.60 | 0.30 (2.47) | 20 |
| 200 | 0.50 (2.12) | 1.00 | 0.75 | 0.35 (2.36) | 109 |
| 300 | 0.65 (1.48) | 1.00 | 1.00 | 0.30 (2.37) | 172 |
| 1000 | 0.85 (0.75) | 1.00 | 1.00 | 0.50 (1.79) | 675 |
| 2000 | 1.00 (0.00) | 1.00 | 1.00 | 0.35 (1.96) | 1446 |

`win_in_1` was correct in 100 % of runs at every setting, even without the shortcut.

### 3.2 Utility function (300 cycles)

| Setting | W / D / L | Score |
|---|:---:|:---:|
| objective_weight = 0 (objective off) | 8 / 2 / 10 | 0.450 |
| objective_weight = 0.25 (default) | 11 / 1 / 8 | 0.575 |
| objective_weight = 1.0 | 12 / 2 / 6 | 0.650 |
| exploration = 0.3 | 12 / 2 / 6 | 0.650 |
| exploration = 1.2 (default) | 11 / 1 / 8 | 0.575 |
| exploration = 2.4 | 10 / 1 / 9 | 0.525 |

### 3.3 Expansion x (300 cycles)

| x | W / D / L | Score | Time (20 games) |
|---:|:---:|:---:|---:|
| 1 | 14 / 0 / 6 | 0.700 | 54 s |
| 2 (default) | 11 / 1 / 8 | 0.575 | 59 s |
| 3 | 11 / 1 / 8 | 0.575 | 61 s |
| 5 | 13 / 1 / 6 | 0.675 | 59 s |
| 7 | 12 / 1 / 7 | 0.625 | 77 s |

### 3.4 Tree height (300 cycles)

| Height | W / D / L | Score | Time (20 games) |
|---:|:---:|:---:|---:|
| 1 | 13 / 2 / 5 | 0.700 | 37 s |
| 2 | 13 / 2 / 5 | 0.700 | 52 s |
| 4 (default) | 11 / 1 / 8 | 0.575 | 59 s |
| 6 | 9 / 2 / 9 | 0.500 | 62 s |
| 10 | 10 / 3 / 7 | 0.575 | 63 s |

### 3.5 Playout policy (300 cycles)

| Playout | W / D / L | Score | Time (20 games) |
|---|:---:|:---:|---:|
| random (assignment) | 11 / 1 / 8 | 0.575 | 60 s |
| tactical (take a win, usually block a loss) | 13 / 2 / 5 | 0.700 | 99 s |

### 3.6 First version of the code against the corrected version
`comparison/compare_original_vs_fixed.py`, 100 cycles each, 24 games: the corrected version won 15, drew 1 and lost 8 (score 0.646). Both used default expansion/height/exploration/objective settings; the corrected side used the tactical playout, the same as the original, so the sign fix is the only difference in play.

### 3.7 Other settings, consistency at 300 cycles (20 seeds)

| Setting | empty: share | open_three correct | midgame: share |
|---|:---:|:---:|:---:|
| expansion = 1 | 0.65 | 0.90 | 0.40 |
| expansion = 2 (default) | 0.65 | 1.00 | 0.30 |
| expansion = 5 | 0.55 | 1.00 | 0.65 |
| expansion = 7 | 0.70 | 1.00 | 0.45 |
| height = 2 | 0.50 | 0.95 | 0.50 |
| height = 4 (default) | 0.65 | 1.00 | 0.30 |
| height = 6 | 0.65 | 1.00 | 0.35 |
| height = 10 | 0.65 | 1.00 | 0.35 |
| objective_weight = 0 | 0.50 | 0.95 | 0.40 |
| objective_weight = 1.0 | 0.70 | 0.95 | 0.25 |
| tactical playout | 0.60 | 1.00 | 0.40 |

---

## 4. Analysis

### Does the simulator always generate the same move?
**No, not across seeds. Yes, for the same seed.** The only random part is the playout (and the random choice of which untried moves to expand), so one seed always gives one move (`test_same_seed_gives_same_move`). Different seeds can give different moves:

* On the empty board, 50 cycles chose column 4 only 7 times out of 20 and spread the rest over six other columns. 1000 cycles chose it 17 times and 2000 cycles chose it 20 times out of 20.
* Positions with a clearly best move became reliable once there were enough cycles: `must_block` was correct every time from 200 cycles, `open_three` from 300 cycles.
* The `midgame` position never became stable (the most common move was chosen only 30–50 % of the time, even at 2000 cycles). Several moves there look nearly equally good, so which one is picked depends on the random numbers.

### What causes the differences and similarities?
1. **Playouts are noisy.** One playout is a win, draw or loss, so the average for a move has an error of about 0.5/√visits. If the best move is clearly better than the rest, the gap is larger than this error and every seed agrees. If two moves are close, the random numbers decide. More cycles reduce the error, so the entropy for `empty` falls from 2.56 to 0 as cycles go from 50 to 2000.
2. **A lucky or unlucky start gets amplified.** The search gives more visits to a child that looks good early, so a few early playouts can send one seed down a different branch. This is a possible reason why `open_three` was still wrong in 25 % of runs at 200 cycles; I did not test this directly.
3. **Choices that are not random lower the variation.** The objective score always ranks the same moves the same way. In my data the effect is small: objective_weight 0 / 0.25 / 1.0 gave `empty` shares of 0.50 / 0.65 / 0.70, but with only 20 seeds this is within what luck could produce.
4. **Tree height has no effect when the tree does not reach it.** Heights 6 and 10 gave exactly the same counts for every position at 300 cycles (for example `empty`: {3: 3, 4: 13, 5: 3, 6: 1}). The same seed uses the same random numbers, so the height limit was probably never reached. With `expansion=2` and 300 cycles the tree is wide and shallow. I did not measure node depths to check this.

### Number of cycles
This is the only effect in the strength tests that is clearly larger than the noise: the score rises from 0.175 (50 cycles) to 0.750 (600 cycles) and each step is higher than the one before. The cost grows about in proportion to cycles (20 ms to 1.4 s per move on the empty board from 50 to 2000 cycles).

### Utility function
The score goes up with the objective weight (0.45, 0.575, 0.65 for weights 0, 0.25, 1.0) and is higher with low exploration (0.65 at 0.3 against 0.525 at 2.4), but each gap is about 1 standard error or less. **I cannot say from 20 games whether the objective part or the exploration setting really matters.** The objective part is deliberately small (scores at most ±0.95 × weight), so it mostly breaks ties between children that have similar playout results.

### Expansion x
Scores are between 0.575 and 0.700 for all x with no pattern, and the differences are well inside the noise. In this program `expansion` only decides how many children are added at a time (every node eventually gets all its moves), so it is not a limit on width and a large effect would not be expected. x = 1 was the cheapest to run.

### Tree height
The scores are 0.70 at heights 1–2 and 0.50–0.575 at heights 4–10. Again the gap is within the noise, so the safest statement is that a deeper tree did not help in these tests. A possible reason is that with a fixed 300 cycles a deeper tree spreads the visits over more nodes, so each gets fewer playouts. I did not test this idea. Height 1 and 2 were also faster per game (37 s and 52 s against 59 s at height 4).

### Playout policy
The tactical playout scored 0.700 against 0.575 for random playouts, but that difference is also within the noise and it made the games 1.7 times slower (99 s against 60 s). The program uses the random playout by default because the assignment asks for it.

### Does the correction to the objective sign matter?
In 24 games the corrected version scored 0.646 against the first version (15 wins, 1 draw, 8 losses). That favours the correction, but with 24 games the standard error is about 0.10, so this is suggestive and not proof.

### Limitations
* 20 games per setting is small. Only the cycles effect is clearly larger than the noise; for the other settings the data do not show a reliable difference.
* One reference opponent and one board size.
* One setting was changed at a time, so combinations (for example x with the number of cycles) were not studied.
* The weights inside `objective_score` were chosen by hand and not tuned.
* The consistency test used 20 seeds, so shares are in steps of 0.05.

### Summary
1. More cycles give better moves and make the chosen move more repeatable. This is the clearest result.
2. The generator is deterministic for one seed. Different results across seeds come from random playouts, and they shrink when one move is clearly best or there are many cycles. They stay large in positions with several similar moves.
3. For the objective weight, exploration, expansion, tree height and playout policy, my 20-game tests did not show differences larger than the noise.
