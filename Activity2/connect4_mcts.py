import argparse
import math
import random

ROWS = 6
COLS = 7
EMPTY = 0

def new_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def legal_moves(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def play_move(board, col, player):
    new = [row[:] for row in board]

    for row in range(ROWS - 1, -1, -1):
        if new[row][col] == EMPTY:
            new[row][col] = player
            return new

    raise ValueError("Column is full")

def winner(board):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(ROWS):
        for c in range(COLS):
            player = board[r][c]

            if player == EMPTY:
                continue

            for dr, dc in directions:
                cells = [
                    (r + i * dr, c + i * dc)
                    for i in range(4)
                ]

                if all(
                    0 <= rr < ROWS and 0 <= cc < COLS
                    for rr, cc in cells
                ):
                    if all(
                        board[rr][cc] == player
                        for rr, cc in cells
                    ):
                        return player

    return None

def terminal(board):
    return winner(board) is not None or not legal_moves(board)

def objective_score(board, player):
    """Rule-based evaluation from the player's perspective."""
    opponent = 3 - player
    result = winner(board)

    if result == player:
        return 1.0
    if result == opponent:
        return -1.0
    if not legal_moves(board):
        return 0.0
    
    score = 0.0

    # Centre column
    for row in range(ROWS):
        if board[row][3] == player:
            score += 0.08
        elif board[row][3] == opponent:
            score -= 0.08
    
    windows = []

    # Horizontal windows.
    for r in range(ROWS):
        for c in range(COLS - 3):
            windows.append([board[r][c + i] for i in range(4)])
    # Vertical windows.
    for r in range(ROWS - 3):
        for c in range(COLS):
            windows.append([board[r + i][c] for i in range(4)])
    
    # Diagonal windows.
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            windows.append([board[r + i][c + i] for i in range(4)])
            windows.append([board[r + 3 - i][c + i] for i in range(4)])
    
    for window in windows:
        own = window.count(player)
        opp = window.count(opponent)
        empty = window.count(EMPTY)

        if own == 3 and empty == 1:
            score += 0.30
        elif own == 2 and empty == 2:
            score += 0.06

        if opp == 3 and empty == 1:
            score -= 0.36
        elif opp == 2 and empty == 2:
            score -= 0.05

    return max(-0.95, min(0.95, score / 3.0))

def immediate_win(board, player):
    for col in legal_moves(board):
        if winner(play_move(board, col, player)) == player:
            return col
    return None

class Node:
    def __init__(self, board, player, parent=None, move=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.move = move
        self.children = []
        self.unexpanded = legal_moves(board)
        self.visits = 0
        self.value_sum = 0.0
    
    @property
    def mean_value(self):
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits

def rollout(board, player, root_player, rng):
    """Play random legal moves until the game ends."""
    board = [row[:] for row in board]

    while not terminal(board):
        # Take an immediate win when available.
        col = immediate_win(board, player)

        if col is None:
            # Sometimes block the opponent's immediate win.
            block = immediate_win(board, 3 - player)

            if block is not None and rng.random() < 0.65:
                col = block
            else:
                col = rng.choice(legal_moves(board))

        board = play_move(board, col, player)
        player = 3 - player

    result = winner(board)

    if result == root_player:
        return 1.0
    if result is None:
        return 0.0
    return -1.0

def mcts(board, player=1, cycles=500, expansion=2,
         height=4, exploration=1.2, objective_weight=0.25,
         seed=1):

    if cycles < 1 or expansion < 1 or height < 1:
        raise ValueError("Cycles, expansion and height must be positive.")

    if not legal_moves(board);
        raise ValueError("The board is full.")

    rng = random.Random(seed)

    # Always take an immediate win or block an immediate loss.
    win = immediate_win(board, player)
    if win is not None:
        return win

    block = immediate_win(board, 3 - player)
    if block is not None:
        return block

    root = Node(board, player)

    for _ in range(cycles):
        node = root
        depth = 0

        # SELECTION and EXPANSION.
        while depth < height and not terminal(node.board):

            if node.unexpanded:
                count = min(expansion, len(node.unexpanded))
                cols = rng.sample(node.unexpanded, count)

                for col in cols:
                    child_board = play_move(
                        node.board, col, node.player
                    )
                    child = Node(
                        child_board,
                        3 - node.player,
                        parent=node,
                        move=col
                    )
                    node.children.append(child)
                    node.unexpanded.remove(col)

                # Select one newly expanded child using the
                # rule-based objective function.
                node = max(
                    node.children[-count:],
                    key=lambda child:
                        objective_weight
                        * objective_score(child.board, player)
                        + rng.random() * 1e-6
                )
                depth += 1
                break

            if not node.children:
                break

            parent_visits = max(1, node.visits)

            def uct(child):
                # Rewards are measured from the root player's view.
                exploit = child.mean_value
                explore = exploration * math.sqrt(
                    math.log(parent_visits + 1)
                    / (child.visits + 1e-9)
                )
                objective = objective_weight * objective_score(
                    child.board, player
                )
                return exploit + explore + objective

            node = max(node.children, key=uct)
            depth += 1

        # SIMULATION.
        reward = rollout(
            node.board, node.player, player, rng
        )

        # BACK-PROPAGATION.
        while node is not None:
            node.visits += 1
            node.value_sum += reward
            node = node.parent

    if not root.children:
        return rng.choice(legal_moves(board))

    # Choose the move visited most often.
    best = max(
        root.children,
        key=lambda child: (
            child.visits,
            child.mean_value
            + objective_weight
            * objective_score(child.board, player)
        )
    )

    return best.move


def main():
    parser = argparse.ArgumentParser(
        description="Connect Four Monte Carlo Tree Search"
    )
    parser.add_argument("--cycles", type=int, default=500)
    parser.add_argument("--expansion", type=int, default=2)
    parser.add_argument("--height", type=int, default=4)
    parser.add_argument("--exploration", type=float, default=1.2)
    parser.add_argument("--objective-weight", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--player", type=int, choices=[1, 2], default=1)
    args = parser.parse_args()

    board = new_board()
    col = mcts(
        board,
        player=args.player,
        cycles=args.cycles,
        expansion=args.expansion,
        height=args.height,
        exploration=args.exploration,
        objective_weight=args.objective_weight,
        seed=args.seed
    )

    print("Connect Four board:")
    for row in board:
        print(" ".join("." if x == 0 else str(x) for x in row))

    print(f"Recommended column: {col + 1}")
    print(f"Search cycles: {args.cycles}")
    print(f"Expansion nodes: {args.expansion}")
    print(f"Tree height: {args.height}")
    print(f"Random seed: {args.seed}")


if __name__ == "__main__";
    main()