import os
import json
REDIS_URL = os.environ.get('REDISCLOUD_URL')
if not REDIS_URL:
    REDIS_URL = "redis://localhost"
DEBUG = 'DEBUG' in os.environ
MASTER_KEY = os.environ.get('MASTER_KEY')
if not MASTER_KEY:
    MASTER_KEY = "fake_master_key"
REST_HOST = os.environ.get('REST_HOST')
if not REST_HOST:
    REST_HOST = "http://localhost:8080"

BYPASS_AUTHENTICATION = os.environ.get('BYPASS_AUTHENTICATION')
if BYPASS_AUTHENTICATION:
    BYPASS_AUTHENTICATION = json.loads(BYPASS_AUTHENTICATION) # cast it to True, False, 0 or 1
else:
    BYPASS_AUTHENTICATION = True # TODO default to true; set to False to allow authentication of users

BOARD_ROWS = 21
BOARD_COLUMNS = 38
# this is the same constants for models.py in CombatingSnake REST API backend.
MAX_MEMBERS_IN_ROOM = 8
STATUS_PLAYING = 1
STATUS_WAITING = 0
#GAME_TICK_TIME = .5
GAME_TICK_TIME = .2
SNAKE_MAX_LENGTH=10