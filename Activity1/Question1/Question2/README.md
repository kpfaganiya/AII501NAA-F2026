# Activity 1 — Question 2: Three-Jug Search Problem (Part B)

AII501NAA - F2026

Jugs: 12-gallon, 8-gallon, 3-gallon, plus an unlimited faucet. Goal: measure out exactly 1 gallon.

## a) States, Actions, Transition Model

**State:** a triple `(x, y, z)` — gallons currently in the 12-, 8-, and 3-gallon jug respectively, with `0 ≤ x ≤ 12`, `0 ≤ y ≤ 8`, `0 ≤ z ≤ 3`. This gives a finite state space of at most 13 × 9 × 4 = 468 states.

**Initial state:** `(0, 0, 0)` — all jugs start empty. *(Not stated explicitly in the problem; stated here as an assumption.)*

**Goal state(s):** any state where at least one jug holds exactly 1 gallon: `x = 1 ∨ y = 1 ∨ z = 1`. This is a goal *test*, not a single target state — many triples satisfy it (e.g. `(1,0,0)`, `(0,1,0)`, `(9,8,1)`, …).

**Actions** (applicable depending on the current state):
- `Fill(J)` — fill jug *J* completely from the faucet (applicable if *J* isn't already full)
- `Empty(J)` — empty jug *J* onto the ground (applicable if *J* isn't already empty)
- `Pour(i → j)` — pour from jug *i* into jug *j* until *i* is empty or *j* is full, whichever comes first (applicable if *i* has water and *j* has room)

**Transition model** `RESULT(state, action)`:
- `Fill(J)`: `contents[J] ← capacity[J]`; other jugs unchanged.
- `Empty(J)`: `contents[J] ← 0`; other jugs unchanged.
- `Pour(i → j)`: `amount ← min(contents[i], capacity[j] − contents[j])`; then `contents[i] -= amount`, `contents[j] += amount`; the third jug is unchanged.

Every action has cost 1 (one "move"), so the cheapest solution is simply the fewest number of actions.

## b) Does a Heuristic Make Sense?

A heuristic *can* be defined, but it's a weak one, which is part of why this problem is well-suited to plain BFS rather than needing an informed search like A*.

**Informal heuristic:** `h(state) = min(|x − 1|, |y − 1|, |z − 1|)` — the smallest distance (in gallons) from any jug's current contents to the goal amount of 1. It's 0 exactly at a goal state, which is the right shape for a heuristic.

Why it's weak: a single action (especially a `Pour`) can change a jug's contents by any amount up to a whole jug's capacity, not by one gallon at a time. So a state that looks "close" under this heuristic (say, 2 gallons away) might actually be reachable in one action, while a state that looks "far" (say, 8 gallons away) might also be one action away (e.g. emptying a full jug). The heuristic doesn't reliably track the true number of *actions* remaining, so it gives only a loose signal rather than a tight, admissible estimate. Given that the full state space is small (at most 468 states), the benefit an informed search would get from this heuristic is marginal — which is consistent with the assignment asking specifically for plain BFS here.

## c) Is Any Search Algorithm Guaranteed to Reach a Goal State?

**No — not *any* search algorithm.** It depends on whether the algorithm is complete, and completeness here depends on how repeated states are handled.

- The state graph contains **cycles**: e.g. `Fill(12)` then `Empty(12)` returns to the exact same state. A **tree-search** version of depth-first search, which doesn't track previously visited states, can loop forever re-exploring the same cycle and is therefore **not guaranteed** to terminate, let alone find the goal — even though a solution exists.
- A **graph-search** version of DFS, or BFS (which tracks `reached` states, as in Figure 3.9), cannot revisit a state twice. Combined with the fact that the state space is finite (≤ 468 states) and a solution is known to exist (a classic number-theory result: since gcd(3, 8) = 1, every integer amount from 0 up to 8 — including 1 — is reachable using just the 8- and 3-gallon jugs), any **complete** search strategy is guaranteed to reach a goal state in a finite number of steps.

So the honest answer is: completeness is a property of the *algorithm's handling of repeated states*, not of "any search algorithm" in general. **BFS with graph-search (as implemented in part d) is guaranteed to reach the goal**, because the space is finite, a goal is reachable from the initial state, and `reached` prevents infinite loops.

## d) Implementation

Implemented in `three_jug_search.py` as a direct translation of **AIMA Figure 3.9**:

```
function BREADTH-FIRST-SEARCH(problem) returns a solution node, or failure
    node <- NODE(problem.INITIAL)
    if problem.IS-GOAL(node.STATE) then return node
    frontier <- a FIFO queue, with node as an element
    reached <- {problem.INITIAL}
    while not IS-EMPTY(frontier) do
        node <- POP(frontier)
        for each child in EXPAND(problem, node) do
            s <- child.STATE
            if problem.IS-GOAL(s) then return child
            if s is not in reached then
                add s to reached
                add child to frontier
    return failure
```

| Book concept | Code |
|---|---|
| `NODE`, parent/action/path-cost | `Node` dataclass |
| `problem.INITIAL` | `ThreeJugProblem.initial` = `(0, 0, 0)` |
| `problem.IS-GOAL` | `ThreeJugProblem.is_goal()` |
| `EXPAND(problem, node)` | `ThreeJugProblem.expand()`, using `actions()` + `result()` |
| FIFO `frontier` | `collections.deque`, `popleft()`/`append()` |
| `reached` | a Python `set` of visited states |

Running it on the defined problem finds the known-optimal 3-action solution:

```
Step  Action                      State (12, 8, 3)
0     (initial state)             (0, 0, 0)
1     Fill(12-gallon)             (12, 0, 0)
2     Pour(12-gallon -> 8-gallon) (4, 8, 0)
3     Pour(12-gallon -> 3-gallon) (1, 8, 3)
```

## Assumptions

- Initial state is all jugs empty `(0, 0, 0)` — not stated explicitly in the problem, so stated here outright.
- "Measure out exactly one gallon" is interpreted as **any one jug** containing exactly 1 gallon at some point (not all three simultaneously, and not poured onto the ground separately).
- Pours are "until empty or full" (standard water-jug-puzzle rule) — partial, arbitrary-amount pours are not modeled as separate actions, since the problem doesn't suggest the jugs have volume markings.
- Water poured "onto the ground" (per `Empty`) is lost — it does not count toward any jug.

## Project Structure

```
Activity1_PartB/
├── README.md                     # this file
├── three_jug_search.py           # problem formulation + BFS (Fig. 3.9)
└── test_three_jug_search.py      # pytest test suite
```

## Setup

Requires Python 3.10+ and `pytest`.

```bash
pip install pytest
```

## Execution

```bash
python3 three_jug_search.py
```

Prints the shortest action sequence (and resulting states) from `(0,0,0)` to a state with exactly 1 gallon in some jug.

To solve for a different target amount, edit `ThreeJugProblem(goal_amount=1)` in the `__main__` block.

## Testing

```bash
pytest test_three_jug_search.py -v
```

14 tests cover: the problem formulation (initial state, goal test, action generation, transition model for `Fill`/`Empty`/`Pour`, including partial-pour edge cases), that BFS finds a goal state, that the solution is confirmed optimal at 3 actions (cross-checked independently by brute force), that the reconstructed solution path is internally consistent (each state really does follow from applying its action to the previous state), and that BFS correctly reports failure for an unreachable goal amount. All 14 currently pass.
