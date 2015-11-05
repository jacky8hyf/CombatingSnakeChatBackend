from threading import Lock
from .chat_backend import ChatBackend
import json

class ChatBackendsManager(object):
    '''
    A synchronized manager of ChatBackends. Each ChatBackend has a unique roomId
    associated with it.
    '''
    def __init__(self, logger, redis):
        self.backends = {}
        self.logger = logger
        self.redis = redis
        self.lock = Lock()

    def get(self, roomId):
        with self.lock:
            if roomId not in self.backends:
                cb = ChatBackend(self.logger, self.redis)
                cb.subscribe(ChatBackendsManager.get_channel(roomId))
                cb.start()
                self.backends[roomId] = cb
            return self.backends[roomId]


    def close(self, roomId):
        with self.lock:
            if roomId in self.backends:
                self.backends[roomId] = None

    def publish_to_room(self, roomId, command, data = None):
        if data is not None:
            msg = "{} {}".format(command, json.dumps(data))
        else:
            msg = command
        self.redis.publish(ChatBackendsManager.get_channel(roomId), msg)

    def listen_to_room(self, roomId, ws):
        self.get(roomId).register(ws)

    @staticmethod
    def get_channel(roomId):
        return "room_{}".format(roomId)