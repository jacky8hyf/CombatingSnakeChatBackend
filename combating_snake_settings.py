import os
REDIS_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'chat'
DEBUG = 'DEBUG' in os.environ
MASTER_KEY = os.environ['MASTER_KEY']
REST_HOST = os.environ['REST_HOST']