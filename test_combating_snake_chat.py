from unittest import TestCase
import json, hashlib, time, threading
from .test_utils import *
from .combating_snake_settings import *

from .combating_snake_chat import * # initualize Dependencies and set up routes

class ChatTestCase(BaseTestCase):
    def setUp(self):
        self.users = [self.createUser(self.restInterface) for _ in range(MAX_MEMBERS_IN_ROOM)]
            # tuple of (userId, sessionId)
        self.roomOwner = self.users[0]
        self.roomId = self.createRoom(self.restInterface, self.roomOwner[1])
        for user in self.users:
            self.restInterface.join_and_get_room(self.roomId, user[0])

    def testRoomsRoute(self):
        return # FIXME this test is not finalized
        for userId, sessionId in self.users:
            ts = time.time() * 1000
            joinmsg = "join {}".format(
                json.dumps({
                    "userId":userId,
                    "ts":ts,
                    "auth":hashlib.sha256("{}:{}:{}".format(sessionId, userId, ts))}))





