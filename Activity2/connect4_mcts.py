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