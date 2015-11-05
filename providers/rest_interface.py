import requests
form combating_snake_settings import *

# this is the same constants for models.py in CombatingSnake REST API backend.
STATUS_PLAYING = 1
STATUS_WAITING = 0

class RestInterface(object):
    @classmethod
    def authenticate_user(cls,userId, ts, auth):
        '''
        Return true if the user should be authenticated, false otherwise.
        '''
        try:
            cls.send_request('post', '/users/{}/authenticate'.format(userId),
                json = {'ts':ts,'auth':auth},
                expect_json_response = False)
        except:
            return False

    @classmethod
    def join_and_get_room(roomId, userId):
        '''
        Put user in the room and return the new room data (a dictionary).
        Raise an exception if the user fails to do so.
        '''
        return cls.send_request('put','/rooms/{}/members/{}'.format(roomId, userId),
            params={'return-room':True})

    @classmethod
    def exit_and_get_room(cls, roomId, userId):
        '''
        Kick user out of the room and return the new room data (a dictionary).
        Raise an exception if the user fails to do so.
        '''
        return cls.send_request('delete','/rooms/{}/members/{}'.format(roomId, userId),
            params={'return-room':True})

    @staticmethod
    def start_room_if_created_by(roomId, userId):
        '''
        Start the game in the room and return true iff room exists and is
        created by user. Return false otherwise.
        '''
        try:
            cls.send_request('put','/rooms/{}',
                json={'status':STATUS_PLAYING},
                expect_json_response=False)
        except:
            return False

    @classmethod
    def send_request(cls, method, path,
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
            response = getattr(requests, method)(
                REST_HOST + path,
                **kwargs)
            response.raise_for_status()
            if expect_json_response:
                return response.json()
        except:
            raise Exception("server returns {} {}".format(response.status_code if response else None,
                response.content if response else None))