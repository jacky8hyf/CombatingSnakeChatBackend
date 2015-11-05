__author__ = 'TrevorTa'
import random

class Direction:
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    STAY = (0, 0)
    OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

    @staticmethod
    def isOppositeDirection(dir1, dir2):
        """
        :param dir1:
        :param dir2:
        :return: true if DIR1 is opposite from DIR2
        """
        return Direction.OPPOSITE[dir1] == dir2

    @staticmethod
    def newPoint(currentPoint, direction):
        return (currentPoint[0] + direction[0], currentPoint[1] + direction[1])

class Board:
    def __init__(self, w, h, players):
        """
        Initialize the game
        :param w: width of the board
        :param h: height of the board
        :param players: number of players (ASSUME players < 8 AT THE MOMENT)
        """
        assert players <= 8
        self.snakes = {} # dictionary from player to Snake, e.g. {1: Snake, 2: Snake}
        self.foods = [] # list of food, e.g. [(1,2), (3, 4)]
        self.w = w
        self.h = h
        self.numPlayers = players
        self.numFoods = players - 1 # set the number of foods to be numPlayers - 1
        self.initializeSnakes()
        self.initializeFoods()

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
            head = Board.generateRandomPoint()
        self.snakes[player].body.append(head)

    def moveSnake(self, player):
        """
        Move snake. This is the most complicated function since it will take care all
        snake logics, include eating food, attacking opponent, check bounds
        :param player: player's ID, get the snake from the snakes dictionary
        """
        
        self.snakes[player].move()

    def addFood(self):
        point = Board.generateRandomPoint()
        while self.isPointOnSnake(point):
            point = Board.generateRandomPoint()
        self.foods.append(point)

    def isPointOnSnake(self, point):
        """
        :param point: tuple (x,y)
        :return: true if point is overlap with another snake's body
        """
        for snakeID in self.snakes: # select each snake
            for body in self.snakes[snakeID].body: # select the body of each snake
                if body == point:
                    return True
        return False

    def generateRandomPoint(self):
        x = random.randint(0, self.w - 1)
        y = random.randint(0, self.h - 1)
        return (x, y)

    def changeDirection(self, player, direction):
        self.snakes[player].changeDirection(direction)


class Snake:
    def __init__(self, bodies, direction):
        """
        Initialize the snakes with bodies and direction
        :param bodies: list of tuples of point, e.g. [(1,2), (1,3)]
        :param direction: a direction in class Direction
        :return:
        """
        self.body = bodies
        self.direction = direction

    def eatFood(self, food):
        self.body.append(food) #append to the end of the list

    def changeDirection(self, newDirection):
        """
        Change direction of this snake. Check that the snake is not turning around.
        """
        if not Direction.isOppositeDirection(self.direction, newDirection):
            self.direction = newDirection

    def move(self):
        """
        Move the snake in the current direction. Assume no collision to another snake
        """
        self.body.remove(len(self.body) - 1) # remove the tail of the snake
        head = self.body[0]
        newHead = Direction.newPoint(head, self.direction)
        self.body.insert(0, newHead) # append the new head to the beginning of the body

Board(20, 20, 4)