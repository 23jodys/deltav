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
        logger.debug("Adding player %s type %s to this location" % (piece.GetPlayer(), piece.GetType()))
        self.piece = piece

    def GetPiece(self):
        return self.piece
        
    def AddMove(self, moveto):
        """
        Arguments
        moveto -- a Space object where this move terminates

        """
        logger.debug("Attempting to add move to %s" % moveto)
        self.moves.append(moveto)

    def GetMoves(self):
        """ Get a list of valid moves from this location
        """
        #toreturn = [x for x in self.moves if not x.GetPiece()]
        toreturn = [x for x in self.moves if not x.GetPiece()]
        logger.debug("returning this list of valid moves %s" % toreturn)
        return toreturn
        
    def AddCapture(self, capture_space, to_space):
        """
        Arguments

        capture_space -- Space object that would be captured
        to_space -- Space object that this capture would end up in
        
        """
        self.captures.append({"capture": capture_space,
                              "to": to_space})

    def GetCaptures(self):
class Board:
    def __init__(self, filehandle):
        """initializes new board

        Arguments:
        filehandle -- file handle to read in, caller is responsible for opening/closing

        # anywhere on a line indicates that that character and all others 
        until the EOL are not to be read and discarded

        LEVEL, ${level name}, ${count}
        LEVEL, alpha, 8

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
                #logger.debug("MOVE -- storing from level %s space %s to level %s space %s" %
                #             (els[1].strip(), els[2].strip(), els[3].strip(), els[4].strip()))
                parsed["move"].append( { "from_level": els[1].strip(),
                                         "from_space": els[2].strip(),
                                         "to_level": els[3].strip(),
                                         "to_space": els[4].strip() } )
                             
            elif els[0] == "CAPTURE":
                #logger.debug("CAPTURE -- storing from space %s %s, capture space %s %s, finish at space %s %s" %
                #             (els[1].strip(), els[2].strip(), 
                #              els[3].strip(), els[4].strip(), 
                #              els[5].strip(), els[6].strip()))
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
            #print("levelname %s, levelcount = %s" % (levelname, levelcount))
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
            logger.debug("Trying to add capture from %s %s through %s %s into %s %s" %
                         (capturedict["from_level"], capturedict["from_space"],
                          capturedict["capture_level"], capturedict["capture_space"],
                          capturedict["to_level"], capturedict["to_space"]))
            from_space = self.GetSpace(capturedict["from_level"], capturedict["from_space"])
            to_space = self.GetSpace(capturedict["to_level"], capturedict["to_space"])
            capture_space = self.GetSpace(capturedict["capture_level"], capturedict["capture_space"])
            if from_space and to_space and capture_space:
                logger.debug("Adding capture from %s capturing %s into %s" % (from_space, capture_space, to_space))
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
                logger.debug("Added piece %s" % newpiece)
            else:
                logger.error("unable to add piece type %s owned by %s at %s %s" %
                             (piece["type"], piece["player"],
                              piece["levelname"], piece["spacenum"]))

        for space in self.board["spaces"]:
            logger.debug(space)

            

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

