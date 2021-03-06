__author__ = 'TrevorTa'

import threading
from combating_snake_settings import *

#TODO: NEED TO IMPLEMENT MAX LENGTH(HEALTH). CURRENTLY THE SNAKE CAN GROW TO ANY SIZE

class Board:
    # ==================== SERVER UTILITIES ============================
    # Create a board:
    #   board = Board(width, height, playerIDs)
    #   board.initializeBoard() # add (numPlayers) random snakes of length 1
    #                             and (numPlayers - 1) foods
    def getGameState(self):
        """
        Return the game state to client. Game state includes positions of the snakes
        and positions of foods.
        :return: Example:
        {"ea9":[[5,9], [5,10]],
         "ca8": [[10,11], [11, 11], [12,11]],
        "_food":[[10,13], [32, 2]]}
        """
        with self.lock:
            res = {}
            for snakeID in self.snakes: # select each snakeID
                snake = self.snakes[snakeID]
                res[snakeID] = snake.body # {1: [[1,2], [1,3]]}
            res["_food"] = self.foods
            return res

    def getWinnerIds(self):
        """
        Return None if there is no winner, [] if the game has ended and
        drawn, [id] if the game has ended and there is a winner.
        """
        with self.lock:
            if len(self.snakes) == 0:
                return []
            if len(self.snakes) == 1:
                return self.snakes.keys()
            potentialWinners = [snakeId for (snakeId, snake) in self.snakes.items() if snake.length() >= SNAKE_MAX_LENGTH]
            if potentialWinners:
                return potentialWinners
            return None

    def moveAllSnakes(self):
        """
        Move all snakes on the board according to each snake's current direction.
        Called at each time tick.
        """
        with self.lock:
            snakesToRemove = []
            for i in self.snakes: # select each snakeID
                self.moveSnake(i, snakesToRemove)
            for i in snakesToRemove: # remove all the snakes that have length 0
                self.removeSnake(i)

    def onKeyStroke(self, player, direction):
        """
        Mimics the behavior when a player hits a keystroke
        :param player: playerID (1 to numPlayers)
        :param direction: Direction.UP/DOWN/LEFT/RIGHT (do not allow STAY)
        """
        with self.lock:
            self.snakes[player].onKeyStroke(direction)

    # def gameEnds(self):
    #     if len(self.snakes) > 1:
    #         return None
    #     # number of snakes is 0 or 1
    #     for snakeID in self.snakes:
    #         return snakeID # should return only 1 snake
    #     return None # FIXME: NO ONE WINS?

    # ======================= IMPLEMENTATION ===================================
    def __init__(self, w, h, players):
        """
        Initialize the game
        :param w: width of the board
        :param h: height of the board
        :param players: list of player IDs
        """
        assert len(players) <= MAX_MEMBERS_IN_ROOM
        assert w * h > 2 * len(players) - 1
        # print("[LOGIC] board is initialized to size {} x {}".format(h, w))
        self.snakes = {} # dictionary from player to Snake, e.g. {1: Snake, 2: Snake}
        self.foods = [] # list of food, e.g. [(1,2), (3, 4)]
        self.w = w
        self.h = h
        self.numPlayers = len(players)
        self.players = players
        self.numFoods = self.numPlayers - 1 # set the number of foods to be numPlayers - 1
        self.lock = threading.Lock()

    def initializeBoard(self):
        self.initializeSnakes()
        self.initializeFoods()

    def drawBoard(self):
        """
        Print the board to screen for debugging purposes.
        :return:
        """
        board = []
        for r in range(self.h):
            row = []
            for c in range(self.w):
                row.append(" ")
            board.append(row)
        for i in self.snakes: # select each snakeID
            snake = self.snakes[i]
            for (r,c) in snake.body:
                board[r][c] = str(i)
        for (r, c) in self.foods:
            board[r][c] = "F"
        print("Board")
        for i in range(0, len(board)):
            print(board[i])
        #print board
        print("=============")


    def initializeFoods(self):
        """
        Initialize all the foods
        """
        for i in range(0, self.numFoods):
            self.addFood()

    def initializeSnakes(self):
        """
        Initialize all the snakes, give each of them a body of 1 CELL
        """
        for i in self.players:
            self.snakes[i] = Snake([], Direction.STAY) #
        for i in self.players:
            self.initializeSnake(i)

    def initializeSnake(self, player):
        """
        Initialize snake for player at a RANDOM point with 1 point body
        :param player: playerID
        """
        head= self.generateRandomPoint()
        while self.isPointOnSnake(head):
            head = self.generateRandomPoint()
        self.snakes[player].body.append(head)

    def isPointOutOfBound(self, point):
        row = point[0] # the current row
        if row < 0 or row >= self.h:
            return True # the snake is out of bound
        col = point[1] # the current col
        if col < 0 or col >= self.w:
            return True # the snake is out of bound
        return False

    def removeSnake(self, player):
        if player in self.snakes:
            del self.snakes[player]

    def moveSnake(self, player, snakesToRemove):
        """
        Move snake. This is the most complicated function since it will take care all
        snake logics, include eating food, attacking opponent, check bounds
        :param player: player's ID, get the snake from the snakes dictionary
        """
        snake = self.snakes[player] # get the current snake
        snake.applyLastKeyStroke()
        if snake.direction == Direction.STAY:
            return
        if len(snake.body) == 0:
            return # can't move an empty snake
        head = snake.body[0]
        newHead = Direction.newPoint(head, snake.direction) # get the position of the new head of the snake
        # check if the snake hits the wall
        if self.isPointOutOfBound(newHead):
            snake.removeTail() # if the snake hits the wall, remove its tail
            if snake.length() == 0:
                snakesToRemove.append(player)
                # print('[LOGIC] killing {} : out of bounds : {}'.format(player, newHead))
            return
        overlappedSnake = self.isPointOnSnake(newHead) # id of the overlapped snake
        if not overlappedSnake: # no snake at this new point
            if self.isPointOnFood(newHead):
                snake.eatFood(newHead) # grow longer
                self.foods.remove(newHead)
                self.addFood()
            else:
                snake.move() # move normally otherwise
        else: # the new point has a snake
            otherSnake = self.snakes[overlappedSnake]
            if otherSnake.body[0] == newHead: # attack on the head, both snakes got hurt
                snake.removeTail()
                if snake.length() == 0:
                    snakesToRemove.append(player)
                    # print('[LOGIC] killing {} : length is zero from headon collision'.format(player))
                otherSnake.removeTail()
                if otherSnake.length() == 0:
                    snakesToRemove.append(overlappedSnake)
                    # print('[LOGIC] killing {} : length is zero from headon collision'.format(player))
            else: # attack body of the other snake, the other snake got hurt
                otherSnake.removeTail()
                snake.move()

    def addFood(self):
        point = self.generateRandomPoint()
        while self.isPointOnSnake(point) or self.isPointOnFood(point):
            point = self.generateRandomPoint()
        self.foods.append(point)

    def isPointOnFood(self, point):
        """
        :param point:
        :return: True if the point is on a food
        """
        return point in self.foods

    def isPointOnSnake(self, point):
        """
        :param point: tuple (x,y)
        :return: the id of the snake that the point is on
        """
        for snakeID in self.snakes: # select each snake ID
            for body in self.snakes[snakeID].body: # select the body of each snake
                if body == point:
                    return snakeID
        return None

    def generateRandomPoint(self):
        import random
        c = random.randint(0, self.w - 1)
        r = random.randint(0, self.h - 1)
        return [r, c]

class Snake:
    def __init__(self, bodies, direction):
        """
        Initialize the snakes with bodies and direction
        :param bodies: list of tuples of point, e.g. [(1,2), (1,3)]
        :param direction: a direction in class Direction
        :return:
        """
        self.verifyBody(bodies)
        self.body = bodies
        self.direction = self.lastKeyStroke = direction

    def length(self):
        return len(self.body)

    def verifyBody(self, bodies):
        pass # TODO: IMPLEMENT

    def eatFood(self, food):
        """
        Only insert the food to body as the new head. Did not check for errors.
        """
        self.body.insert(0, food) #append to the front of the list

    def applyLastKeyStroke(self):
        """
        Return true if changing direction to lastKeyStroke is legal
        """
        if self.length() == 1 or not Direction.isOppositeDirection(self.direction, self.lastKeyStroke):
            self.direction = self.lastKeyStroke

    def onKeyStroke(self, keyStroke):
        """
        Change direction of this snake. Check that the snake is not turning around.
        """
        self.lastKeyStroke = keyStroke

    def move(self):
        """
        Move the snake in the current direction. Assume no collision to another snake
        Assume not going outside of the board. Assume applyLastKeyStroke is called
        """
        head = self.body[0]
        newHead = Direction.newPoint(head, self.direction)
        self.body.insert(0, newHead) # append the new head to the beginning of the body
        self.removeTail() # remove tail last in case of length-1 body

    def removeTail(self):
        """
        Hurt the snake by remove the tail of the snake
        """
        if len(self.body) > 0:
            self.body.pop()
            # self.body.remove(self.body[-1]) # remove the tail of the snake



class Direction:
    """
    Keep the direction and position logic for the board.
    Use list to represent each point.
    Point [R, C] represents cell at row R (zero-indexed) and column C (zero-indexed).
    Board:
        C0 C1 C2 C3 C4 C5 C6 C7 C8
    R0
    R1
    R2
    R3
    R4
    """
    UP = [-1, 0] # go up, row decreases by 1
    DOWN = [1, 0] # go down, row increases by 1
    LEFT = [0, -1] # go left, column decreases by 1
    RIGHT = [0, 1] # go right, column increases by 1
    STAY = [0, 0]

    @staticmethod
    def from_str(s):
        """
        Translate from string 'l','r','u','d' to Direction.
        :param s: string representation of direction
        """
        if (s == 'l'):
            return Direction.LEFT
        if (s == 'r'):
            return Direction.RIGHT
        if (s == 'u'):
            return Direction.UP
        if (s == 'd'):
            return Direction.DOWN
        return None

    @staticmethod
    def isOppositeDirection(dir1, dir2):
        """
        :param dir1:
        :param dir2:
        :return: true if DIR1 is opposite from DIR2
        """
        # Stay direction has no opposite
        if dir1 == Direction.STAY or dir2 == Direction.STAY:
            return False
        if dir1 == Direction.LEFT:
            return dir2 == Direction.RIGHT
        if dir1 == Direction.RIGHT:
            return dir2 == Direction.LEFT
        if dir1 == Direction.UP:
            return dir2 == Direction.DOWN
        if dir1 == Direction.DOWN:
            return dir2 == Direction.UP
        return True

    @staticmethod
    def newPoint(currentPoint, direction):
        return [currentPoint[0] + direction[0], currentPoint[1] + direction[1]]
