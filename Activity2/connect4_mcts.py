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