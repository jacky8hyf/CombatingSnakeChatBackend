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
import traceback
from flask import Flask, render_template
from models.message import Message
from models.invalid_input_error import InvalidInputError
from providers.room_manager import RoomManager
from providers.regex_sockets import RegexSockets
from providers.rest_interface import RestInterface
from providers.time_provider import TimeProvider
from providers.chat_message_handler import ChatMessageHandler
from models.snake_game_models import Board, Direction
from providers.snake_game_execution import SnakeGameExecution
from combating_snake_settings import DEBUG, REDIS_URL

### globals

app = Flask(__name__)
app.debug = DEBUG

sockets = RegexSockets(app)

redis = redis_module.from_url(REDIS_URL)

timeProvider = TimeProvider.create()

restInterface = RestInterface.create()

roomManager = RoomManager.create(
    logger = app.logger,
    redis = redis)

snakeGameExecution = SnakeGameExecution.create(
    restInterface = restInterface,
    roomManager = roomManager,
    timeProvider = timeProvider,
    logger = app.logger)

chatMessageHandler = ChatMessageHandler.create(
    restInterface = restInterface,
    roomManager = roomManager,
    snakeGameExecution = snakeGameExecution)

### rooms route
@sockets.route('/rooms/(\\w+)')
def rooms_route(ws, roomId):
    try:
        message = retrieveNextMessage(ws)
        userId = chatMessageHandler.handleFirstMessage(message, roomId, ws)
    except InvalidInputError as ex:
        ws.send("error " + ex.json())
        return # end this connection if cannot authenticate

    # infinite loop to handle the rest of the messages
    while True:
        message = retrieveNextMessage(ws)
        try:
            if chatMessageHandler.handleOtherMessage(message, roomId, userId):
                break
        except InvalidInputError as ex:
            ws.send("error " + ex.json())
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