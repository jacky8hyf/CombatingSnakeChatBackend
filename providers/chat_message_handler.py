import json
import traceback
import threading
import time
from models.snake_game_models import Direction
from models.invalid_input_error import InvalidInputError

class ChatMessageHandler(object):

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __init__(self, restInterface, roomManager, snakeGameExecution):
        self.restInterface = restInterface
        self.roomManager = roomManager
        self.snakeGameExecution = snakeGameExecution

    def handleFirstMessage(self, message, roomId, ws):
        '''
        Handles the first message. Returns userId if authentication is successful.
        '''
        # consume the first message; require it to be join or reconn
        if (message.command != 'join' and message.command != 'reconn') or not message.data:
            raise InvalidInputError('requires a join or reconn with authdata')

        authdata = message.data
        if 'userId' not in authdata or 'ts' not in authdata or 'auth' not in authdata:
            raise InvalidInputError("missing keys")
        if not self.restInterface.authenticate_user(authdata['userId'], authdata['ts'], authdata['auth']):
            raise InvalidInputError('cannnot authenticate')
        userId = authdata['userId']
        room = None
        if message.command == 'reconn':
            try:
                room = self.restInterface.get_room(roomId)
            except Exception as ex:
                raise InvalidInputError(str(ex))
            if room.get('creator')['userId'] == userId or \
                userId in [e['userId'] for e in room.get('members')]:
                self.roomManager.listen_to_room(roomId, ws)
                ws.send('room {}'.format(json.dumps(room)))
            else:
                raise InvalidInputError('You are not in the room {}'.format(roomId))
        elif message.command == 'join':
            try:
                room = self.restInterface.join_and_get_room(roomId, userId)
            except Exception as ex: # the user cannot join the room
                raise InvalidInputError(str(ex))
            self.roomManager.listen_to_room(roomId, ws)
            self.roomManager.publish_to_room(roomId, "room", room)
        return userId

    def handleOtherMessage(self, message, roomId, userId):
        '''
        Handles the rest of the messages. Assume game starts.
        Raise an exception if any error. Return True if the connection should end.
        '''
        if message.command == 'start':
            if not self.restInterface.start_room_if_created_by(roomId, userId):
                raise InvalidInputError('You don\'t have permission to start the game')
            threading.Thread(target=self.snakeGameExecution.start,kwargs={"roomId": roomId}).start()
            return False
        if message.command in ('u','d','l','r'):
            board = self.roomManager.get(roomId).board
            if not board:
                raise InvalidInputError('Game not started yet.')
            board.onKeyStroke(userId, Direction.from_str(message.command))
            return False
        if message.command == 'quit':
            data = self.restInterface.exit_and_get_room(roomId, userId)
                # could be empty if room is deleted
            self.roomManager.publish_to_room(roomId, "room", data)
            return True
        raise InvalidInputError('I don\' recognize this command {}'.format(message.command))