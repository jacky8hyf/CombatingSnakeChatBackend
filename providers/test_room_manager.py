__author__ = 'YifanHong'
import unittest
import json
from kgb import SpyAgency, spy_on
from .test_utils import *
from .chat_backend import ChatBackend
from .room_manager import RoomManager


class RoomManagerTestCase(BaseTestCase, unittest.TestCase):
    def setUp(self):
        self.agency = SpyAgency()
        self.agency.spy_on(ChatBackend.create, call_fake = lambda cls, *args:MockChatBackend.create(*args))
        self.redis = MockRedis()
        self.roomManager = RoomManager.create(None, self.redis)
    def tearDown(self):
        ChatBackend.create.unspy()

    def testSanity(self):
        self.assertIsInstance(self.roomManager.get('meow').chatBackend, MockChatBackend)

    def testPublish(self):
        with spy_on(self.redis.publish, call_original = False):
            self.roomManager.publish_to_room('roomId','command')
            self.assertMethodCalledWith(self.redis.publish, 'room_roomId', 'command')
            self.roomManager.publish_to_room('roomId','command', {'foo':'bar'})
            self.assertMethodCalledWith(self.redis.publish, 'room_roomId', 'command ' + json.dumps({'foo':'bar'}))

    def testListenToRoom(self):
        room = self.roomManager.get('meow')
        with spy_on(room.chatBackend.register, call_original = False):
            self.roomManager.listen_to_room('meow', "fake_ws")
            self.assertMethodCalledWith(room.chatBackend.register, "fake_ws");
