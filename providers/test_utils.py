from unittest import TestCase
import unittest
from chat_backend import ChatBackend
from room_manager import RoomManager
from kgb import SpyAgency, spy_on

class BaseTestCase(TestCase):
    def assertMethodCalledWith(self, func, *args, **kwargs):
        self.assertTrue(func.called_with(*args, **kwargs),
            "{} is not called with ({}, {})".format(func, args, kwargs))
    def assertFunctionCalledWith(self, func, *args, **kwargs):
        self.assertTrue(func.spy.called_with(*args, **kwargs),
            "{} is not called with ({}, {})".format(func, args, kwargs))


class MockChatBackend(ChatBackend):
    @classmethod
    def create(cls, *args):
        return cls(*args)
    def __init__(self, logger, redis): pass
    def __iter_data(self): pass
    def subscribe(self, channel): pass
    def register(self, client): pass
    def send(self, client, data): pass
    def run(self):pass
    def start(self):pass

class MockRedis(object):
    def publish(self, chan, msg): pass
