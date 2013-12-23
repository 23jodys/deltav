import logging
logger = logging.getLogger(__name__)
class Piece:
    def __init__(self, shiptype, startinglocation):
        self.type = shiptype
        
class Player:
    def __init__(self, name):
        self.name = name
        self.pieces = []
        
    def AddPiece(self, piece):
        self.pieces.append(piece)
        
class Space:

    def __init__(self, levelname, spacenum):
        #logger.debug("trying to create SPACE with name %s, space %s" % (levelname, spacenum))
        self.levelname = levelname
        self.spacenum = int(spacenum)

        # A list of spaces that I could potentially move to
        self.moves = []

        # A list of spaces that I could potentially capture through and into
        self.captures = []

    def __str__(self):
        toreturn = "START SPACE %s, %s" % (self.levelname, self.spacenum)
        # if self.piece:
        #     toreturn += " PIECE: %s" % self.piece
        # else:
        #     toreturn += " PIECE: no piece here"    
        for move in self.moves:
            toreturn += "\n MOVE: into %s %s" % (move["to_level"], move["to_space"])

        for capture in self.captures:
            toreturn += "\n CAPTURE: capture through %s %s into %s %s" % (
                capture["capture_level"], capture["capture_space"],
                capture["to_level"], capture["to_space"])

        return toreturn

    def GetLevelName(self):
        #logger.debug("returning '%s'" % self.levelname)
        return self.levelname

    def GetSpaceNum(self):
        #logger.debug("returning '%s'" % self.spacenum)
        return self.spacenum
    
    def AddMove(self, movedict):
        """
        Arguments
        movedict -- a dictionary with { "from_level": %s, "from_space": %d, "to_level":%s, "to_space":%s }
        """
        logger.debug("adding move to %s %s" % 
                     (movedict["to_level"], movedict["to_space"]))
        self.moves.append({"to_level": movedict["to_level"],
                           "to_space": movedict["to_space"]})

    def AddCapture(self, capturedict):
        """
        Arguments
        capturedict -- a dictionary with { "from_level": %s, "from_space": %d, 
                                           "capture_level": %s, "capture_space": %d,
                                           "to_level":%s, "to_space":%d }

        """
        self.captures.append(capturedict)
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
                       "players": []} 
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
            logger.debug("processing line %d: %s" % (linenum, usable[0]))

            if els[0] == "LEVEL":
                logger.debug("LEVEL -- storing %s with %s elements" % (els[1].strip(), int(els[2].strip())))
                parsed["levels"][els[1].strip()] = int(els[2].strip())
                
            elif els[0] == "MOVE":
                logger.debug("MOVE -- storing from level %s space %s to level %s space %s" %
                             (els[1].strip(), els[2].strip(), els[3].strip(), els[4].strip()))
                parsed["move"].append( { "from_level": els[1].strip(),
                                         "from_space": els[2].strip(),
                                         "to_level": els[3].strip(),
                                         "to_space": els[4].strip() } )
                             
            elif els[0] == "CAPTURE":
                logger.debug("CAPTURE -- storing from space %s %s, capture space %s %s, finish at space %s %s" %
                             (els[1].strip(), els[2].strip(), 
                              els[3].strip(), els[4].strip(), 
                              els[5].strip(), els[6].strip()))
                parsed["capture"].append( { "from_level": els[1].strip(),
                                            "from_space": els[2].strip(),
                                            "capture_level": els[3].strip(),
                                            "capture_space": els[4].strip(),
                                            "to_level": els[5].strip(),
                                            "to_space": els[6].strip() } )

                logger.debug("UNKNOWN")
            elif els[0] == "PIECE":
                logger.debug("PIECE -- storing %s, type %s in location %s" % (els[1].strip(), 
                                                                              els[2].strip(), 
                                                                              els[3].strip()))
                parsed["piece"].append( {"player": els[1].strip(),
                                         "type": els[2].strip(),
                                         "location": els[3].strip() } )
                                                                              

            linenum += 1

        logger.debug("parsed structure is %s" % parsed)

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
            if from_space:
                from_space.AddMove(movedict)
            else:
                logger.error("WTF: couldn't find %s %s to start with" % (movedict["from_level"],
                                                                        movedict["from_space"]))

        # Populate all of the valid captures
        for capturedict in parsed["capture"]:
            print capturedict
            logger.debug("Trying to add capture from %s %s through %s %s into %s %s" %
                         (capturedict["from_level"], capturedict["from_space"],
                          capturedict["capture_level"], capturedict["capture_space"],
                          capturedict["to_level"], capturedict["to_space"]))
            form_space = self.GetSpace(capturedict["from_level"], capturedict["from_space"])
            if from_space:
                from_space.AddCapture(capturedict)
            else:
                logger.error("WTF: couldn't find %s %s to start with" % (capturedict["from_level"],
                                                                         capturedict["from_space"]))

        for space in self.board["spaces"]:
            logger.debug(space)

        # Create all of the players
        for player in ["player1", "player2"]:
            self.board["players"].append(Player(player))

        # Create all of the pieces
        for piece in parsed["piece"]:

            
    def GetSpace(self, levelname, spacenum):
        """
        Return a reference to a given space

        Arguments:
        levelname -- name of level
        spacenum -- integer number of space in that level

        Returns:
        a Space object
        """

        for space in self.board["spaces"]:
            #logger.debug("looking at space %s %s" % (space.GetLevelName(), space.GetSpaceNum()))
            if (space.GetLevelName() == levelname) and (space.GetSpaceNum() == int(spacenum)):
                return space
                    
        else:
            return False
