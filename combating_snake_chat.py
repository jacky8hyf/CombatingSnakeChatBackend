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
from models.invalid_input_error import InvalidInputError
from providers.room_manager import RoomManager
from providers.regex_sockets import RegexSockets
from providers.rest_interface import RestInterface
from providers.time_provider import TimeProvider
from models.snake_game_models import Board, Direction
from providers.snake_game_execution import SnakeGameExecution
from combating_snake_settings import DEBUG, REDIS_URL

### globals

app = Flask(__name__)
app.debug = DEBUG

sockets = RegexSockets(app)

redis = redis_module.from_url(REDIS_URL)

timeProvider = TimeProvider.create()

roomManager = RoomManager.create(
    logger = app.logger,
    redis = redis)

restInterface = RestInterface.create()

snakeGameExecution = SnakeGameExecution.create(
    restInterface = restInterface,
    roomManager = roomManager,
    timeProvider = timeProvider,
    logger = app.logger)

### rooms route
@sockets.route('/rooms/(\\w+)')
def rooms_route(ws, roomId):
    try:
        message = retrieveNextMessage(ws)
        userId = handleFirstMessage(message, roomId, ws)
    except InvalidInputError as ex:
        ws.send(ex.json())
        return # end this connection if cannot authenticate

    # infinite loop to handle the rest of the messages
    while True:
        message = retrieveNextMessage(ws)
        try:
            if handleOtherMessage(message, roomId, userId):
                break
        except InvalidInputError as ex:
            ws.send(ex.json())
            continue

### helper methods

def retrieveNextMessage(ws):
    '''
    Retrieve next non-trivial message. Raise an exception if socket ends
    '''
    message = None
    while not message:
        message = Message.from_str(ws.receive())
    return message

def handleFirstMessage(message, roomId, ws):
    '''
    Handles the first message. Returns userId if authentication is successful.
    '''
    # consume the first message; require it to be join or reconn
    if (message.command != 'join' and message.command != 'reconn') or not message.data:
        raise InvalidInputError('requires a join or reconn with authdata')

    authdata = message.data
    if 'userId' not in authdata or 'ts' not in authdata or 'auth' not in authdata:
        raise InvalidInputError("missing keys")
    if not restInterface.authenticate_user(authdata['userId'], authdata['ts'], authdata['auth']):
        raise InvalidInputError('cannnot authenticate')
    userId = authdata['userId']
    room = None
    if message.command == 'reconn':
        try:
            room = restInterface.get_room(roomId)
        except Exception as ex:
            raise InvalidInputError(str(ex))
        if room.get('creator')['userId'] == userId or \
            userId in [e['userId'] for e in room.get('members')]:
            roomManager.listen_to_room(roomId, ws)
            ws.send('room {}'.format(json.dumps(room)))
        else:
            raise InvalidInputError('You are not in the room {}'.format(roomId))
    elif message.command == 'join':
        try:
            room = restInterface.join_and_get_room(roomId, userId)
        except Exception as ex: # the user cannot join the room
            raise InvalidInputError(str(ex))
        roomManager.listen_to_room(roomId, ws)
        roomManager.publish_to_room(roomId, "room", room)
    return userId

def handleOtherMessage(message, roomId, userId):
    '''
    Handles the rest of the messages. Assume game starts.
    Raise an exception if any error. Return True if the connection should end.
    '''
    if message.command == 'start':
        if not restInterface.start_room_if_created_by(roomId, userId):
            raise InvalidInputError('You don\'t have permission to start the game')
        threading.Thread(target=snakeGameExecution.start,kwargs={"roomId": roomId}).start()
        return False
    if message.command in ('u','d','l','r'):
        board = roomManager.get(roomId).board
        if not board:
            raise InvalidInputError('Game not started yet.')
        board.changeDirection(userId, Direction.fromStr(message.command))
        return False
    if message.command == 'quit':
        data = restInterface.exit_and_get_room(roomId, userId)
        roomManager.publish_to_room(roomId, "room", data)
        return True
    raise InvalidInputError('I don\' recognize this command {}'.format(message.command))