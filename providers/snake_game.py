__author__ = 'TrevorTa'


#TODO: NEED TO IMPLEMENT MAX LENGTH(HEALTH). CURRENTLY THE SNAKE CAN GROW TO ANY SIZE

class Board:
    # ==================== SERVER UTILITIES ============================
    # Notes: players are numbered from 1 to numPlayers.
    # Create a board:
    #   board = Board(width, height, numPlayers)
    #   board.initializeBoard() # add (numPlayers) random snakes of length 1
    #                             and (numPlayers - 1) foods
    def getGameState(self):
        """
        Return the game state to client. Game state includes positions of the snakes
        and positions of foods.
        :return: Example:
        {1:[[5,9], [5,10]],
        2: [[10,11], [11, 11], [12,11]],
        4: [[3, 2], [3, 3]],
        "foods":[[10,13], [32, 2]]}
        """
        res = {}
        for snakeID in self.snakes: # select each snakeID
            snake = self.snakes[snakeID]
            res[snakeID] = snake.body # {1: [[1,2], [1,3]]}
        res["foods"] = self.foods
        return res

    def moveAllSnakes(self):
        """
        Move all snakes on the board according to each snake's current direction.
        Called at each time tick.
        """
        snakesToRemove = []
        for i in self.snakes: # select each snakeID
            self.moveSnake(i, snakesToRemove)
        for i in snakesToRemove: # remove all the snakes that have length 0
            self.removeSnake(i)

    def changeDirection(self, player, direction):
        """
        Change direction of player to direction
        :param player: playerID (1 to numPlayers)
        :param direction: Direction.UP/DOWN/LEFT/RIGHT (do not allow STAY)
        """
        self.snakes[player].changeDirection(direction)

    # ======================= IMPLEMENTATION ===================================
    def __init__(self, w, h, players):
        """
        Initialize the game
        :param w: width of the board
        :param h: height of the board
        :param players: number of players (ASSUME players < 8 AT THE MOMENT)
        """
        assert players <= 8
        assert w * h > 2 * players - 1
        self.snakes = {} # dictionary from player to Snake, e.g. {1: Snake, 2: Snake}
        self.foods = [] # list of food, e.g. [(1,2), (3, 4)]
        self.w = w
        self.h = h
        self.numPlayers = players
        self.numFoods = players - 1 # set the number of foods to be numPlayers - 1

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
        print "Board"
        for i in range(0, len(board)):
            print board[i]
        #print board
        print "============="


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
        for i in range(1, self.numPlayers + 1):
            self.snakes[i] = Snake([], Direction.STAY) #
        for i in range(1, self.numPlayers + 1):
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
        head = snake.body[0]
        newHead = Direction.newPoint(head, snake.direction) # get the position of the new head of the snake
        # check if the snake hits the wall
        if self.isPointOutOfBound(newHead):
            snake.removeTail() # if the snake hits the wall, remove its tail
            if snake.length() == 0:
                #self.removeSnake(player)
                snakesToRemove.append(player)
            return
        overlappedSnake = self.isPointOnSnake(newHead) # id of the overlapped snake
        if overlappedSnake == 0: # no snake at this new point
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
                otherSnake.removeTail()
                if otherSnake.length() == 0:
                    snakesToRemove.append(overlappedSnake)
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
        return 0

    def generateRandomPoint(self):
        import random
        x = random.randint(0, self.w - 1)
        y = random.randint(0, self.h - 1)
        return [x, y]

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
        self.direction = direction

    def length(self):
        return len(self.body)

    def verifyBody(self, bodies):
        pass # TODO: IMPLEMENT

    def eatFood(self, food):
        """
        Only insert the food to body as the new head. Did not check for errors.
        """
        self.body.insert(0, food) #append to the front of the list

    def changeDirection(self, newDirection):
        """
        Change direction of this snake. Check that the snake is not turning around.
        """
        if not Direction.isOppositeDirection(self.direction, newDirection):
            self.direction = newDirection

    def move(self):
        """
        Move the snake in the current direction. Assume no collision to another snake
        Assume not going outside of the board.
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
            self.body.remove(self.body[-1]) # remove the tail of the snake


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
    #OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

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
