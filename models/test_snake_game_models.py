__author__ = 'TrevorTa'
# Tests for snake_game.py
#from django.test import TestCase
from .snake_game_models import *
from unittest import TestCase

class SnakeGameModelsTestCase(TestCase):
    def testSnakeInit(self):
        snake = Snake([[1,1]], Direction.UP)
        self.assertTrue(snake.direction == Direction.UP)
        self.assertTrue(len(snake.body) == 1)
        self.assertTrue(snake.body[0] == [1,1])

    def testMoveSnake(self):
        snake = Snake([(1,1)], Direction.UP)
        snake.move()
        self.assertTrue(len(snake.body) == 1)
        self.assertTrue(snake.body[0] == [0,1])

    def testChangeDirection(self):
        snake = Snake([[1,1]], Direction.UP)
        snake.changeDirection(Direction.DOWN)
        # not allow to change to opposite direction
        self.assertTrue(snake.direction == Direction.UP)
        snake.changeDirection(Direction.LEFT)
        self.assertTrue(snake.direction == Direction.LEFT)
        snake.changeDirection(Direction.STAY)
        self.assertTrue(snake.direction == Direction.STAY)
        snake.changeDirection(Direction.RIGHT)
        self.assertTrue(snake.direction == Direction.RIGHT)
        snake.changeDirection(Direction.LEFT)
        self.assertTrue(snake.direction == Direction.RIGHT)
        snake.changeDirection(Direction.UP)
        self.assertTrue(snake.direction == Direction.UP)

    def testMoveAndChangeDirection(self):
        snake = Snake([[1,1]], Direction.UP)
        snake.move()
        self.assertTrue(len(snake.body) == 1)
        self.assertTrue(snake.body[0] == [0,1])
        snake.changeDirection(Direction.LEFT)
        snake.move()
        self.assertTrue(snake.body[0] == [0,0])
        snake.changeDirection(Direction.STAY)
        snake.move()
        self.assertTrue(snake.body[0] == [0,0])

    def testEatFood(self):
        snake = Snake([[1,1]], Direction.UP)
        snake.eatFood([1, 2]) # add to the front of the list
        snake.eatFood([1, 3])
        snake.eatFood([1, 4])
        self.assertTrue(len(snake.body) == 4)
        self.assertTrue(snake.body == [[1,4],[1,3],[1,2],[1,1]])

    def testRemoveTail(self):
        snake = Snake([[1,1],[1,2],[1,3],[1,4]], Direction.UP)
        snake.removeTail()
        self.assertTrue(len(snake.body) == 3)
        self.assertTrue(snake.body == [[1,1],[1,2],[1,3]])
        snake.removeTail()
        self.assertTrue(len(snake.body) == 2)
        self.assertTrue(snake.body == [[1,1],[1,2]])

    def testEatAndRemoveTail(self):
        snake = Snake([[1,1],[1,2],[1,3],[1,4]], Direction.UP)
        snake.removeTail()
        self.assertTrue(len(snake.body) == 3)
        self.assertTrue(snake.body == [[1,1],[1,2],[1,3]])
        snake.eatFood([1,0])
        snake.removeTail()
        self.assertTrue(len(snake.body) == 3)
        self.assertTrue(snake.body == [[1,0],[1,1],[1,2]])

class DirectionTestCase(TestCase):
    def testOppositeDirection(self):
        self.assertTrue(Direction.isOppositeDirection(Direction.LEFT, Direction.RIGHT))
        self.assertTrue(Direction.isOppositeDirection(Direction.RIGHT, Direction.LEFT))
        self.assertTrue(Direction.isOppositeDirection(Direction.UP, Direction.DOWN))
        self.assertTrue(Direction.isOppositeDirection(Direction.DOWN, Direction.UP))
        self.assertFalse(Direction.isOppositeDirection(Direction.DOWN, Direction.LEFT))
        self.assertFalse(Direction.isOppositeDirection(Direction.DOWN, Direction.RIGHT))
        self.assertFalse(Direction.isOppositeDirection(Direction.UP, Direction.RIGHT))
        self.assertFalse(Direction.isOppositeDirection(Direction.UP, Direction.UP))

    def testNewPoint(self):
        self.assertTrue(Direction.newPoint([1,0], Direction.RIGHT) == [1,1])
        self.assertTrue(Direction.newPoint([5,5], Direction.LEFT) == [5,4])
        self.assertTrue(Direction.newPoint([1,0], Direction.DOWN) == [2,0])
        self.assertTrue(Direction.newPoint([1,0], Direction.UP) == [0,0])
        self.assertTrue(Direction.newPoint([1,0], Direction.STAY) == [1,0])
        self.assertTrue(Direction.newPoint([1,3], Direction.RIGHT) == [1,4])

class BoardTestCase(TestCase):
    def testInitBoard(self):
        board = Board(5, 5, [1,2,3,4])
        board.initializeBoard()
        self.assertEquals(board.w, 5)
        self.assertEquals(board.h, 5)
        self.assertEquals(board.numPlayers, 4)
        self.assertEquals(len(board.foods), 3)
        self.assertEquals(len(board.snakes), 4)

    def testAddFood(self):
        board = Board(5, 5, [1,2,3,4])
        board.initializeFoods()
        self.assertEquals(len(board.foods), 3)
        board.addFood()
        self.assertEquals(len(board.foods), 4)
        board.addFood()
        self.assertEquals(len(board.foods), 5)
        board.addFood()
        self.assertEquals(len(board.foods), 6)

    def testIsPointOutOfBound(self):
        board = Board(5, 5, [1,2,3,4])
        self.assertFalse(board.isPointOutOfBound([1,2]))
        self.assertTrue(board.isPointOutOfBound([1,10]))
        self.assertTrue(board.isPointOutOfBound([10,10]))
        self.assertTrue(board.isPointOutOfBound([-10,10]))
        self.assertTrue(board.isPointOutOfBound([10,-10]))
        self.assertTrue(board.isPointOutOfBound([5,5]))

    def testIsPointOnFood(self):
        board = Board(5, 5, [1,2,3,4])
        board.foods = [[1,2],[2,3],[3,4]]
        self.assertTrue(board.isPointOnFood([1,2]))
        self.assertTrue(board.isPointOnFood([2,3]))
        self.assertTrue(board.isPointOnFood([3,4]))
        self.assertFalse(board.isPointOnFood([0,0]))

    def testIsPointOnSnake(self):
        board = Board(5, 5, [1,2,3,4])
        board.snakes[1] = Snake([[1,1]], Direction.STAY)
        board.snakes[2] = Snake([[0,0]], Direction.LEFT)
        self.assertTrue(board.isPointOnSnake([1,1]))
        self.assertTrue(board.isPointOnSnake([0,0]))
        self.assertFalse(board.isPointOnSnake([2,1]))
        self.assertFalse(board.isPointOnSnake([2,2]))

    def testMoveAllSnakes(self):
        board = Board(5, 5, [1,2,3,4])
        board.snakes[1] = Snake([[1,1]], Direction.DOWN)
        board.snakes[2] = Snake([[0,0]], Direction.RIGHT)
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[2,1]])
        self.assertEqual(board.snakes[2].body, [[0,1]])
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[3,1]])
        self.assertEqual(board.snakes[2].body, [[0,2]])
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[4,1]])
        self.assertEqual(board.snakes[2].body, [[0,3]])
        board.moveAllSnakes() # snake1 hits wall
        self.assertEquals(len(board.snakes), 1)
        self.assertEqual(board.snakes[2].body, [[0,4]])
        board.moveAllSnakes() # snake2 hits wall
        self.assertEquals(len(board.snakes), 0)

    def testMoveSnake(self):
        board = Board(5, 5, [1,2,3,4])
        board.snakes[1] = Snake([[1,1], [0,1]], Direction.DOWN)
        board.moveSnake(1, [])
        self.assertEqual(board.snakes[1].body, [[2,1],[1,1]])
        board.moveSnake(1, [])
        self.assertEqual(board.snakes[1].body, [[3,1],[2,1]])
        board.changeDirection(1, Direction.RIGHT)
        board.moveSnake(1, [])
        self.assertEqual(board.snakes[1].body, [[3,2],[3,1]])
        board.moveSnake(1, [])
        self.assertEqual(board.snakes[1].body, [[3,3],[3,2]])
        board.changeDirection(1, Direction.RIGHT)
        board.moveSnake(1, [])
        self.assertEqual(board.snakes[1].body, [[3,4],[3,3]])
        board.changeDirection(1, Direction.LEFT)
        self.assertEqual(board.snakes[1].direction, Direction.RIGHT)
        board.moveSnake(1, [])
        self.assertEqual(board.snakes[1].body, [[3,4]]) # can't change opposite direction, keep going and hit the wall

    def testRemoveSnake(self):
        board = Board(5, 5, [1,2,3,4,5,6])
        board.initializeBoard()
        self.assertEquals(len(board.snakes), 6)
        board.removeSnake(2)
        self.assertEquals(len(board.snakes), 5)
        board.removeSnake(2)
        self.assertEquals(len(board.snakes), 5)
        board.removeSnake(3)
        self.assertEquals(len(board.snakes), 4)
        board.removeSnake(1)
        self.assertEquals(len(board.snakes), 3)

    def testMoveSnakeHitWall(self):
        board = Board(5, 5, [1])
        board.snakes[1] = Snake([[0,0],[0,1], [0,2], [0,3]], Direction.LEFT)
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[0,0],[0,1],[0,2]])
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[0,0],[0,1]])
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[0,0]])
        board.moveAllSnakes()
        self.assertTrue(len(board.snakes) == 0)

    def testMoveSnakeEatFood(self):
        board = Board(5, 5, [1])
        board.snakes[1] = Snake([[0,0]], Direction.RIGHT)
        board.foods = [[0,1],[0,2],[0,3],[1,3]]
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[0,1],[0,0]])
        self.assertEqual(len(board.foods), 4) # keep the same number of foods
        board.moveAllSnakes()
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[0,3],[0,2],[0,1],[0,0]])
        self.assertEqual(len(board.foods), 4) # keep the same number of foods
        board.changeDirection(1, Direction.DOWN)
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[1,3],[0,3],[0,2],[0,1],[0,0]])
        self.assertEqual(len(board.foods), 4) # keep the same number of foods

    def testMoveSnakeAttackSimple(self):
        board = Board(5, 5, [1,2])
        board.snakes[1] = Snake([[2,1],[2,0]], Direction.RIGHT)
        board.snakes[2] = Snake([[1,2],[2,2],[3,2],[4,2]], Direction.UP)
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[2,2],[2,1]])
        self.assertEqual(board.snakes[2].body, [[0,2],[1,2],[2,2]])

    def testMoveSnakeAttackHeadToHeadBody(self):
        board = Board(5, 5, [1,2])
        board.snakes[1] = Snake([[2,1],[2,0]], Direction.RIGHT)
        board.snakes[2] = Snake([[2,2],[3,2]], Direction.UP)
        board.moveAllSnakes()
        self.assertEqual(board.snakes[1].body, [[2,1]])
        self.assertEqual(board.snakes[2].body, [[1,2]])

    def testMoveSnakeAttackHeadToHead(self):
        board = Board(5, 5, [1,2])
        board.snakes[1] = Snake([[0,0]], Direction.RIGHT)
        board.snakes[2] = Snake([[0,3],[0,4]], Direction.LEFT)
        board.moveAllSnakes()
        board.moveAllSnakes()
        self.assertEqual(len(board.snakes), 1)
        self.assertEqual(board.snakes[2].length(), 1)

    def testMoveSnakeAttackComplicated(self):
        pass

    def testMaxLength(self):
        pass

    def testGameEnd(self):
        board = Board(5, 5, [3,3])
        board.snakes[1] = Snake([[1,1]], Direction.LEFT)
        board.snakes[2] = Snake([[2,2]], Direction.LEFT)
        board.moveAllSnakes()
        self.assertEquals(len(board.snakes), 2)
        board.moveAllSnakes()
        self.assertEquals(len(board.snakes), 1)
