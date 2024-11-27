"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    plays = 0
    for row in board:
        for element in row:
            if element != EMPTY:
                plays += 1

    turn = plays % 2
    if turn == 0:
        return X
    elif turn == 1:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    pot_moves = set()
    for i, row in enumerate(board):
        for j, element in enumerate(row):
            if element == EMPTY:
                pot_moves.add((i, j))

    return pot_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    turn = player(board)
    pot_board = copy.deepcopy(board)

    # Check if action is legit
    if pot_board[action[0]][action[1]] != EMPTY or action[0] > 2 or action[0] < 0 or action[1] > 2 or action[1] < 0:
        raise ValueError("An error occurred")

    pot_board[action[0]][action[1]] = turn
    return pot_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Create all possible winning lines
    possible_lines = dict()

    possible_lines["row0"] = set()
    possible_lines["row1"] = set()
    possible_lines["row2"] = set()
    possible_lines["column0"] = set()
    possible_lines["column1"] = set()
    possible_lines["column2"] = set()
    possible_lines["diagonal1"] = set()
    possible_lines["diagonal2"] = set()

    for i in range(3):
        for j in range(3):
            if i == 0:
                possible_lines["row0"].add(board[i][j])
            if i == 1:
                possible_lines["row1"].add(board[i][j])
            if i == 2:
                possible_lines["row2"].add(board[i][j])

            if j == 0:
                possible_lines["column0"].add(board[i][j])
            elif j == 1:
                possible_lines["column1"].add(board[i][j])
            elif j == 2:
                possible_lines["column2"].add(board[i][j])

            if i == j:
                possible_lines["diagonal1"].add(board[i][j])
            if i+j == 2:
                possible_lines["diagonal2"].add(board[i][j])

    for key, value in possible_lines.items():
        if len(value) == 1 and next(iter(value)) is not None:  # fromc cs50 duck
            return value.pop()

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True

    for row in board:
        for element in row:
            if element == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)

    if win == O:
        return -1

    elif win == X:
        return 1

    else:
        return 0

# def minimax(board):
#     """
#     Returns the optimal action for the current player on the board.
#     """

#     turn = player(board)

#     if terminal(board):
#         return None

#     # if turn is X, wishes to maximeze the score
#     if turn == X:

#         max_score_X = -10000
#         best_move_X = ()


#         for actionX in actions(board):

#             boardX = result(board, actionX)

#             min_score_O = 10000
#             # find minimum score for O if X does action
#             for actionO in actions(boardX):
#                 boardO = result(boardX,actionO)
#                 value = utility(boardO)
#                 if value < min_score_O:
#                         min_score_O = value

#             if min_score_O > max_score_X:
#                     max_score_X = min_score_O
#                     best_move_X = actionX

#         return best_move_X

#      # if turn is X, wishes to maximeze the score
#     if turn == O:

#         min_score_O = 10000
#         best_move_O = ()


#         for actionO in actions(board):

#             boardO = result(board, actionO)

#             max_score_X = -10000
#             # find max score for X if O does action
#             for actionX in actions(boardO):
#                 boardX = result(boardO,actionX)
#                 value = utility(boardX)
#                 if value > max_score_X:
#                         max_score_X = value

#             if  max_score_X < min_score_O:
#                     min_score_O = max_score_X
#                     best_move_O = actionO

#         return best_move_O


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # The idea of the second function was from the cs50 duck
    def minimax_helper(board):
        if terminal(board):
            return (utility(board), None)

        turn = player(board)

        if turn == X:
            max_score_X = -10000
            move = ()
            for actionX in actions(board):
                boardX = result(board, actionX)
                value, _ = minimax_helper(boardX)
                if value > max_score_X:
                    max_score_X = value
                    move = actionX
            return max_score_X, move

        if turn == O:
            min_score_Y = 10000
            move = ()
            for actionO in actions(board):
                boardO = result(board, actionO)
                value, _ = minimax_helper(boardO)
                if value < min_score_Y:
                    min_score_Y = value
                    move = actionO
            return min_score_Y, move

    _, move = minimax_helper(board)
    return move
