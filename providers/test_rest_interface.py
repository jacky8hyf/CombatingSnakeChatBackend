
from time import time
from hashlib import sha256
import random

from combating_snake_settings import *
from .test_utils import *

from .rest_interface import RestInterface

print("RestInterfaceTestCase: Testing against {}".format(REST_HOST))

class RestInterfaceTestCase(BaseTestCase):
    '''
    Test of rest_interface.py.
    It will connect to http://localhost:8080 as defined
    in combating_snake_settings.py. So set up the django server
    running on that port before running this test.
    '''
    def createUser(self):
        userResponse = self.restInterface.send_request('post', '/users', json = {"username":
            "test_user_" + str(random.randint(1,10000)),
            "password":"password"})
        return userResponse['userId'], userResponse['sessionId']

    def setUp(self):
        self.restInterface = RestInterface.create()

        self.userId, self.sessionId = self.createUser()
        self.bobId, self.bobSession = self.createUser()

        roomResponse = self.restInterface.send_request('post', '/rooms',
            headers={'X-Snake-Session-Id':self.sessionId})
        self.roomId = roomResponse['roomId']

    def tearDown(self):
        self.restInterface.send_request('delete', '/users/' + self.userId);

    def testAuthenticateUser(self):
        ts = int(time() * 1000)
        rawAuth = "{}:{}:{}".format(self.sessionId, self.userId, ts)
        auth = sha256(rawAuth).hexdigest();
        self.assertTrue(self.restInterface.authenticate_user(
            self.userId, ts, auth), "authenticate_user returns false")

    def testJoinExitRoom(self):
        roomResponse = self.restInterface.join_and_get_room(self.roomId, self.bobId);
        self.assertEquals(self.bobId, roomResponse['members'][0]['userId'])
        self.assertEquals(roomResponse, self.restInterface.get_room(self.roomId))
        roomResponse = self.restInterface.exit_and_get_room(self.roomId, self.bobId);
        self.assertFalse(roomResponse['members'])

    def testStartRoom(self):
        self.restInterface.start_room_if_created_by(self.roomId, self.bobId)
        self.assertEquals(STATUS_WAITING, self.restInterface.get_room(self.roomId)['status'])
        self.restInterface.start_room_if_created_by(self.roomId, self.userId)
        self.assertEquals(STATUS_PLAYING, self.restInterface.get_room(self.roomId)['status'])
