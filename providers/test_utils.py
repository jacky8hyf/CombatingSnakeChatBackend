from unittest import TestCase
import unittest
from mock import Mock
from .chat_backend import ChatBackend
from .room_manager import RoomManager
from .time_provider import TimeProvider

class BaseTestCase(TestCase):
    pass


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
    def create(cls, *args, **kwargs): return Mock()

class MockRedis(object):
    @classmethod
    def create(cls, *args, **kwargs): return Mock(spec = cls)
    def publish(self, chan, msg): pass
