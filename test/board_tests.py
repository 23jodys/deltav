
import board
import tempfile
import logging

default_formatter = logging.Formatter(\
    "%(asctime)s:%(levelname)s:%(name)s:%(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(default_formatter)

# error_handler = logging.FileHandler(runtime.get("Locations","log"), "a")
# error_handler.setLevel(logging.DEBUG)
# error_handler.setFormatter(default_formatter)

# rootlogger = logging.getLogger()
# rootlogger.addHandler(console_handler)
# rootlogger.addHandler(error_handler)
from nose.tools import nottest

def test_board():
    filename = "board.txt"
    newboard = board.Board(open(filename))
    #assert False

@nottest
def test_board_init():
    test_data = [
    "LEVEL, alpha, 8",
    "LEVEL, beta, 8#This is a comment",
    "LEVEL, delta, 8",
    "LEVEL, gamma, 8",
    "LEVEL, outerspace, 1",
    "LEVEL, commandbay, 3",
    "LEVEL, supplybay, 3",
    "# This is a comment",
    "MOVE, alpha, 1, alpha, 2",
    "MOVE, alpha, 1, alpha, 3",
    "CAPTURE, alpha, 1, alpha,2, alpha, 4",
    "PIECE, player1, command, outerspace, 1",
    "PIECE, player1, supply, outerspace, 1",
    "PIECE, player1, drone, commandbay, 1",
    "PIECE, player1, drone, commandbay, 2",
    "PIECE, player1, drone, commandbay, 3",
    "PIECE, player1, drone, supplybay, 1",
    "PIECE, player1, drone, supplybay, 2",
    "PIECE, player1, drone, supplybay, 3",
    ]
    newboard = board.Board(test_data)

    #assert False

def test_space_valid_moves():
    tests = [ 
        [ 
            ["LEVEL, alpha, 8",
             "LEVEL, beta, 8",
             "MOVE, alpha, 1, alpha, 3",
             "MOVE, alpha, 1, beta, 1",
             "MOVE, alpha, 1, beta, 3",
             "PIECE, player1, drone, alpha, 3"],
             ["SPACE, beta, 1","SPACE, beta, 3"],
             "occupied space near alpha 1"
        ]
    ]

    def _check_valid_moves(testboard, expected, message):
        newboard = board.Board(testboard)
        spacetocheck = newboard.GetSpace("alpha", 1)
        moves = spacetocheck.GetMoves()
        print "%s: expected -- %s, got -- %s" % (message, expected, [move.__str__() for move in moves])
        assert expected == [move.__str__() for move in moves]

    for test in tests:
        yield _check_valid_moves, test[0], test[1], test[2]
    
def test_space_valid_captures():
    assert True
