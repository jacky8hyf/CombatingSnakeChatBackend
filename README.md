# Combating Snake Chat Backend
This Flask application is aimed to provide websocket backend for the CombatingSnake
project.

## Set it up
1. Clone the repository
2. `virtualenv venv`
3. `source venv/bin/activate`
4. `[sudo] pip install -r requirements.txt`

## Run it locally
1. Clone the [Django app](/jacky8hyf/CS169CombatingSnake)
2. In the root of that app, run: `[PORT=8080] heroku local`; you need to specify
   the port manually if it is not 8080 by default. If you don't want it to run on
   port 8080, you need to specify the `REST_HOST` environment variable below.
3. Simply run `[REST_HOST=http://localhost:8080] PORT=8081 heroku local`
   in the root of this repository! It should recognize the REST host being run
   on port 8080 by default.
4. Now, you can use `wscat` or your favorite tool to connect to `ws://localhost:8081`

## Test it
Many of the tests are highly dependent on the [Django app](/jacky8hyf/CS169CombatingSnake);
so you need to have that app running on a different process.
1. Clone the [Django app](/jacky8hyf/CS169CombatingSnake)
2. In the root of that app, run: `[PORT=8080] heroku local`; you need to specify
   the port manually if it is not 8080 by default. If you don't want it to run on
   port 8080, you need to specify the `REST_HOST` environment variable below.
3. Clone this repository.
4. In the root of this app, run
   `[REST_HOST=http://localhost:8080] python -m unittest discover`.
5. (Temporary) Expect the test `testNoMasterKey` to fail; we bypassed some security
   checks for iteration 2.

Below is the original README for the Python Websockets example. The original repository
is [here](/heroku-examples/python-websockets-chat)

# Python Websockets Example: Chat

This is a simple application that serves tasty WebSockets to your users
with Flask, Flask-Sockets, Gevent, and Gunicorn.

Mmmm.

Check out the [live demo](http://flask-chat.herokuapp.com) or [read the docs](https://devcenter.heroku.com/articles/python-websockets).