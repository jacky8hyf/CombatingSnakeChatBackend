import os
REDIS_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'chat'
DEBUG = 'DEBUG' in os.environ