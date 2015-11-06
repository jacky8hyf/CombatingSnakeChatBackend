
from time import time
from hashlib import sha256
import random
import requests
import mock

from combating_snake_settings import *
from .test_utils import *

from .rest_interface import RestInterface

print("RestInterfaceTestCase: Testing against {}".format(REST_HOST))

class RestInterfaceTestCase(BaseTestCase):

    def setUp(self):
        self.restInterface = RestInterface.create()

        self.userId, self.sessionId = self.createUser(self.restInterface)
        self.bobId, self.bobSession = self.createUser(self.restInterface)

        self.roomId = self.createRoom(self.restInterface, self.sessionId)

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

    def testNoMasterKey(self):
        restInterface = Mock(wraps = self.restInterface)
        with mock.patch.object(self.restInterface, 'send_request', self.fake_send_request):
            ts = int(time() * 1000)
            rawAuth = "{}:{}:{}".format(self.sessionId, self.userId, ts)
            auth = sha256(rawAuth).hexdigest();
            self.assertFalse(self.restInterface.authenticate_user(
                self.userId, ts, auth), "authenticate_user returns true without master key")

    def fake_send_request(self, method, path, **kwargs):
        '''
        helper method for sending requests. return kv pair of response.
        raise exception on error http status.
        '''
        response = None
        try:
            response = getattr(requests, method.lower())(
                REST_HOST + path,
                **kwargs)
            response.raise_for_status()
        except:
            raise Exception("server returns {} {}".format(response.status_code if response is not None else None,
                response.content if response is not None else None))