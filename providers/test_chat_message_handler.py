from unittest import TestCase
import json, hashlib, time, threading
from mock import patch
import redis as redis_module
from models.invalid_input_error import InvalidInputError
from providers.test_utils import *
from providers.snake_game_execution import SnakeGameExecution
from providers.chat_message_handler import ChatMessageHandler
from combating_snake_settings import *
from models.message import Message

class ChatMessageHandlerTestCase(BaseTestCase):
    def setUp(self):
        self.restInterface = Mock(wraps = RestInterface.create())
        self.redis = MockRedis.create()
        self.logger = MockLogger.create()
        self.roomManager = Mock(wraps = RoomManager.create(logger = self.logger, redis = self.redis))
        self.deleteAllUsers(self.restInterface)
        self.users = [self.createUser(self.restInterface) for _ in range(MAX_MEMBERS_IN_ROOM)]
            # tuple of (userId, sessionId)
        self.roomOwner = self.users[0]
        self.roomId = self.createRoom(self.restInterface, self.roomOwner[1])
        self.timeProvider = MockTimeProvider.create()
        self.snakeGameExecution = SnakeGameExecution.create(
            restInterface = self.restInterface,
            roomManager = self.roomManager,
            timeProvider = self.timeProvider,
            logger = self.logger)

        self.chatMessageHandler = ChatMessageHandler.create(
            restInterface = self.restInterface,
            roomManager = self.roomManager,
            snakeGameExecution = self.snakeGameExecution)


    def testHandleFirstMessage(self):
        with patch.object(self.roomManager, 'listen_to_room', Mock(self.fake)), \
            patch.object(self.roomManager, 'publish_to_room', Mock(self.fake)):
            ws = MockWebsocket.create()

            # test join
            userId, sessionId = self.users[1]
            msg = self.constructAuth('join', userId, sessionId)
            self.chatMessageHandler.handleFirstMessage(msg, self.roomId, ws)
            self.roomManager.listen_to_room.assert_called_with(self.roomId, ws)
            self.assertTrue(self.roomManager.publish_to_room.called)
            self.restInterface.join_and_get_room.assert_called_with(self.roomId, userId)

            # test reconn
            self.roomManager.reset_mock()
            self.restInterface.reset_mock()
            msg = self.constructAuth('reconn', userId, sessionId)
            self.chatMessageHandler.handleFirstMessage(msg, self.roomId, ws)
            self.roomManager.listen_to_room.assert_called_with(self.roomId, ws)
            self.roomManager.publish_to_room.assert_not_called()
            self.restInterface.join_and_get_room.assert_not_called()

            # test reconn of non member
            self.roomManager.reset_mock()
            self.restInterface.reset_mock()
            userId, sessionId = self.users[2]
            msg = self.constructAuth('reconn', userId, sessionId)
            with self.assertRaises(InvalidInputError) as cm:
                self.chatMessageHandler.handleFirstMessage(msg, self.roomId, ws)
            self.assertIn('You are not in the room', cm.exception.json())
            self.roomManager.listen_to_room.assert_not_called()
            self.roomManager.publish_to_room.assert_not_called()
            self.restInterface.join_and_get_room.assert_not_called()

            # TODO Test on non-member joining a full room -> error
            # TODO Test on member joining a full room -> no effect

    def testHandleStartQuit(self):
        ws = MockWebsocket.create()
        userId, sessionId = self.users[1]
        msg = self.constructAuth('join', userId, sessionId)
        self.chatMessageHandler.handleFirstMessage(msg, self.roomId, ws)

        with self.assertRaises(InvalidInputError) as cm: # member cannot start the game
            self.chatMessageHandler.handleOtherMessage(Message.create('start'), self.roomId, userId)
        self.assertIn('permission', cm.exception.json())

        # owner should be able to start the game
        self.chatMessageHandler.handleOtherMessage(Message.create('start'), self.roomId, self.roomOwner[0])

        # owner quits the game
        self.chatMessageHandler.handleOtherMessage(Message.create('quit'), self.roomId, self.roomOwner[0])
        self.assertNotEquals(self.roomOwner[0], self.restInterface.get_room(self.roomId)['creator']['userId'])

        self.chatMessageHandler.handleOtherMessage(Message.create('quit'), self.roomId, userId)
        with self.assertRaises(Exception) as cm:
            self.restInterface.get_room(self.roomId)
        self.assertIn('Not Found Room', str(cm.exception))

    def constructAuth(self, command, userId, sessionId):
        ts = int(time.time() * 1000)
        return Message.create(command,{
                    "userId":userId,
                    "ts":ts,
                    "auth":hashlib.sha256("{}:{}:{}".format(sessionId, userId, ts))})
    def fake(self, *args, **kwargs):
        pass