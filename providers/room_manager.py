from threading import Lock
from .chat_backend import ChatBackend
import json

class Room(object):
    def __init__(self):
        self.board = None
        self.chatBackend = None

class RoomManager(object):

    @classmethod
    def create(cls, *args):
        '''
        Create a RoomManager object. (Could be a mock)
        '''
        return cls(*args)

    '''
    A synchronized manager of ChatRooms. Each ChatBackend has a unique roomId
    associated with it.
    '''
    def __init__(self, logger, redis):
        self.rooms = {}
        self.logger = logger
        self.redis = redis
        self.lock = Lock()

    def get(self, roomId):
        with self.lock:
            if roomId not in self.rooms:
                cb = ChatBackend.create(self.logger, self.redis)
                cb.subscribe(RoomManager.get_channel(roomId))
                cb.start()
                room = Room()
                room.chatBackend = cb
                self.rooms[roomId] = room
            return self.rooms[roomId]


    def close(self, roomId):
        with self.lock:
            if roomId in self.rooms:
                self.rooms[roomId] = None

    def publish_to_room(self, roomId, command, data = None):
        if data is not None:
            msg = "{} {}".format(command, json.dumps(data))
        else:
            msg = command
        self.redis.publish(RoomManager.get_channel(roomId), msg)

    def listen_to_room(self, roomId, ws):
        self.get(roomId).chatBackend.register(ws)

    @staticmethod
    def get_channel(roomId):
        return "room_{}".format(roomId)