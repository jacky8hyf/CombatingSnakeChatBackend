from unittest import TestCase
import unittest
import random
from mock import Mock
from geventwebsocket.websocket import WebSocket
from .chat_backend import ChatBackend
from .room_manager import RoomManager
from .time_provider import TimeProvider
from .rest_interface import RestInterface

class BaseTestCase(TestCase):
    '''
    Test of rest_interface.py.
    It will connect to http://localhost:8080 as defined
    in combating_snake_settings.py. So set up the django server
    running on that port before running this test.
    '''
    def createUser(self, restInterface):
        userResponse = restInterface.send_request('post', '/users', json = {"username":
            "test_user_" + str(random.getrandbits(64)),
            "password":"password"})
        return userResponse['userId'], userResponse['sessionId']

    def createRoom(self, restInterface, sessionId):
        roomResponse = restInterface.send_request('post', '/rooms',
            headers={'X-Snake-Session-Id':sessionId})
        return roomResponse['roomId']


class MockChatBackend(object):
    @classmethod
    def create(cls, *args, **kwargs): return Mock(spec = ChatBackend)

class MockTimeProvider(TimeProvider):
    @classmethod
    def create(cls, *args, **kwargs): return cls(*args, **kwargs)
    def __init__(self, *args, **kwargs): self._time = 0
    def time(self): return self._time
    def sleep(self, secs): self._time+=secs

class MockLogger(object):
    @classmethod
    def create(cls, *args, **kwargs): return cls(*args, **kwargs)
    def info(self, msg):
        print(msg)

class MockRedis(object):
    @classmethod
    def create(cls, *args, **kwargs): return Mock(wrap = MockRedis())
    def publish(self, chan, msg):
        print("[REDIS] {}: {}".format(chan, msg))

# class MockRoomManager(RoomManager):
#     @classmethod
#     def create(cls, *args, **kwargs): return Mock(spec = RoomManager)

# class MockRestInterface(RestInterface):
#     @classmethod
#     def create(cls, *args, **kwargs): return Mock(spec = RestInterface)

class MockWebsocket(object):
    @classmethod
    def create(cls, *args, **kwargs): return Mock(spec = WebSocket)
