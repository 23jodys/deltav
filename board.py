import logging
logger = logging.getLogger(__name__)

class Piece:
    def __init__(self, shiptype, player, startinglocation):
        self.shiptype = shiptype
        self.player = player
        self.location = startinglocation
        self.location.AddPiece(self)

    def __str__(self):
        return "owned by %s, type %s, location %s %s" % (self.player, self.shiptype, self.location.levelname, self.location.spacenum)

    def GetType(self):
        return self.shiptype

    def GetPlayer(self):
        return self.player

    def GetLocation(self):
        return self.location

class Space:

    def __init__(self, levelname, spacenum):
        #logger.debug("trying to create SPACE with name %s, space %s" % (levelname, spacenum))
        self.levelname = levelname
        self.spacenum = int(spacenum)

        self.piece = False
        # A list of spaces that I could potentially move to
        self.moves = []

        # A list of spaces that I could potentially capture through and into
        self.captures = []

    def __str__(self):
        toreturn = "SPACE, %s, %s" % (self.levelname, self.spacenum)
        return toreturn

    def DebugRepr(self):
        """ Returning textual representation of this node"""
        toreturn = "SPACE %s, %s" % (self.levelname, self.spacenum)
        # if self.piece:
        #     toreturn += " PIECE: %s" % self.piece
        # else:
        #     toreturn += " PIECE: no piece here"    
        for move in self.moves:
            toreturn += "\n MOVE: into %s " % move

        for capture in self.captures:
            toreturn += "\n CAPTURE: capture through %s into %s" % (
                capture["capture"], capture["to"])
        if self.piece:
            toreturn += "\n PIECE: player %s, type %s" % (self.piece.GetPlayer(), self.piece.GetType())

        return toreturn

        
    
    def GetLevelName(self):
        #logger.debug("returning '%s'" % self.levelname)
        return self.levelname

    def GetSpaceNum(self):
        #logger.debug("returning '%s'" % self.spacenum)
        return self.spacenum

    def AddPiece(self, piece):
        #logger.debug("Adding player %s type %s to this location" % (piece.GetPlayer(), piece.GetType()))
        self.piece = piece

    def GetPiece(self):
        return self.piece
        
    def AddMove(self, moveto):
        """
        Arguments
        moveto -- a Space object where this move terminates

        """
        #logger.debug("Attempting to add move to %s" % moveto)
        self.moves.append(moveto)

    def GetMoves(self):
        """ Get a list of Space objects that are valid moves from this location
        """
        #toreturn = [x for x in self.moves if not x.GetPiece()]
        #toreturn = [x for x in self.moves if not x.GetPiece()]
        #logger.debug("returning this list of valid moves %s" % toreturn)
        
        return self.moves
        
    def AddCapture(self, capture_space, to_space):
        """
        Arguments

        capture_space -- Space object that would be captured
        to_space -- Space object that this capture would end up in
        
        """
        self.captures.append({"capture": capture_space,
                              "to": to_space})
    def GetCaptures(self):
        """
        Return a list of dictionaries containing space objects
        { "to": Space,
           "capture": Space()}
        """
        return self.captures

class Board:
    def __init__(self, filehandle):
        """initializes new board

        Arguments:
        filehandle -- file handle to read in, caller is responsible for opening/closing

        # anywhere on a line indicates that that character and all others 
        until the EOL are not to be read and discarded

        LEVEL, ${level name}, ${count}, Owner
        LEVEL, alpha, 8, none

        MOVE, from level name, from space, to level name, to space
        # Example
        MOVE, alpha, 1, alpha, 2

        CAPTURE, from level name, from space, capture level name, capture space, to level name, to space
        CAPTURE, alpha, 1, alpha, 3, alpha, 5
        """
        self.board = { "levels": {},
                       "spaces": [],
                       "pieces": [],
                       "players": {}}
         
        self.turnnum = 1
        self.currentplayer = "player1"

        parsed = { "levels": {},
                   "move": [],
                   "capture": [],
                   "piece": [] }

        els = []
        linenum = 1
        logger.debug("Starting to read in filehandle")
        for line in filehandle:
            # Deal with comments by only using stuff to the left of our comment symble
            usable = line.split("#")
            els = usable[0].split(",")
            #            logger.debug("processing line %d: %s" % (linenum, usable[0]))

            if els[0] == "LEVEL":
                #logger.debug("LEVEL -- storing %s with %s elements" % (els[1].strip(), int(els[2].strip())))
                parsed["levels"][els[1].strip()] = int(els[2].strip())
                
            elif els[0] == "MOVE":
                if len(els) == 5:
                    # logger.debug("MOVE -- storing from level %s space %s to level %s space %s" %
                    #             (els[1].strip(), els[2].strip(), els[3].strip(), els[4].strip()))
                    parsed["move"].append( { "from_level": els[1].strip(),
                                             "from_space": els[2].strip(),
                                             "to_level": els[3].strip(),
                                             "to_space": els[4].strip() } )
                else:
                    logger.error("MOVE, but we do not have 5 elements")
         
            elif els[0] == "CAPTURE":
                if len(els) != 7:
                    logger.error("CAPTURE, but we do not have 7 elements")
                else:
#                     logger.debug("CAPTURE -- storing from space %s %s, capture space %s %s, finish at space %s %s" %
#                             (els[1].strip(), els[2].strip(), 
#                              els[3].strip(), els[4].strip(), 
#                              els[5].strip(), els[6].strip()))
                    parsed["capture"].append( { "from_level": els[1].strip(),
                                                "from_space": els[2].strip(),
                                                "capture_level": els[3].strip(),
                                                "capture_space": els[4].strip(),
                                                "to_level": els[5].strip(),
                                                "to_space": els[6].strip() } )

        
            elif els[0] == "PIECE":
                #logger.debug("PIECE -- storing %s, type %s in location %s %s" % (els[1].strip(), 
                                                                              # els[2].strip(), 
                                                                              # els[3].strip(),
                                                                              # els[4].strip()))
                parsed["piece"].append( {"player": els[1].strip(),
                                         "type": els[2].strip(),
                                         "levelname": els[3].strip(),
                                         "spacenum": els[4].strip()} )
                                                                              
            # else:
            #     logger.debug("UNKNOWN")
            linenum += 1

        #        logger.debug("parsed structure is %s" % parsed)

        # Create all of the spaces
        for (levelname, levelcount) in parsed["levels"].iteritems():
            print("levelname %s, levelcount = %s" % (levelname, levelcount))
            self.board["levels"][levelname] = {}
            for i in range(1, levelcount + 1):
                newspace = Space(levelname, i)
                #logger.debug("creating new space: %s" % newspace)
                self.board["spaces"].append( newspace )

        # Populate all of the valid moves
        for movedict in parsed["move"]:
            # logger.debug("Trying to add move %s %s to %s %s" %
            #              (movedict["from_level"], movedict["from_space"],
            #               movedict["to_level"], movedict["to_space"]))
            from_space = self.GetSpace(movedict["from_level"], movedict["from_space"])
            to_space = self.GetSpace(movedict["to_level"], movedict["to_space"])
            if from_space and to_space:
                from_space.AddMove(to_space)
            else:
                logger.error("WTF: couldn't find %s %s to start with" % (movedict["from_level"],
                                                                        movedict["from_space"]))

        # Populate all of the valid captures
        for capturedict in parsed["capture"]:
            # logger.debug("Trying to add capture from %s %s through %s %s into %s %s" %
#                          (capturedict["from_level"], capturedict["from_space"],
#                           capturedict["capture_level"], capturedict["capture_space"],
#                           capturedict["to_level"], capturedict["to_space"]))
            from_space = self.GetSpace(capturedict["from_level"], capturedict["from_space"])
            to_space = self.GetSpace(capturedict["to_level"], capturedict["to_space"])
            capture_space = self.GetSpace(capturedict["capture_level"], capturedict["capture_space"])
            if from_space and to_space and capture_space:
                #logger.debug("Adding capture from %s capturing %s into %s" % (from_space, capture_space, to_space))
                from_space.AddCapture(capture_space, to_space)
            else:
                logger.error("WTF: couldn't find %s %s to start with" % (capturedict["from_level"],
                                                                         capturedict["from_space"]))

        # # Create all of the players
        # for player in ["player1", "player2"]:
        #     self.board["players"].append({"name": player})

        #logger.debug( self.board["players"])

        # # create the supply and command ships first
        # for piece in parsed["piece"]:
        #     if piece["type"] == "command" or piece["type"] == "supply":
        #         # Create the actual pieces
        #         newpiece = Piece(piece["type"], piece["player"], piece["location"])
        #         logger.debug("Added piece %s" % newpiece)
        #         self.board["pieces"].append(newpiece)

        #         # Create the drone bay locations
        # Create all of the other pieces, this can only happen after we have created 
        # the levels and spaces and ships for them to exist in 
        for piece in parsed["piece"]:
            newlocation = self.GetSpace(piece["levelname"], piece["spacenum"])
            if newlocation:
                newpiece = Piece(piece["type"], piece["player"], newlocation)
                newlocation.AddPiece(newpiece)
                self.board["pieces"].append(newpiece)
#                 logger.debug("Added piece %s" % newpiece)
            else:
                logger.error("unable to add piece type %s owned by %s at %s %s" %
                             (piece["type"], piece["player"],
                              piece["levelname"], piece["spacenum"]))

        for space in self.board["spaces"]:
            logger.debug(space)

    def PrintSpace(self, levelname, spacenum):
        """
        return a single character for this space:

        @ = player1
        # = player2
        * = empty
        """

        piece = self.CheckSpace(levelname, spacenum)
        if piece:
            if piece.GetPlayer() == "player1":
                char = "@"
            elif piece.GetPlayer() == "player2":
                char = "#"
            else:
                char = "!" # WTF? How did we get here
        else:
            char = "*"

        return char

    def PrintBoard(self):
        printed_board = ""
        alt = False # if alt is True, then indent one empty space
        for levelname in self.board["levels"].keys():
            printed_board += " %s\n" % levelname

            if levelname == "alpha" or levelname == "gamma":
                alt = True
            else:
                alt = False

            printed_board += "+----+\n"
            for pair in [ (7,8), (5,6), (3,4), (1,2) ]:
                if alt:
                    printed_board += "| %s %s|\n" % (self.PrintSpace(levelname, pair[0]),
                                                     self.PrintSpace(levelname, pair[1]))
                    alt = False
                else:
                    printed_board += "|%s %s |\n" % (self.PrintSpace(levelname, pair[0]),
                                                     self.PrintSpace(levelname, pair[1]))
                    alt = True
                #print "| %s %s|" % self.PrintSpace(levelname, spacenum)

            printed_board += "+----+\n"

        return printed_board

    def GetValidCaptures(self, playername, location):            
        """ Assume that there is a piece owned by playername at this location
            what captures are possible?

        """
        toreturn = []
        for capture in location.GetCaptures():
            logger.debug("GetValidCaptures(%s, '%s'): looking at capture %s, to %s" %
                         (playername, location, capture["capture"], capture["to"]))

            # Check to see if there is any piece in the capture terminus
            if not capture["to"].GetPiece():
                # Check to see if there is another player's piece in the capture space
                capturepiece = capture["capture"].GetPiece()
                if capturepiece.GetPlayer() != playername:
                    toreturn.append({"from": location,
                                     "to": capture["to"],
                                     "capture": capture["capture"]})

            else:
                logger.debug("piece located at %s, capture move not valid" % capture["to"])
        return toreturn
    
    def GetValidMoves(self, location):
        """ Return a list of valid moves"""
        toreturn = []

        # Additionally, any drone in a command/supply bay may move to any location
        # that the command or supply ship could move to.
        (player, levelname) = location.GetLevelName().split("_")
        if 
        piece = location.GetPiece()
        if piece and (piece.GetType() == "command" or piece.GetType() == "supply"):
            moves = 

        for move in location.GetMoves():
            if not move.GetPiece():
                toreturn.append(move)

        return toreturn

    def CheckSpace(self, levelname, spacenum):
        """
        Return reference to the piece occupying this space, if any
        
        """

        space = self.GetSpace(levelname, spacenum)
        if space:
            return space.GetPiece()
        else:
            return False
        
    def GetSpace(self, levelname, spacenum):
        """
        Return a reference to a given space

        Arguments:
        levelname -- name of level
        spacenum -- integer number of space in that level

        Returns:
        a Space object
        """
        #logger.debug("looking for %s %s" % (levelname, spacenum))
        for space in self.board["spaces"]:
            #logger.debug("looking at space %s %s" % (space.GetLevelName(), space.GetSpaceNum()))
            if (space.GetLevelName() == levelname) and (space.GetSpaceNum() == int(spacenum)):
                #logger.debug("returning %s" % space)
                return space
                    
        else:
            return False

    def ExecuteTurn(self, move):
        """
        Takes a textual description of a move, parses, then executes if possible, 
        
        player1, player1_supply, 1, MOVE, alpha, 1
        player2, player2_supply, 1, MOVE, beta, 2
        player1, alpha, 1, CAPTURE, gamma, 2

        Returns -- "SUCCESS" if sucessful

        otherwise returns "ERROR, text error message"
        """

        (player, startname, startnum, type, toname, tonum) = move.split(",")

        error = False
        
        # Check that this player can make a move
        if player != self.currentplayer:
            errormsg = "Not the current player"
            error = True

        # Check that piece exists and player owns it
        piece = self.CheckSpace(startname, startnum)
        print piece
        if not piece or piece.GetPlayer() != player:
            errormsg = "You cannot move that piece"
            error = True

        if error:
            return errormsg

        if type == "MOVE":
            # If this is a move, verify that it is valid, then do it
            errormsg = "SUCCESS"
        elif type == "CAPTURE":
            # If this is a capture, verify, then do it
            errormsg = "SUCCESS"
        else:
            # Otherwise return an error
            errormsg = "I don't know what type of turn %s is" % type

        return errormsg


        
    #def CheckMove(self, piece, to):

    def CheckCapture(self, piece, capture, to):
        test = { "from": piece.GetLocation(),
                 "capture": capture,
                 "to": to }
        for i in self.GetValidCaptures(piece.GetPlayer(), piece.GetLocation()):
            if test == i:
                logger.debug("CheckCapture(%s, %s, %s): this is a valid capture" % (piece, capture, to))
                return True
            
        else:
            logger.debug("CheckCapture(%s, %s, %s): this is a valid capture" % (piece, capture, to))
            return False
    
        
