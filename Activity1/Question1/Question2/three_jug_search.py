"""
Breadth-First Search -- Three-Jug Water Measuring Problem
============================================================
AII501NAA - Activity 1, Question 2 (Part B)

Jugs: 12-gallon, 8-gallon, 3-gallon, plus an unlimited faucet. Goal: measure
out exactly 1 gallon in some jug.

Implements BREADTH-FIRST-SEARCH exactly as given in AIMA (4th ed.), Figure 3.9:

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
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

State = Tuple[int, int, int]  # (12-gallon jug, 8-gallon jug, 3-gallon jug)

CAPACITIES: State = (12, 8, 3)
JUG_NAMES = ("12-gallon", "8-gallon", "3-gallon")


# ---------------------------------------------------------------------------
# Node -- AIMA Figure 3.7
# ---------------------------------------------------------------------------
@dataclass
class Node:
    state: State
    parent: Optional["Node"] = None
    action: Optional[str] = None
    path_cost: int = 0


# ---------------------------------------------------------------------------
# Problem formulation -- matches Part B, item (a)
# ---------------------------------------------------------------------------
class ThreeJugProblem:
    def __init__(self, goal_amount: int = 1):
        self.initial: State = (0, 0, 0)   # assumption: all jugs start empty
        self.goal_amount = goal_amount

    def is_goal(self, state: State) -> bool:
        """Goal test: at least one jug holds exactly goal_amount gallons."""
        return self.goal_amount in state

    def actions(self, state: State) -> Iterator[str]:
        """All applicable actions in this state: Fill, Empty, Pour(i -> j)."""
        for i in range(3):
            if state[i] < CAPACITIES[i]:
                yield f"Fill({JUG_NAMES[i]})"
            if state[i] > 0:
                yield f"Empty({JUG_NAMES[i]})"
        for i in range(3):
            for j in range(3):
                if i != j and state[i] > 0 and state[j] < CAPACITIES[j]:
                    yield f"Pour({JUG_NAMES[i]} -> {JUG_NAMES[j]})"

    def result(self, state: State, action: str) -> State:
        """Transition model: RESULT(state, action)."""
        s = list(state)
        if action.startswith("Fill"):
            i = self._jug_index(action, "Fill")
            s[i] = CAPACITIES[i]
        elif action.startswith("Empty"):
            i = self._jug_index(action, "Empty")
            s[i] = 0
        elif action.startswith("Pour"):
            i, j = self._pour_indices(action)
            amount = min(s[i], CAPACITIES[j] - s[j])
            s[i] -= amount
            s[j] += amount
        else:
            raise ValueError(f"Unknown action: {action}")
        return (s[0], s[1], s[2])

    def expand(self, node: Node) -> Iterator[Node]:
        """EXPAND(problem, node): generate child nodes via each action."""
        for action in self.actions(node.state):
            next_state = self.result(node.state, action)
            yield Node(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
            )

    @staticmethod
    def _jug_index(action: str, prefix: str) -> int:
        name = action[len(prefix) + 1 : -1]
        return JUG_NAMES.index(name)

    @staticmethod
    def _pour_indices(action: str) -> Tuple[int, int]:
        inner = action[len("Pour(") : -1]
        left, right = inner.split(" -> ")
        return JUG_NAMES.index(left), JUG_NAMES.index(right)


# ---------------------------------------------------------------------------
# BREADTH-FIRST-SEARCH -- AIMA Figure 3.9
# ---------------------------------------------------------------------------
def breadth_first_search(problem: ThreeJugProblem) -> Optional[Node]:
    node = Node(state=problem.initial)
    if problem.is_goal(node.state):
        return node

    frontier = deque([node])          # a FIFO queue, with node as an element
    reached = {problem.initial}       # reached <- {problem.INITIAL}

    while frontier:                   # while not IS-EMPTY(frontier)
        node = frontier.popleft()     # node <- POP(frontier)
        for child in problem.expand(node):
            s = child.state
            if problem.is_goal(s):    # if problem.IS-GOAL(s)
                return child
            if s not in reached:      # if s is not in reached
                reached.add(s)
                frontier.append(child)

    return None  # failure


def reconstruct_path(node: Node) -> List[Node]:
    """Follow parent pointers back to the root to recover the solution path."""
    path = []
    while node is not None:
        path.append(node)
        node = node.parent
    return list(reversed(path))


def print_solution(node: Optional[Node]) -> None:
    if node is None:
        print("No solution found.")
        return
    path = reconstruct_path(node)
    print(f"Solution found in {node.path_cost} actions:\n")
    print(f"{'Step':<6}{'Action':<28}{'State (12, 8, 3)'}")
    for i, n in enumerate(path):
        action = n.action if n.action else "(initial state)"
        print(f"{i:<6}{action:<28}{n.state}")


if __name__ == "__main__":
    problem = ThreeJugProblem(goal_amount=1)
    solution = breadth_first_search(problem)
    print_solution(solution)
