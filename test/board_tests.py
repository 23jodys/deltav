
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
def test_space_GetValidCaptures():
    tests = [ 
        [ 
            ["LEVEL, alpha, 8",
             "CAPTURE, alpha, 1, alpha, 2, alpha, 4",
             "PIECE, player2, drone, alpha, 2"],
             "alpha",
             1,
             "player1",
             [['SPACE, alpha, 1', 'SPACE, alpha, 2', 'SPACE, alpha, 4']],
             "valid capture of alpha 2"
        ],
        [
            ["LEVEL, alpha, 8",
             "CAPTURE, alpha, 1, alpha, 2, alpha, 4",
             "PIECE, player2, drone, alpha, 4"],
             "alpha",
             1,
             "player1",
             [],
             "valid capture of alpha 2"
        ]
    ]

    def _GetValidCaptures(testboard, levelname, spacenum, playername, expected, message):
        newboard = board.Board(testboard)
        spacetocheck = newboard.GetSpace(levelname, spacenum)
        captures = newboard.GetValidCaptures(playername, spacetocheck)
        print "%s: expected -- %s\n got                               -- %s" % (message, 
                                                 expected, 
                                                 [ 
                                                     [x["from"].__str__(), 
                                                      x["capture"].__str__(),  
                                                      x["to"].__str__()] for x in captures
                                                    ] )

        assert expected == [ 
            [x["from"].__str__(), 
             x["capture"].__str__(),  
             x["to"].__str__()] for x in captures
             ]
                                                    

    for test in tests:
        yield _GetValidCaptures, test[0], test[1], test[2], test[3], test[4], test[5]

def test_board_PrintBoard():
    tests = [ 
        [
            ["LEVEL, alpha, 8",
             "LEVEL, beta, 8",
             "LEVEL, gamma, 8",
             "LEVEL, delta, 8",
             "PIECE, player1, drone, alpha, 3",
             "PIECE, player2, drone, alpha, 1",
             "PIECE, player3, drone, alpha, 8"],
            """

 alpha
+----+
| * !|
|* * |
| @ *|
|# * |
+----+
 beta
+----+
|* * |
| * *|
|* * |
| * *|
+----+
 gamma
+----+
| * *|
|* * |
| * *|
|* * |
+----+
 delta
+----+
|* * |
| * *|
|* * |
| * *|
+----+


""",
            "bad test" ]
        ]

    def _PrintBoard(testboard, expected, message):
        newboard = board.Board(testboard)
        printed_board = newboard.PrintBoard()
        print printed_board
        #assert printed_board == expected

    for test in tests:
        yield _PrintBoard, test[0], test[1], test[2]

def test_board_PrintSpace():
    tests = [
        [
            ["LEVEL, alpha, 8",
             "LEVEL, beta, 8",
             "LEVEL, gamma, 8",
             "LEVEL, delta, 8",
             "PIECE, player1, drone, alpha, 3",
             "PIECE, player2, drone, alpha, 1",
             "PIECE, player3, drone, alpha, 8"],
             { "alpha": [ "#", "*", "@", "*", "*", "*", "*", "!"  ],
               "beta":  [ "*", "*", "*", "*", "*", "*", "*", "*"   ],
               "gamma": [ "*", "*", "*", "*", "*", "*", "*", "*"  ],
               "delta": [ "*", "*", "*", "*", "*", "*", "*", "*"   ]},
            "good test"
            ]
        ]

    def _PrintSpace(testboard, expected_dict):

        newboard = board.Board(testboard)
        for levelname in ["alpha", "beta", "gamma", "delta"]:
            for spacenum in range(1, 9):
                print "checking %s %s" % (levelname, spacenum)
                piece = newboard.PrintSpace(levelname, spacenum)

                print "got %s, expected %s" % ( piece, expected_dict[levelname][spacenum - 1])
                assert piece == expected_dict[levelname][spacenum - 1]


    for test in tests:
        yield _PrintSpace, test[0], test[1]
               

def test_board_CheckSpace():
    tests = [
        [
            ["LEVEL, alpha, 8",
             "LEVEL, beta, 8",
             "LEVEL, gamma, 8",
             "LEVEL, delta, 8",
             "PIECE, player1, drone, alpha, 3",
             "PIECE, player2, drone, alpha, 1",
             "PIECE, player3, drone, alpha, 8"],
             { "alpha": ["player2", False, "player1", False, False, False, False, "player3"],
               "beta": [False, False, False, False, False, False, False, False],
               "gamma": [False, False, False, False, False, False, False, False],
               "delta": [False, False, False, False, False, False, False, False]},
            "good test"
        ]
    ]


    def _CheckSpace(testboard, expected_dict):
        newboard = board.Board(testboard)
        for levelname in ["alpha", "beta", "gamma", "delta"]:
            for spacenum in range(1, 9):
                print "checking %s %s" % (levelname, spacenum)
                piece = newboard.CheckSpace(levelname, spacenum)
                if piece:
                    playername = piece.GetPlayer()
                    print "got %s, expected %s" % ( playername, expected_dict[levelname][spacenum - 1])
                    assert playername == expected_dict[levelname][spacenum - 1]
                else:
                    print "no piece here"
                    assert expected_dict[levelname][spacenum - 1] == False

    for test in tests:
        yield _CheckSpace, test[0], test[1]


def test_space_ExecuteTurn():
    tests = [
        [
            "board.txt",
            [[ "player1, player1_supplybay, 1, MOVE, alpha, 1", "SUCCESS"],
             [ "player2, player2_supplybay, 1, MOVE, beta, 2", "SUCCESS"],
             [ "player1, alpha, 1, CAPTURE, gamma, 2", "SUCESS"]]
            ]
        ]

    def _ExecuteTurn(testboardfile, turns):
        with open(testboardfile) as testfile:
            newboard = board.Board(testfile)
            for turn in turns:
                result = newboard.ExecuteTurn(turn[0])
                print "trying to execute move: %s" % turn[0]
                print "expected %s, got %s" % (turn[1], result)
                assert result == turn[1]

    for test in tests:
        yield _ExecuteTurn, test[0], test[1]

        
def test_space_GetValidMoves():
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
        moves = newboard.GetValidMoves(spacetocheck)
        print "%s: expected -- %s, got -- %s" % (message, expected, [move.__str__() for move in moves])
        assert expected == [move.__str__() for move in moves]

    for test in tests:
        yield _check_valid_moves, test[0], test[1], test[2]
    
def test_space_valid_captures():
    assert True
