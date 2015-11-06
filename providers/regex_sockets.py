from flask_sockets import Sockets
import re

class RegexSocketMiddleware(object):
    def __init__(self, wsgi_app, socket):
        self.ws = socket
        self.app = wsgi_app

    def __call__(self, environ, start_response):
        if 'wsgi.websocket' not in environ:
            return self.app(environ, start_response) # this is not a websocket request from the client

        path = environ['PATH_INFO']

        for pattern, handler in self.ws.url_map.items():
            match_object = re.match(pattern, path)
            if match_object:
                environment = environ['wsgi.websocket']

                handler(environment, *match_object.groups())
                return []
        return self.app(environ, start_response)

class RegexSockets(Sockets):
    def init_app(self, app):
        app.wsgi_app = RegexSocketMiddleware(app.wsgi_app, self)
