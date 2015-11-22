import traceback
import requests
from combating_snake_settings import *

class RestInterface(object):

    @classmethod
    def create(cls, *args, **kwargs):
        '''
        Create a RestInterface object. (Could be a mock)
        '''
        return cls(*args, **kwargs)

    def authenticate_user(self, userId, ts, auth):
        '''
        Return true if the user should be authenticated, false otherwise.
        '''
        if BYPASS_AUTHENTICATION:
            return True # FIXME bypassing authentication
        try:
            self.send_request('post', '/users/{}/authenticate'.format(userId),
                json = {'ts':ts,'auth':auth},
                expect_json_response = False)
            return True
        except:
            return False

    def join_and_get_room(self, roomId, userId):
        '''
        Put user in the room and return the new room data (a dictionary).
        Raise an exception if the user fails to do so.
        '''
        return self.send_request('put','/rooms/{}/members/{}'.format(roomId, userId),
            params={'return-room':True})

    def exit_and_get_room(self, roomId, userId):
        '''
        Kick user out of the room and return the new room data (a dictionary).
        Raise an exception if the user fails to do so.
        '''
        return self.send_request('delete','/rooms/{}/members/{}'.format(roomId, userId),
            params={'return-room':True})

    def get_room(self, roomId):
        '''
        Get the room
        '''
        return self.send_request('get','/rooms/{}'.format(roomId),
            params={'members': True,
                    'member-profile': True,
                    'creator-profile': True})

    def start_room_if_created_by(self, roomId, userId):
        '''
        Start the game in the room and return true iff room exists and is
        created by user. Return false otherwise.
        '''
        try:
            self.send_request('put','/rooms/{}'.format(roomId),
                json={'status':STATUS_PLAYING, 'proposer': userId},
                expect_json_response=False)
            return True
        except:
            return False

    def ends_game(self, roomId):
        '''
        Ends the game
        '''
        self.send_request('put','/rooms/{}'.format(roomId),
                json={'status':STATUS_WAITING},
                expect_json_response=False)

    def update_scores(self, players, winner = None):
        '''
        Update scores for players and winner. Return true if successful, false
        otherwise.
        '''
        obj = {'players':players}
        if winner: obj['winner'] = winner;
        try:
            self.send_request('put','/users/scores',
                json = obj,
                expect_json_response=False)
            return True
        except:
            return False

    def send_request(self, method, path,
        expect_json_response=True, **kwargs):
        '''
        helper method for sending requests. return kv pair of response.
        raise exception on error http status.
        '''
        response = None
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['X-Snake-Master-Key'] = MASTER_KEY
        try:
            response = getattr(requests, method.lower())(
                REST_HOST + path,
                **kwargs)
            response.raise_for_status()
            if expect_json_response:
                return response.json()
        except:
            # traceback.print_exc();
            raise Exception("server returns {} {}".format(response.status_code if response is not None else None,
                response.content if response is not None else None))