# This code is copied from https://devcenter.heroku.com/articles/python-websockets

import os
import logging
import gevent
from flask import Flask, render_template
from combating_snake_settings import *

class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    @classmethod
    def create(cls, *args):
        '''
        Create a new ChatBackend object (could be a mock depending on the context)
        '''
        return cls(*args)

    def __init__(self, logger, redis):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.logger = logger

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                self.logger.info(u'Sending message: {}'.format(data))
                yield data

    def subscribe(self, channel):
        self.pubsub.subscribe(channel)

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)


