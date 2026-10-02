"""
Test cases for the three-jug BFS search.
AII501NAA - Activity 1, Question 2, Part B(d)

Run with:  pytest test_three_jug_search.py -v
"""

import pytest

from three_jug_search import (
    ThreeJugProblem,
    breadth_first_search,
    reconstruct_path,
)


@pytest.fixture
def problem() -> ThreeJugProblem:
    return ThreeJugProblem(goal_amount=1)


def test_initial_state_is_all_empty(problem):
    assert problem.initial == (0, 0, 0)


def test_is_goal_true_when_any_jug_has_one_gallon(problem):
    assert problem.is_goal((1, 0, 0))
    assert problem.is_goal((0, 1, 0))
    assert problem.is_goal((5, 8, 1))


def test_is_goal_false_otherwise(problem):
    assert not problem.is_goal((0, 0, 0))
    assert not problem.is_goal((12, 8, 3))


def test_actions_from_empty_state_are_fills_only(problem):
    actions = set(problem.actions((0, 0, 0)))
    assert actions == {"Fill(12-gallon)", "Fill(8-gallon)", "Fill(3-gallon)"}


def test_actions_from_full_state_are_empties_and_pours_only(problem):
    actions = set(problem.actions((12, 8, 3)))
    assert "Fill(12-gallon)" not in actions
    assert "Empty(12-gallon)" in actions
    # Pours into already-full jugs should not be offered
    assert "Pour(8-gallon -> 12-gallon)" not in actions
    assert "Pour(8-gallon -> 3-gallon)" not in actions


def test_result_fill(problem):
    assert problem.result((0, 0, 0), "Fill(12-gallon)") == (12, 0, 0)
    assert problem.result((5, 0, 0), "Fill(8-gallon)") == (5, 8, 0)


def test_result_empty(problem):
    assert problem.result((12, 0, 0), "Empty(12-gallon)") == (0, 0, 0)


def test_result_pour_partial_fill_of_target(problem):
    # Pouring 12-gallon (full) into 8-gallon (empty): target not full
    # before source empties -> source goes to 4, target fills to 8
    assert problem.result((12, 0, 0), "Pour(12-gallon -> 8-gallon)") == (4, 8, 0)


def test_result_pour_source_empties_before_target_fills(problem):
    # Pouring 3-gallon (full) into 8-gallon (has 7, room for only 1):
    # source should drain fully since 3 <= room(1)? no: room=1 < 3, so only 1 moves
    assert problem.result((0, 7, 3), "Pour(3-gallon -> 8-gallon)") == (0, 8, 2)


def test_bfs_finds_a_goal_state(problem):
    solution = breadth_first_search(problem)
    assert solution is not None
    assert problem.is_goal(solution.state)


def test_bfs_solution_is_three_actions_optimal(problem):
    """Known optimal solution length for this classic puzzle is 3 actions;
    BFS guarantees the shortest path since all action costs are uniform (1)."""
    solution = breadth_first_search(problem)
    assert solution.path_cost == 3


def test_no_two_action_solution_exists(problem):
    """Brute-force check (depth <= 2) that confirms 3 is really optimal,
    independent of the BFS implementation itself."""
    found = False
    for a1 in problem.actions(problem.initial):
        s1 = problem.result(problem.initial, a1)
        if problem.is_goal(s1):
            found = True
        for a2 in problem.actions(s1):
            s2 = problem.result(s1, a2)
            if problem.is_goal(s2):
                found = True
    assert found is False


def test_reconstructed_path_is_internally_consistent(problem):
    """Each step's state must equal applying its action to the previous
    step's state -- i.e. the parent pointers/actions tell a coherent story."""
    solution = breadth_first_search(problem)
    path = reconstruct_path(solution)

    assert path[0].state == problem.initial
    for prev, curr in zip(path, path[1:]):
        assert problem.result(prev.state, curr.action) == curr.state


def test_bfs_reports_failure_for_unreachable_goal():
    """A goal amount that no combination of these jugs can ever produce
    (e.g. 100 gallons, which exceeds every jug's capacity) must fail cleanly."""
    impossible = ThreeJugProblem(goal_amount=100)
    assert breadth_first_search(impossible) is None
