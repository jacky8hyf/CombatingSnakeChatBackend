# Combating Snake Chat Backend
This Flask application is aimed to provide websocket backend for the CombatingSnake
project.

## Set it up
1. `virtualenv venv`
2. `source venv/bin/activate`
3. `sudo pip install -r requirements.txt`
4. `heroku config -s > .env`

## Run it!
Simply run `heroku local` after you confirm there is the file `.env` in your
directory.

Below is the original README for the Python Websockets example.

# Python Websockets Example: Chat

This is a simple application that serves tasty WebSockets to your users
with Flask, Flask-Sockets, Gevent, and Gunicorn.

Mmmm.

Check out the [live demo](http://flask-chat.herokuapp.com) or [read the docs](https://devcenter.heroku.com/articles/python-websockets).