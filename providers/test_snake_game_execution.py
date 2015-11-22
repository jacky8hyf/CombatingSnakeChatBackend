from unittest import TestCase
from mock import patch
import time
from .test_utils import *
from combating_snake_settings import *
from .snake_game_execution import SnakeGameExecution
from models.snake_game_models import Direction
from providers.time_provider import TimeProvider

print("SnakeGameExecutionTestCase: Testing against {}".format(REST_HOST))

class SnakeGameExecutionTestCase(BaseTestCase):
    def setUp(self):
        self.timeProvider = MockTimeProvider.create()
        self.logger = MockLogger.create()
        self.restInterface = RestInterface.create() # true rest interface
        self.roomManager = RoomManager.create(logger = self.logger, redis = MockRedis.create()) # true room manager

        self.snakeGameExecution = Mock(wraps = SnakeGameExecution.create(
            restInterface = self.restInterface,
            roomManager = self.roomManager,
            timeProvider = self.timeProvider,
            logger = self.logger))

    def setUpUsersAndRoom(self, numUsers):
        self.deleteAllUsers(self.restInterface)
        self.users = [self.createUser(self.restInterface) for _ in range(numUsers)]
            # tuple of (userId, sessionId)
        self.roomOwner = self.users[0]
        self.roomId = self.createRoom(self.restInterface, self.roomOwner[1])
        for user in self.users:
            self.restInterface.join_and_get_room(self.roomId, user[0])

    def testGameLoop(self): # mainly an experiment, not a test.
        random.seed(1)
        self.setUpUsersAndRoom(2)

        board, membersDict = self.snakeGameExecution.prepare(self.roomId)
        for userId, sessionId in self.users:
            self.roomManager.get(self.roomId).board.onKeyStroke(userId, Direction.UP)
        while True:
            # print(self.roomManager.get(self.roomId).board.getGameState())
            self.timeProvider.sleep(.5)
            snakes = self.snakeGameExecution.tickOnce(self.roomId, board, membersDict)
            if snakes is not None:
                self.assertLessEqual(len(self.roomManager.get(self.roomId).board.snakes), 1)
                winner = snakes[0] if snakes else None
                # print winner
                break
            else:
                self.assertGreater(len(self.roomManager.get(self.roomId).board.snakes), 1)



