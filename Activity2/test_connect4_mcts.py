
import unittest
from connect4_mcts import (
    new_board,
    legal_moves,
    play_move,
    winner,
    mcts,
)


class ConnectFourTests(unittest.TestCase):

    def test_initial_board_has_seven_moves(self):
        board = new_board()
        self.assertEqual(legal_moves(board), list(range(7)))

    def test_move_falls_to_bottom(self):
        board = play_move(new_board(), 3, 1)
        self.assertEqual(board[5][3], 1)

    def test_horizontal_win(self):
        board = new_board()
        for col in range(4):
            board = play_move(board, col, 1)
        self.assertEqual(winner(board), 1)

    
    def test_vertical_win(self):
        board = new_board()

        for player in [1, 2, 1, 2, 1, 2]:
            board = play_move(board, 0, player)

        self.assertIsNone(winner(board))


    def test_mcts_returns_legal_column(self):
        board = new_board()
        move = mcts(board, cycles=100, seed=10)
        self.assertIn(move, legal_moves(board))


if __name__ == "__main__":
    unittest.main()
