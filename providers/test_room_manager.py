__author__ = 'YifanHong'
import unittest
import json
from mock import Mock, patch
from .test_utils import *
from .chat_backend import ChatBackend
from .room_manager import RoomManager


class RoomManagerTestCase(BaseTestCase, unittest.TestCase):
    def setUp(self):
        self.redis = MockRedis.create()
        self.roomManager = RoomManager.create(MockLogger.create(), self.redis, chatBackendProvider = MockChatBackend)
    def tearDown(self):
        pass

    def testSanity(self):
        self.assertIsInstance(self.roomManager.get('meow').chatBackend, Mock)

    def testPublish(self):
        self.roomManager.publish_to_room('roomId','command')
        self.redis.publish.assert_called_with('room_roomId', 'command')
        self.roomManager.publish_to_room('roomId','command', {'foo':'bar'})
        self.redis.publish.assert_called_with('room_roomId', 'command ' + json.dumps({'foo':'bar'}))

    def testListenToRoom(self):
        room = self.roomManager.get('meow')
        self.roomManager.listen_to_room('meow', "fake_ws")
        room.chatBackend.register.assert_called_with("fake_ws")
