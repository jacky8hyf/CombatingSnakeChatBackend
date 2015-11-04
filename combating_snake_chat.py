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
from flask import Flask, render_template
from chat.chat_backend import ChatBackend
from chat.regex_sockets import RegexSockets
from combating_snake_settings import *

app = Flask(__name__)
app.debug = DEBUG

sockets = RegexSockets(app)
redis = redis_module.from_url(REDIS_URL)

chats = ChatBackend(app, redis)
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

@sockets.route('/rooms/(\\d+)')
def rooms_route(ws, roomId):
    while True:
        message = ws.receive()
        ws.send(roomId)