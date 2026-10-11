import argparse
import math
import random

ROWS = 6
COLS = 7
EMPTY = 0

def new_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
