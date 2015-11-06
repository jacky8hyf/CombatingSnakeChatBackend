from unittest import TestCase
from .test_utils import *
from combating_snake_settings import *
from .snake_game_execution import SnakeGameExecution

print("RestInterfaceTestCase: Testing against {}".format(REST_HOST))

class SnakeGameExecutionTest(BaseTestCase):
    def setUp(self):
        self.timeProvider = MockTimeProvider.create()
        self.logger = MockLogger.create()
        self.restInterface = RestInterface.create() # true rest interface
        self.roomManager = RoomManager.create(logger = self.logger, redis = MockRedis.create()) # true room manager

        self.snakeGameExecution = SnakeGameExecution.create(
            restInterface = self.restInterface,
            roomManager = self.roomManager,
            timeProvider = self.timeProvider,
            logger = self.logger)

        self.users = [self.createUser(self.restInterface) for _ in range(MAX_MEMBERS_IN_ROOM)]
            # tuple of (userId, sessionId)
        self.roomOwner = self.users[0]
        self.roomId = self.createRoom(self.restInterface, self.roomOwner[1])
        for user in self.users:
            self.restInterface.join_and_get_room(self.roomId, user[0])

    def testGameLoop(self):
        random.seed(1)
        self.snakeGameExecution.start(self.roomId) # FIXME this is not a real test, just for experiment
