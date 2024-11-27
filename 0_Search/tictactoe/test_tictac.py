from tictactoe import minimax

X = "X"
O = "O"
EMPTY = None



test_board =[[EMPTY, EMPTY, O],
            [O, X, EMPTY],
            [X, EMPTY, EMPTY]]

print(minimax(test_board))
