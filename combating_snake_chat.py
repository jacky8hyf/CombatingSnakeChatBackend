# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging
import redis as redis_module
import gevent
import json
import threading
from flask import Flask, render_template
from models.message import Message
from providers.chat_backend import ChatBackend
from providers.chat_backends_manager import ChatBackendsManager
from providers.regex_sockets import RegexSockets
from providers.rest_interface import RestInterface
from providers.time_provider import TimeProvider
from providers.snake_game import Board, Direction
from combating_snake_settings import *

### globals

app = Flask(__name__)
app.debug = DEBUG

sockets = RegexSockets(app)

redis = redis_module.from_url(REDIS_URL)

time = TimeProvider()

cbmanager = ChatBackendsManager(app.logger, redis)

### game loop
def gameloop(roomId=None, *args, **kwargs):
    
    count = 100
    while True:
        # update game state
        print("tick {}".format(count))
        count -= 1 # FIXME: dumb game here
        cbmanager.publish_to_room(roomId, 'ping', {'count':count})
        if count <= 0:
            break

        time.sleep(.5) # sleep for .5 seconds

### rooms route
@sockets.route('/rooms/(\\d+)')
def rooms_route(ws, roomId):

    error = lambda message: 'error {}'.format(json.dumps({"msg": message}))

    def authenticate(authdata):
        if 'userId' not in authdata or 'ts' not in authdata or 'auth' not in authdata:
            ws.send(error("missing keys"))
            return None
        if RestInterface.authenticate_user(authdata['userId'], authdata['ts'], authdata['auth']):
            return authdata['userId']
        ws.send(error('cannnot authenticate'))
        return None

    message = Message.from_str(ws.receive())
    if not message:
        return

    # consume the first message; require it to be join or reconn
    if (message.command == 'join' or message.command == 'reconn') and message.data:
        userId = authenticate(message.data)
        if not userId: return
        cbmanager.listen_to_room(roomId, ws)

        if message.command == 'join':
            try:
                data = RestInterface.join_and_get_room(roomId, userId)
            except Exception as ex:
                ws.send(error(str(ex)))
            cbmanager.publish_to_room(roomId, "room", data)
    else:
        ws.send(error('requires a join or reconn with authdata'))
        return # drop this connection

    # infinite loop to handle the rest of the messages
    while True:
        message = None
        try:
            message = Message.from_str(ws.receive())
        except:
            return # end this connection

        if message is None:
            continue

        if message.command == 'start':
            if not RestInterface.start_room_if_created_by(roomId, userId):
                ws.send(error('You don\'t have permission to start the game'))
                continue
            threading.Thread(target=gameloop,kwargs={"roomId": roomId}).start()
            continue
        if message.command in ('u','d','l','r'):
            # FIXME sets appropriate game state
            continue
        if message.command == 'quit':
            data = RestInterface.exit_and_get_room(roomId, userId)
            cbmanager.publish_to_room(roomId, "room", data)
            return # ends this connection

        ws.send(error('I don\' recognize this command {}'.format(message.command)))

