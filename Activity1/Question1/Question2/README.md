# Activity 1 - Question 2: Three-Jug Search Problem (Part B)

AII501NAA - F2026

Jugs: 12-gallon, 8-gallon, 3-gallon, plus an unlimited faucet. Goal: measure out exactly 1 gallon.

## a) States, actions, transition model

I'm representing a state as a triple `(x, y, z)` - gallons currently in the 12-, 8-, and 3-gallon jug. So `0 ≤ x ≤ 12`, `0 ≤ y ≤ 8`, `0 ≤ z ≤ 3`, which caps the whole state space at 13 × 9 × 4 = 468 possible states.

The initial state is `(0, 0, 0)` - all jugs empty. The assignment doesn't actually say this outright, so I'm stating it as an assumption rather than something given.

The goal isn't one specific state, it's a condition: any state where at least one jug has exactly 1 gallon in it (`x = 1 ∨ y = 1 ∨ z = 1`). There are a bunch of states that satisfy that - `(1,0,0)`, `(0,1,0)`, `(9,8,1)`, and so on.

Actions available depend on the state: `Fill(J)` fills jug J from the faucet (only if it isn't already full), `Empty(J)` dumps jug J out (only if it isn't already empty), and `Pour(i → j)` pours from jug i into jug j until either i runs out or j fills up, whichever happens first (only applicable if i has something in it and j has room).

For the transition model: `Fill(J)` just sets that jug to its capacity. `Empty(J)` sets it to 0. `Pour(i → j)` computes `amount = min(contents[i], capacity[j] - contents[j])`, then subtracts that from i and adds it to j. Every action costs 1, so the cheapest solution is just whichever path uses the fewest actions.

## b) Does a heuristic make sense here?

Sort of, but it's not a great one, honestly. You could define something like `h(state) = min(|x-1|, |y-1|, |z-1|)` - the smallest distance from any jug's current amount to 1 gallon. It does hit 0 right at the goal, which is the basic shape you want.

The problem is that a single pour can swing a jug's contents by anywhere from 1 gallon up to a whole jug's capacity - it's not like each action only moves you 1 gallon closer or further. So a state that looks "close" under this heuristic might actually be several moves away, and a state that looks "far" might be one move away (like emptying a full jug). It doesn't track the real number of remaining actions very well. Given how small the whole state space is (under 500 states), it's not really worth the trouble of an informed search here anyway - which is probably why the assignment just asks for plain BFS instead of something like A*.

## c) Is any search algorithm guaranteed to find a goal?

Not any algorithm, no - it really depends on how it handles states it's already seen.

The state graph has cycles in it. For example, `Fill(12)` followed by `Empty(12)` just puts you back where you started. If you ran a plain depth-first search that doesn't track which states it's already visited (tree-search, not graph-search), it could get stuck looping through a cycle like that forever, even though a solution exists somewhere in the graph.

But if you do track visited states - which is what graph-search does, and what BFS does by keeping a `reached` set - then you can't ever revisit the same state twice. Combined with the fact that the state space is finite, and that a solution is actually reachable here (this is a known number theory result - since gcd(3,8) = 1, you can measure any integer amount from 0 to 8 using just the 8 and 3 gallon jugs), that guarantees the search will eventually hit the goal.

So the real answer is that it's not about the algorithm being BFS or DFS specifically, it's about whether it avoids re-exploring states it's already seen. BFS as implemented in part (d), using a `reached` set, is guaranteed to find the goal because the space is finite and a solution exists.

## d) Implementation

`three_jug_search.py` implements this pretty much directly from the book's BFS pseudocode (Figure 3.9):

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

`ThreeJugProblem` holds the problem formulation - `initial`, `is_goal()`, `actions()`, `result()`, and `expand()` which ties `actions()` and `result()` together to generate child nodes. `breadth_first_search()` is the actual search loop, using a `deque` as the FIFO frontier and a plain set for `reached`.

Running it finds the known 3-move solution:

```
Step  Action                      State (12, 8, 3)
0     (initial state)             (0, 0, 0)
1     Fill(12-gallon)             (12, 0, 0)
2     Pour(12-gallon -> 8-gallon) (4, 8, 0)
3     Pour(12-gallon -> 3-gallon) (1, 8, 3)
```

## Assumptions

Initial state is all jugs empty - not stated directly in the problem, so I'm assuming it. "Measure exactly one gallon" is being read as any single jug holding exactly 1 gallon at some point, not all three jugs simultaneously or anything like that. Pours go until empty-or-full rather than some arbitrary partial amount, since there's no indication the jugs have volume markings for measuring partial pours. And anything emptied onto the ground is just gone - it doesn't count toward any jug.

## Project structure

```
Activity1_PartB/
├── README.md
├── three_jug_search.py
└── test_three_jug_search.py
```

## Setup

Needs Python 3.10+ and pytest.

```bash
pip install pytest
```

## Running it

```bash
python3 three_jug_search.py
```

Prints the shortest sequence of actions from `(0,0,0)` to a state with 1 gallon in some jug. To try a different target amount, change `ThreeJugProblem(goal_amount=1)` in the `__main__` block.

## Testing

```bash
pytest test_three_jug_search.py -v
```

14 tests, covering the problem formulation itself (initial state, goal test, which actions are valid in a given state, the transition model for each action type including partial-pour edge cases), that BFS actually finds a goal, that the solution really is optimal at 3 moves (double-checked with a separate brute-force check, not just trusting the BFS code itself), that the solution path is internally consistent (each step's state really does follow from applying that step's action to the previous state), and that it fails cleanly for a target amount that isn't reachable. All 14 pass.
