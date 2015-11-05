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
from providers.room_manager import RoomManager
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

roomManager = RoomManager(app.logger, redis)

### game loop
def gameloop(roomId=None, *args, **kwargs):
    # prepare the game
    if not roomId:
        app.logger.info('[GameLoop] No room id.')
        return
    room = RestInterface.get_room(roomId)
    members = room.get('members')
    creator = room.get('creator')
    if not members or not creator:
        app.logger.info('[GameLoop] no members or creator key')
        return
    members.append(creator)
    membersDict = {}
    for member in members: membersDict[member['userId']] = member;
    memberIds = [member.get('userId') for member in members]
    if len(memberIds) > MAX_MEMBERS_IN_ROOM:
        roomManager.publish_to_room(roomId, error('Too many in the room, cannot start'))
        return
    board = roomManager.get(roomId).board = Board(BOARD_COLUMNS, BOARD_ROWS, memberIds)

    # notify everybody: game starts here!
    roomManager.publish_to_room(roomId, 'start')

    # infinite game loop
    while True:
        time.sleep(GAME_TICK_TIME)
        board.moveAllSnakes()
        roomManager.publish_to_room(roomId, 'g', board.getGameState())
        snakes = board.snakes
        if len(snakes) <= 1:
            winner = snakes[0] if len(snakes) == 1 else None
            winner = membersDict.get(winner) if winner else None
            roomManager.publish_to_room(roomId, 'end', {
                'winner': winner
                } if winner else None)
            break;

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
        roomManager.listen_to_room(roomId, ws)

        if message.command == 'join':
            try:
                data = RestInterface.join_and_get_room(roomId, userId)
            except Exception as ex:
                ws.send(error(str(ex)))
            roomManager.publish_to_room(roomId, "room", data)
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
            board = roomManager.get(roomId).board
            if board:
                board.changeDirection(userId, Direction.fromStr(message.command))
            else:
                ws.send(error('Game not started yet.'))
            continue
        if message.command == 'quit':
            data = RestInterface.exit_and_get_room(roomId, userId)
            roomManager.publish_to_room(roomId, "room", data)
            return # ends this connection

        ws.send(error('I don\' recognize this command {}'.format(message.command)))

