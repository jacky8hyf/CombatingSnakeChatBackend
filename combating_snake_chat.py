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
from chat.chat_backend import ChatBackend
from chat.chat_backends_manager import ChatBackendsManager
from chat.regex_sockets import RegexSockets
from providers.rest_interface import RestInterface
from providers.time_provider import TimeProvider
from chat.message import Message
from combating_snake_settings import *

### globals

app = Flask(__name__)
app.debug = DEBUG

sockets = RegexSockets(app)

redis = redis_module.from_url(REDIS_URL)

time = TimeProvider()

## original chat demo code. placed here for reference; need to be deleted later

chats = ChatBackend(app.logger, redis)
chats.subscribe(REDIS_CHAN)
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while True:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            redis.publish(REDIS_CHAN, message)

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while True:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)

####################################################
#            Combating snake logic                 #
####################################################

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
            data = RestInterface.join_and_get_room(roomId, userId)
            cbmanager.publish_to_room(roomId, "room", data)
    else:
        ws.send(error('requires a join or reconn with authdata'))
        return # drop this connection

    # infinite loop to handle the rest of the messages
    while True:
        message = Message.from_str(ws.receive())

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

